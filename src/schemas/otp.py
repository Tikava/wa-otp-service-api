from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class OTPSendRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15, pattern=r"^\+?\d+$")
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
    
    class Config:
        schema_extra = {
            "example": {
                "message": "OTP sent successfully",
                "otp_id": 1,
                "expires_at": "2022-01-01T00:00:00"
            }
        }
        
class OTPVerifyRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15, pattern=r"^\+?\d+$")
    otp_code: str = Field(..., min_length=4, max_length=10)
    
    class Config:
        schema_extra = {
            "example": {
                "phone_number": "+1234567890",
                "otp_code": "1234"
            }
        }
        
class OTPVerifyResponse(BaseModel):
    message: Literal["OTP verified successfully"]
