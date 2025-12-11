from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    admin: dict

class TokenData(BaseModel):
    sub: str | None = None
    email: str | None = None
    org_id: str | None = None
    role: str | None = None

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str
