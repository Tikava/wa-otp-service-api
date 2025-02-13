from pydantic import BaseModel, Field
from datetime import datetime

class BusinessCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    whatsapp_token: str = Field(..., min_length=10)
    phone_number_id: str = Field(..., min_length=5)

class BusinessCreateResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
