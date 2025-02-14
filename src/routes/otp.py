from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_session
from src.schemas.otp import OTPSendRequest, OTPSendResponse
from src.services.otp import send_otp

router = APIRouter(prefix="/otp", tags=["OTP"])

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
