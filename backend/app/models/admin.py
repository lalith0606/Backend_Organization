from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from typing import Optional, Annotated
from datetime import datetime

# Helper for ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class AdminBase(BaseModel):
    organization_id: PyObjectId
    email: EmailStr
    role: str = "admin"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AdminInDB(AdminBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    password_hash: str
