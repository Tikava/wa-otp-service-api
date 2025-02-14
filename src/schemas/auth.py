from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbkBnbWFpbC5jb20iLCJleHAiOjE2MzQwNzQwMzB9.1e3b8z9zX8hL5zgQwGz9z8z9z8z9z8z9z8z9z8z9z8z",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class TokenRequest(BaseModel):
    email: EmailStr
    password: str
    
    