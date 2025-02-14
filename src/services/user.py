from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models import User, UserStatus

async def get_or_create_user(session: AsyncSession, phone_number: str) -> User:

    stmt = select(User).where(User.phone_number == phone_number)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        return user

    new_user = User(phone_number=phone_number, status=UserStatus.NOT_VERIFIED)
    session.add(new_user)
    
    try:
        await session.flush()
        return new_user
    except IntegrityError:
        await session.rollback()
        raise ValueError("User creation failed due to a unique constraint violation.")

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
