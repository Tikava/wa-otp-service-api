from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.database.models import UserStatus
from src.schemas.otp import *
from src.services.otp import *
from src.exceptions.otp import *

router = APIRouter(prefix="/api/v1/otp", tags=["OTP"])

@router.post("/send", response_model=OTPSendResponse, status_code=201)
async def send_otp_handler(
    request: OTPSendRequest,
    x_api_key: str = Header(...),
    session: AsyncSession = Depends(get_session)
):
    try:
        otp_record = await OTPService.send_otp(
            session, 
            x_api_key, 
            request.phone_number, 
            request.length
        )
        return OTPSendResponse(
            message="OTP sent successfully",
            otp_id=otp_record.id,
            expires_at=otp_record.expires_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify", tags=["OTP"], response_model=OTPVerifyResponse)
async def verify_otp_handler(
    request: OTPVerifyRequest,
    x_api_key: str = Header(...),
    session: AsyncSession = Depends(get_session)
):
    try:
        # Validate client with specific error handling
        try:
            client = await OTPService._validate_client(session, x_api_key)
        except Exception as e:
            raise ClientValidationError("Invalid client or API key") from e
            
        # Verify OTP with detailed error tracking
        try:
            otp = await OTPService.verify_otp(
                session,
                request.phone_number,
                request.otp_code,
                client
            )
        except OTPExpiredError as e:
            raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")
        except OTPAlreadyUsedError as e:
            raise HTTPException(status_code=400, detail="OTP has already been used.")
        except InvalidOTPError as e:
            raise HTTPException(status_code=400, detail="Invalid OTP or phone number.")
            
        # Update statuses - avoid nested transaction with async with
        await OTPService.update_otp_status(session, otp.otp_code, True)
        await session.execute(
            update(User)
            .where(User.id == otp.user_id)
            .values(status=UserStatus.VERIFIED)
        )
        
        # Commit changes
        await session.commit()
        
        return OTPVerifyResponse(message="OTP verified successfully")
        
    except ClientValidationError as e:
        await session.rollback()
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        # Re-raise HTTPException as-is
        raise
    except Exception as e:
        await session.rollback()
        # Log the original exception for debugging
        raise HTTPException(status_code=500, detail={
            "error": str(e), 
            "message": "An unexpected error occurred during OTP verification."
        })