from pydantic import BaseModel, EmailStr
from datetime import datetime

class AdminCreateRequest(BaseModel):
    email: EmailStr
    password: str
    
class AdminCreateResponse(BaseModel):
    email: EmailStr
    created_at: datetime
    
    class Config:
        from_attributes = True