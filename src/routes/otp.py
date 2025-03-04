from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_session
from src.database.models import UserStatus
from src.schemas.otp import *
from src.services.otp import *
from src.services.client import get_client_by_api_key
from src.services.user import update_user_status

router = APIRouter(prefix="/api/v1/otp", tags=["OTP"])

@router.post("/send", response_model=OTPSendResponse, status_code=201)
async def send_otp_handler(
    request: OTPSendRequest,
    x_api_key: str = Header(...),
    session: AsyncSession = Depends(get_session)
):
    
    try:
        otp_record = await send_otp(session, x_api_key, request.phone_number, request.length)
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
    client = await get_client_by_api_key(session, x_api_key)
    if not client:
        raise HTTPException(status_code=403, detail="Invalid API key.")
    
    otp = await verify_otp(session, request.phone_number, request.otp_code, client)
    if not otp:
        raise HTTPException(status_code=400, detail="Invalid OTP or phone number.")
    
    try:
        await update_otp_status(session, otp.otp_code, True)
        await update_user_status(session, otp.user_id, UserStatus.VERIFIED)
        await session.commit()
        return OTPVerifyResponse(message="OTP verified successfully.")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error verifying OTP: {str(e)}")
