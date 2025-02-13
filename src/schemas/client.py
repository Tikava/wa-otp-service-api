from pydantic import BaseModel
from datetime import datetime

class ClientCreateRequest(BaseModel):
    name: str
    scopes: str 

class ClientCreateResponse(BaseModel):
    id: int
    name: str
    business_id: int
    scopes: str
    api_key: str
    created_at: datetime

    class Config:
        from_attributes = True
