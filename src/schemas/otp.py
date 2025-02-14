from pydantic import BaseModel, Field
from datetime import datetime

class OTPSendRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15, regex=r"^\+?\d+$")
    length: int = Field(6, ge=4, le=10)
    
    class Config:
        schema_extra = {
            "example": {
                "phone_number": "+1234567890",
                "length": 6
            }
        }

class OTPSendResponse(BaseModel):
    message: str
    otp_id: int
    expires_at: datetime
