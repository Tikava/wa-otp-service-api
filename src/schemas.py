from pydantic import BaseModel, EmailStr
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: datetime


class TokenData(BaseModel):
    username: str = None
    
    
