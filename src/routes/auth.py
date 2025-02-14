from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from src.database import get_session
from src.services.admin import get_admin
from src.schemas.auth import *
from src.config import settings
from src.utils.auth import create_jwt_token

router = APIRouter(prefix="/api/v1")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/token")
async def login_for_access_token(form_data: TokenRequest, session: AsyncSession = Depends(get_session)):
    admin = await get_admin(session, form_data.email)
    
    if admin is None or not pwd_context.verify(form_data.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = await create_jwt_token(admin)
    expires_in = settings.access_token_expire_minutes * 60

    return TokenResponse(access_token=access_token, token_type="bearer", expires_in=expires_in)
