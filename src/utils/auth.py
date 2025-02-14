from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_session
from src.database.models import Admin
from src.config import settings
from src.services.admin import get_admin

from datetime import datetime, timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

async def create_jwt_token(admin: Admin) -> str:
    expiration = datetime.now() + timedelta(seconds=settings.access_token_expire_minutes * 60)
    payload = {
        "sub": admin.email,
        "exp": expiration
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

async def get_current_admin(
    token: str = Security(oauth2_scheme), session: AsyncSession = Depends(get_session)
):

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        admin = await get_admin(session, email)
        if admin is None:
            raise HTTPException(status_code=401, detail="Admin not found")
        return admin
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
