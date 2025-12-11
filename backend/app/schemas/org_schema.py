from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Any
from datetime import datetime
import re

class OrgCreateRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str = Field(min_length=8)

    @validator("organization_name")
    def validate_org_name(cls, v):
        if not re.match(r"^[a-zA-Z0-9\-]+$", v):
            raise ValueError("Organization name must contain only letters, numbers, and hyphens.")
        return v.lower()

class OrgConnectionResponse(BaseModel):
    db_name: str
    collection_name: str
    extra: dict = {}

class OrgResponse(BaseModel):
    id: str
    organization_name: str
    collection_name: str
    admin_user_id: str
    connection: Optional[OrgConnectionResponse] = None
    created_at: datetime

class OrgUpdateRequest(BaseModel):
    organization_name: str
    new_organization_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class OrgDeleteRequest(BaseModel):
    organization_name: str
