from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from src.database.models import Admin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def add_admin(session: AsyncSession, email: str, password: str) -> Admin:
    hashed_password = pwd_context.hash(password)
    admin = Admin(email=email, password=hashed_password)
    session.add(admin)

    try:
        await session.flush() 
        await session.commit()
        return admin
    except IntegrityError:
        await session.rollback()
        raise ValueError("Admin creation failed. Email may already be in use.")