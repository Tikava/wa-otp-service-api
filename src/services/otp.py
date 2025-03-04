import random
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from src.database.models import OTP, Client, Business, User
from src.services.wa import send_whatsapp_template
from src.services.user import get_or_create_user


EXPIRATION_MINUTES = 5
MAX_OTP_ATTEMPTS = 3

def generate_otp(length: int = 6) -> str:
    """
    Generate a secure OTP with configurable length.
    Ensures no repeated digits for better randomness.
    """
    digits = list(range(10))
    random.shuffle(digits)
    return ''.join(map(str, digits[:length]))

class OTPService:
    @staticmethod
    async def send_otp(
        session: AsyncSession, 
        api_key: str, 
        phone_number: str, 
        length: int = 6
    ) -> OTP:
        """
        Comprehensive OTP sending process with detailed error handling.
        """
        try:
            # Validate input
            if not phone_number or len(phone_number) < 10:
                raise ValueError("Invalid phone number")

            # Validate client and business in a single query for efficiency
            stmt = (
                select(Client)
                .options(selectinload(Client.business))
                .where(Client.api_key == api_key)
            )
            result = await session.execute(stmt)
            client = result.scalar_one_or_none()

            if not client:
                raise ValueError("Invalid API key")
            
            if not client.business:
                raise ValueError("No business associated with client")

            # Generate and send OTP
            otp_code = generate_otp(length)
            
            # Send WhatsApp message
            try:
                await OTPService._send_otp_via_whatsapp(
                    phone_number, 
                    otp_code, 
                    client.business.phone_number_id, 
                    client.business.whatsapp_api_token
                )
            except Exception as wa_error:
                raise ValueError(f"WhatsApp sending error: {wa_error}")

            # Create OTP record
            otp_record = await OTPService._create_otp_record(
                session, 
                phone_number, 
                otp_code, 
                client.id
            )

            return otp_record

        except ValueError as ve:
            raise
        except SQLAlchemyError as se:
            await session.rollback()
            raise ValueError(f"Database error: {se}")
        except Exception as e:
            await session.rollback()
            raise ValueError(f"OTP sending failed: {e}")

    @staticmethod
    async def _create_otp_record(
        session: AsyncSession, 
        phone_number: str, 
        otp_code: str, 
        client_id: int
    ) -> OTP:
        """
        Create OTP record with additional safeguards.
        """
        try:
            # Get or create user with a single query
            user = await get_or_create_user(session, phone_number)
            
            # Check existing non-expired OTPs
            existing_otps_count = await session.scalar(
                select(select(OTP)
                    .where(
                        OTP.user_id == user.id, 
                        OTP.client_id == client_id,
                        OTP.expires_at > datetime.utcnow()
                    )
                    .exists()
                )
            )

            if existing_otps_count >= MAX_OTP_ATTEMPTS:
                raise ValueError(f"Maximum {MAX_OTP_ATTEMPTS} active OTPs exceeded")

            # Create new OTP
            expires_at = datetime.utcnow() + timedelta(minutes=EXPIRATION_MINUTES)
            
            new_otp = OTP(
                user_id=user.id,
                client_id=client_id,
                otp_code=otp_code,
                expires_at=expires_at,
                is_used=False
            )
            
            session.add(new_otp)
            await session.commit()
            await session.refresh(new_otp)
            
            return new_otp

        except IntegrityError:
            await session.rollback()
            raise ValueError("Failed to create OTP record due to database constraint")
        except Exception as e:
            await session.rollback()
            raise ValueError(f"OTP record creation error: {e}")

    @staticmethod
    async def _validate_client(
        session: AsyncSession, 
        api_key: str
    ) -> Client:
        """Validate and retrieve client by API key."""
        stmt = select(Client).where(Client.api_key == api_key)
        result = await session.execute(stmt)
        client = result.scalars().first()
        
        if not client:
            raise ValueError("Invalid API key.")
        return client

    @staticmethod
    async def _validate_business(
        session: AsyncSession, 
        business_id: int
    ) -> Business:
        """Validate and retrieve business by ID."""
        stmt = select(Business).where(Business.id == business_id)
        result = await session.execute(stmt)
        business = result.scalars().first()
        
        if not business:
            raise ValueError("No business associated with the client.")
        return business

    @staticmethod
    async def _send_otp_via_whatsapp(
        phone_number: str, 
        otp_code: str, 
        phone_number_id: str, 
        whatsapp_api_token: str
    ) -> None:
        """Send OTP via WhatsApp and handle potential errors."""
        response = await send_whatsapp_template(
            phone_number,
            otp_code=otp_code,
            phone_number_id=phone_number_id,
            whatsapp_api_token=whatsapp_api_token
        )
        
        if 'error' in response:
            raise ValueError(f"WhatsApp OTP sending failed: {response['error']}")

    @staticmethod
    async def verify_otp(
        session: AsyncSession, 
        phone_number: str, 
        otp_code: str, 
        client: Client
    ) -> Optional[OTP]:

        try:
            stmt = select(OTP).join(User).where(
                User.phone_number == phone_number,
                OTP.otp_code == otp_code,
                OTP.client_id == client.id
            )
            result = await session.execute(stmt)
            otp = result.scalar_one_or_none()
            
            if not otp:
                return None
            
            # Validate OTP
            if otp.expires_at < datetime.utcnow():
                raise ValueError("OTP has expired.")
            
            if otp.is_used:
                raise ValueError("OTP has already been used.")
            
            return otp
        
        except Exception as e:
            raise ValueError(f"OTP verification failed: {str(e)}")

    @staticmethod
    async def update_otp_status(
        session: AsyncSession, 
        otp_code: str, 
        is_used: bool
    ) -> None:
        """Update OTP usage status."""
        try:
            await session.execute(
                update(OTP).where(OTP.otp_code == otp_code).values(is_used=is_used)
            )
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise ValueError(f"OTP status update failed: {str(e)}")