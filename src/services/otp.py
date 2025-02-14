import random

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from src.database.models import OTP, Client, Business
from src.services.wa import send_whatsapp_template
from src.services.user import get_or_create_user


EXPIRATION_MINUTES = 5


async def generate_otp(length: int = 6) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))

async def create_otp(session: AsyncSession, phone_number: str, client_id: int, length: int, expiration_minutes: int = EXPIRATION_MINUTES) -> OTP:
    user = await get_or_create_user(session, phone_number)
    
    
    otp_code = await generate_otp(length)
    expires_at = datetime.time() + timedelta(minutes=expiration_minutes)
    
    new_otp = OTP(
        user_id=user.id,
        client_id=client_id,
        otp_code=otp_code,
        expires_at=expires_at,
    )

    session.add(new_otp)

    try:
        await session.flush()
        await session.commit()
        return new_otp
    except IntegrityError:
        await session.rollback()
        raise ValueError("OTP generation failed due to a unique constraint violation.")
        
    
async def send_otp(session: AsyncSession, api_key: str, phone_number: str, length: int) -> OTP:


    stmt = select(Client).where(Client.api_key == api_key)
    result = await session.execute(stmt)
    client = result.scalar_one_or_none()

    if not client:
        raise ValueError("Invalid API key.")
    
    stmt = select(Business).where(Business.id == client.business_id)
    result = await session.execute(stmt)
    business = result.scalar_one_or_none()
    
    if not business:
        raise ValueError("Business associated with this client not found.")

    try:
        
        otp_record = await create_otp(session, phone_number, client.id, length)

        success = await send_whatsapp_template(
            phone_number, 
            otp_record.otp_code, 
            business.phone_number_id, 
            business.whatsapp_api_token
        )
        
        if not success:
            await session.rollback()
            raise ValueError("Failed to send OTP. Please try again.")
        
        await session.commit()
        return otp_record
    except IntegrityError:
        await session.rollback()
        raise ValueError("OTP generation failed due to a database error.")



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
