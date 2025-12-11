from fastapi import APIRouter
from app.schemas.auth_schema import AdminLoginRequest, Token
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/admin/login", response_model=Token)
async def login(login_request: AdminLoginRequest):
    return await AuthService.authenticate_admin(login_request)
