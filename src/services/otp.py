from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from src.database.models import OTP

async def create_otp(session: AsyncSession, user_id: int, business_id: int, otp_code: str, expiration_minutes: int = 5) -> OTP:
    expires_at = datetime.time() + timedelta(minutes=expiration_minutes)
    
    otp = OTP(
        user_id=user_id,
        business_id=business_id,
        otp_code=otp_code,
        expires_at=expires_at
    )

    session.add(otp)

    try:
        await session.flush()
        await session.commit()
        return otp
    except IntegrityError:
        await session.rollback()
        raise ValueError("Error creating OTP.")


async def get_otp_by_code(session: AsyncSession, otp_code: str) -> OTP:
    result = await session.execute(select(OTP).filter(OTP.otp_code == otp_code))
    otp = result.scalar_one_or_none()

    if otp is None:
        raise ValueError("OTP not found.")
    
    return otp


async def verify_otp(session: AsyncSession, otp_code: str, user_id: int, business_id: int) -> OTP:
    otp = await get_otp_by_code(session, otp_code)
    
    if otp.is_used:
        raise ValueError("OTP has already been used.")
    
    if otp.user_id != user_id or otp.business_id != business_id:
        raise ValueError("OTP does not belong to this user or business.")
    
    if otp.expires_at < datetime.time():
        raise ValueError("OTP has expired.")
    
    otp.is_used = True
    try:
        await session.commit()  
        return otp
    except IntegrityError:
        await session.rollback() 
        raise ValueError("Error verifying OTP.")


async def expire_otp(session: AsyncSession, otp_code: str) -> OTP:
    otp = await get_otp_by_code(session, otp_code)
    
    otp.expires_at = datetime.time()  

    try:
        await session.commit() 
        return otp
    except IntegrityError:
        await session.rollback() 
        raise ValueError("Error expiring OTP.")


async def get_otps_by_user(session: AsyncSession, user_id: int) -> list[OTP]:
    result = await session.execute(select(OTP).filter(OTP.user_id == user_id))
    otps = result.scalars().all()
    return otps


async def get_otps_by_business(session: AsyncSession, business_id: int) -> list[OTP]:
    result = await session.execute(select(OTP).filter(OTP.business_id == business_id))
    otps = result.scalars().all()
    return otps
