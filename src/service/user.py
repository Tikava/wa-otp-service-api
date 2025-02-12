from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models import User, UserStatus

async def create_user(session: AsyncSession, phone_number: str) -> User:

    user = User(phone_number=phone_number, status=UserStatus.NOT_VERIFIED)
    session.add(user)

    try:
        await session.flush() 
        await session.commit()
        return user
    except IntegrityError:
        await session.rollback()
        raise ValueError("User with this phone number already exists.")

async def get_user_by_phone(session: AsyncSession, phone_number: str) -> User:

    result = await session.execute(select(User).filter(User.phone_number == phone_number))
    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError("User not found.")
    
    return user

async def update_user_status(session: AsyncSession, user_id: int, new_status: UserStatus) -> User:
    result = await session.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError("User not found.")

    user.status = new_status
    user.updated_at = func.now()

    try:
        await session.commit()
        return user
    except IntegrityError:
        await session.rollback()
        raise ValueError("Error updating user status.")
