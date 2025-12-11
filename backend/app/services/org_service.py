from fastapi import HTTPException, status
from app.db.master_repo import master_repo
from app.db.client import get_tenant_collection_name, get_master_db
from app.schemas.org_schema import OrgCreateRequest, OrgResponse, OrgConnectionResponse
from app.core.security import get_password_hash
from app.core.config import settings
from datetime import datetime
from bson import ObjectId

class OrgService:
    @staticmethod
    async def create_organization(request: OrgCreateRequest) -> OrgResponse:
        print(f"DEBUG: Starting create_organization for {request.organization_name}")
        # 1. Validate Uniqueness
        existing = await master_repo.get_org_by_name(request.organization_name)
        if existing:
            raise HTTPException(status_code=409, detail="Organization already exists")

        # 2. Prepare Data
        collection_name = await get_tenant_collection_name(request.organization_name)
        
        # 3. Create Tenant Collection
        db = await get_master_db()
        try:
            await db.create_collection(collection_name)
            print(f"DEBUG: Created collection {collection_name}")
        except Exception as e:
            print(f"DEBUG: Collection creation skipped or failed: {e}")
        
        # 4. Create Org Metadata
        org_doc = {
            "organization_name": request.organization_name,
            "collection_name": collection_name,
            "connection": {
                "db_name": settings.MASTER_DB_NAME,
                "collection_name": collection_name,
                "extra": {}
            },
            "admin_user_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        org_id = await master_repo.create_org(org_doc)
        print(f"DEBUG: Created org with ID {org_id}")

        # 5. Create Admin
        try:
            admin_doc = {
                "organization_id": ObjectId(org_id),
                "email": request.email,
                "password_hash": get_password_hash(request.password),
                "role": "admin",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            admin_id = await master_repo.create_admin(admin_doc)
            print(f"DEBUG: Created admin with ID {admin_id}")
        except Exception as e:
            print(f"DEBUG: Failed to create admin: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create admin: {str(e)}")

        # 6. Link Admin to Org
        try:
            await master_repo.update_org_admin_id(org_id, admin_id)
            print("DEBUG: Linked admin to org")
        except Exception as e:
            print(f"DEBUG: Failed to link admin: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to link admin: {str(e)}")

        return OrgResponse(
            id=org_id,
            organization_name=request.organization_name,
            collection_name=org_doc["collection_name"],
            admin_user_id=admin_id,
            created_at=org_doc["created_at"],
            connection=OrgConnectionResponse(**org_doc["connection"])
        )

    @staticmethod
    async def get_organization(organization_name: str) -> OrgResponse:
        org = await master_repo.get_org_by_name(organization_name)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return OrgResponse(
            id=str(org["_id"]),
            organization_name=org["organization_name"],
            collection_name=org["collection_name"],
            admin_user_id=str(org["admin_user_id"]),
            created_at=org["created_at"],
            connection=OrgConnectionResponse(**org["connection"])
        )

    @staticmethod
    async def delete_organization(organization_name: str, current_admin_org_id: str):
        org = await master_repo.get_org_by_name(organization_name)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Authorization Check: Admin calling must belong to this org
        if str(org["_id"]) != current_admin_org_id:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this organization")

        # Delete Tenant Collection
        db = await get_master_db()
        await db.drop_collection(org["collection_name"])

        # Delete Admins
        await master_repo.delete_admins_by_org_id(str(org["_id"]))

        # Delete Org Metadata
        await master_repo.delete_org(str(org["_id"]))

        return {"ok": True, "message": "Organization and related data deleted."}
