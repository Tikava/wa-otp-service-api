import random

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from src.database.models import OTP, Client, Business, User
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

async def verify_otp(session: AsyncSession, phone_number: str, otp_code: str, client: Client):
    stmt = select(OTP).join(User).where(
        User.phone_number == phone_number,
        OTP.otp_code == otp_code,
        OTP.client_id == client.id
    )
    result = await session.execute(stmt)
    otp = result.scalar_one_or_none()

    if not otp:
        raise ValueError("Invalid OTP or phone number.")

    if otp.expires_at < datetime.now():
        raise ValueError("OTP has expired.")

    if otp.is_used:
        raise ValueError("OTP has already been used.")

    return otp

async def update_otp_status(session: AsyncSession, otp_code: str, is_used: bool):
    await session.execute(
        update(OTP).where(OTP.otp_code == otp_code).values(is_used=is_used)
    )