from typing import Annotated

from fastapi import FastAPI, APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext

from .config import settings


SECRET_KEY = ''
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(version="0.0.1", title="Verify Code API")
router = APIRouter(
    prefix="/api/v1",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str
    

class TokenData(BaseModel):
    username: str = None
    
    
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


@router.post("/send-otp", tags=["send_code"])
async def send_code(token: Annotated[str, Depends(oauth2_scheme)]):
    return settings

@router.post("/verify-otp", tags=["verify_code"])
async def verify_code():
    return {"message": "Verify code"}


@router.post("/admin/register", tags=["admin"])
async def register_admin():
    pass



app.include_router(router)