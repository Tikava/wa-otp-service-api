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


def generate_otp(length: int = 6) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))

async def send_otp(session: AsyncSession, api_key: str, phone_number: str, length: int) -> OTP:
    try:
        stmt = select(Client).where(Client.api_key == api_key)
        result = await session.execute(stmt)
        client = result.scalars().first()

        if not client:
            raise ValueError("Invalid API key provided.")
        
        stmt = select(Business).where(Business.id == client.business_id)
        result = await session.execute(stmt)
        business = result.scalars().first()

        if not business:
            raise ValueError("No business associated with the provided client.")
        
        otp_code = generate_otp(length)
        
        # OTP via WhatsApp
        response = await send_whatsapp_template(
            phone_number, 
            otp_code=otp_code,  
            phone_number_id=business.phone_number_id, 
            whatsapp_api_token=business.whatsapp_api_token
        )
        
        if 'error' in response:
            raise ValueError(f"Failed to send OTP. Error: {response['error']}")

        expires_at = datetime.now() + timedelta(minutes=EXPIRATION_MINUTES)

        user = await get_or_create_user(session, phone_number)
        new_otp = OTP(
            user_id=user.id,
            client_id=client.id,
            otp_code=otp_code,
            expires_at=expires_at,
        )
        session.add(new_otp)
        await session.flush()
        await session.commit()

        return new_otp
    except ValueError as e:
        await session.rollback()
        raise ValueError(f"Error in send_otp: {str(e)}")
    except Exception as e:
        await session.rollback()
        raise ValueError(f"An unexpected error occurred while sending OTP: {str(e)}")



async def verify_otp(session: AsyncSession, phone_number: str, otp_code: str, client: Client):
    try:

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
    except Exception as e:
        raise ValueError(f"An error occurred while verifying OTP: {str(e)}")



async def update_otp_status(session: AsyncSession, otp_code: str, is_used: bool):
    try:
        await session.execute(
            update(OTP).where(OTP.otp_code == otp_code).values(is_used=is_used)
        )
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise ValueError(f"An error occurred while updating OTP status: {str(e)}")