from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from app.schemas.org_schema import OrgCreateRequest, OrgResponse, OrgDeleteRequest, OrgUpdateRequest
from app.schemas.auth_schema import TokenData
from app.services.org_service import OrgService
from app.services.migration_service import MigrationService
from app.core.security import decode_access_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/org", tags=["Organizations"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

async def get_current_admin(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenData(**payload)

@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_org(request: OrgCreateRequest):
    org_response = await OrgService.create_organization(request)
    return {"ok": True, "organization": org_response}

@router.get("/get", response_model=dict)
async def get_org(organization_name: str):
    org_response = await OrgService.get_organization(organization_name)
    return {"ok": True, "organization": org_response}

@router.put("/update", response_model=dict)
async def update_org(
    body: OrgUpdateRequest,
    current_admin: Annotated[TokenData, Depends(get_current_admin)]
):
    # 1. Authorize: Admin must own the org he is trying to update
    # The body.organization_name refers to the CURRENT name
    target_org = await OrgService.get_organization(body.organization_name)
    if not target_org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    if target_org.id != current_admin.org_id:
        raise HTTPException(status_code=403, detail="Unauthorized to update this organization")

    # 2. Rename Logic
    if body.new_organization_name and body.new_organization_name != body.organization_name:
        # Check uniqueness of new name
        try:
            existing = await OrgService.get_organization(body.new_organization_name)
            if existing:
                raise HTTPException(status_code=409, detail="New organization name already exists")
        except HTTPException as e:
            if e.status_code != 404: raise e
        
        # Initiate Migration
        await MigrationService.perform_migration(
            body.organization_name, 
            body.new_organization_name, 
            target_org.id
        )

    # 3. Admin Credentials Update (Email/Pass)
    if body.email or body.password:
        # We need to update the admin user.
        # The admin user ID is in target_org.admin_user_id (str)
        # But wait, OrgResponse returns admin_user_id.
        
        # Update logic in auth/master repo
        # Using a helper in OrgService or direct repo call?
        # Let's keep it clean and use OrgService or MasterRepo.
        # But we need to hash password if present.
        from app.core.security import get_password_hash
        from app.db.master_repo import master_repo
        
        pwd_hash = get_password_hash(body.password) if body.password else None
        await master_repo.update_admin_credentials(
            target_org.admin_user_id,
            email=body.email,
            password_hash=pwd_hash
        )

    # 4. Return Updated Org
    # Fetch fresh
    final_name = body.new_organization_name if body.new_organization_name else body.organization_name
    updated_org = await OrgService.get_organization(final_name)
    
    return {"ok": True, "message": "Organization updated", "organization": updated_org}


@router.delete("/delete", response_model=dict)
async def delete_org(
    body: OrgDeleteRequest,
    current_admin: Annotated[TokenData, Depends(get_current_admin)]
):
    result = await OrgService.delete_organization(body.organization_name, current_admin.org_id)
    return result
