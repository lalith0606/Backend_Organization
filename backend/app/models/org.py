from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Annotated, Any
from datetime import datetime

PyObjectId = Annotated[str, BeforeValidator(str)]

class OrgConnection(BaseModel):
    db_name: str
    collection_name: str
    extra: dict = {}

class OrganizationInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    organization_name: str
    collection_name: str
    connection: OrgConnection
    admin_user_id: Optional[PyObjectId]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
