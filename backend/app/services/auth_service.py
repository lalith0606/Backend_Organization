from fastapi import HTTPException, status
from app.db.master_repo import MasterRepository
from app.core.security import verify_password, create_access_token
from app.schemas.auth_schema import AdminLoginRequest, Token
from app.core.config import settings

class AuthService:
    @staticmethod
    async def authenticate_admin(login_data: AdminLoginRequest) -> Token:
        admin_data = await MasterRepository.get_admin_by_email(login_data.email)
        if not admin_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        if not verify_password(login_data.password, admin_data["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        # Create JWT
        token_payload = {
            "sub": str(admin_data["_id"]),
            "email": admin_data["email"],
            "org_id": str(admin_data["organization_id"]),
            "role": admin_data["role"]
        }
        
        access_token = create_access_token(data=token_payload)
        
        return Token(
            access_token=access_token,
            expires_in=settings.JWT_EXPIRES_MINUTES * 60,
            admin={
                "id": str(admin_data["_id"]),
                "email": admin_data["email"],
                "organization_id": str(admin_data["organization_id"])
            }
        )
