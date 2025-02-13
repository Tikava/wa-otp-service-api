from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy import select
from typing import Optional
from src.database.models import Admin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def add_admin(session: AsyncSession, email: str, password: str) -> Admin:
    """
    Creates a new admin with a hashed password.

    :param session: AsyncSession - SQLAlchemy session.
    :param email: str - Email of the admin.
    :param password: str - Plaintext password (hashed before storing).
    :return: Admin - The created admin instance.
    :raises ValueError: If the email is already registered.
    """
    hashed_password = pwd_context.hash(password)
    admin = Admin(email=email, password=hashed_password)
    session.add(admin)

    try:
        await session.flush()
        await session.refresh(admin)
        await session.commit()
        return admin
    except IntegrityError as e:
        await session.rollback()

        if "unique constraint" in str(e.orig).lower():
            raise ValueError(f"Admin with email '{email}' already exists.")
        raise ValueError("Database error: Unable to create admin.")

async def get_admin(session: AsyncSession, email: str) -> Optional[Admin]:
    """
    Fetches an admin by email.

    :param session: AsyncSession - SQLAlchemy session.
    :param email: str - Email to search.
    :return: Optional[Admin] - The admin if found, otherwise None.
    """
    stmt = select(Admin).where(Admin.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
