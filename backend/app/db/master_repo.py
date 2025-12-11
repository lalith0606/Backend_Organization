from app.db.client import get_master_db
from app.models.admin import AdminInDB
from app.core.security import verify_password
from bson import ObjectId
from datetime import datetime


class MasterRepository:
    @staticmethod
    async def get_admin_by_email(email: str):
        db = await get_master_db()
        return await db.admins.find_one({"email": email})

    @staticmethod
    async def get_org_by_id(org_id: str):
        db = await get_master_db()
        return await db.organizations.find_one({"_id": ObjectId(org_id)})
    
    @staticmethod
    async def get_org_by_name(name: str):
        db = await get_master_db()
        return await db.organizations.find_one({"organization_name": name})

    @staticmethod
    async def create_org(org_data: dict) -> str:
        db = await get_master_db()
        result = await db.organizations.insert_one(org_data)
        return str(result.inserted_id)

    @staticmethod
    async def create_admin(admin_data: dict) -> str:
        db = await get_master_db()
        result = await db.admins.insert_one(admin_data)
        return str(result.inserted_id)

    @staticmethod
    async def update_org_admin_id(org_id: str, admin_id: str):
        db = await get_master_db()
        print(f"DEBUG: Updating org {org_id} with admin {admin_id}")
        result = await db.organizations.update_one(
            {"_id": ObjectId(org_id)},
            {"$set": {"admin_user_id": ObjectId(admin_id)}}
        )
        print(f"DEBUG: Matched: {result.matched_count}, Modified: {result.modified_count}")
        if result.matched_count == 0:
            print(f"DEBUG: WARNING - No organization matched for update!")

    @staticmethod
    async def delete_org(org_id: str):
        db = await get_master_db()
        await db.organizations.delete_one({"_id": ObjectId(org_id)})

    @staticmethod
    async def delete_admin(admin_id: str):
        db = await get_master_db()
        await db.admins.delete_one({"_id": ObjectId(admin_id)})
    
    @staticmethod
    async def delete_admins_by_org_id(org_id: str):
        db = await get_master_db()
        await db.admins.delete_many({"organization_id": ObjectId(org_id)})

    @staticmethod
    async def update_org_metadata(org_id: str, update_data: dict):
        db = await get_master_db()
        await db.organizations.update_one(
            {"_id": ObjectId(org_id)},
            {"$set": update_data}
        )
    
    @staticmethod
    async def update_admin_credentials(admin_id: str, email: str = None, password_hash: str = None):
        db = await get_master_db()
        update_fields = {"updated_at": datetime.utcnow()}
        if email:
            update_fields["email"] = email
        if password_hash:
            update_fields["password_hash"] = password_hash
            
        await db.admins.update_one(
            {"_id": ObjectId(admin_id)},
            {"$set": update_fields}
        )

master_repo = MasterRepository()
