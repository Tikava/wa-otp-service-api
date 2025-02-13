from fastapi import APIRouter, HTTPException, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.database.models import Admin
from src.services.admin import add_admin
from src.services.business import add_business
from src.schemas.admin import AdminCreateRequest, AdminCreateResponse
from src.schemas.business import BusinessCreateRequest, BusinessCreateResponse
from src.config import settings
from src.utils.auth import get_current_admin

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

@router.post("/register", response_model=AdminCreateResponse, status_code=201)
async def register_admin(
    admin: AdminCreateRequest, 
    x_admin_secret: str = Header(...),
    session: AsyncSession = Depends(get_session)
):
    if x_admin_secret != settings.super_admin_secret:
        raise HTTPException(status_code=403, detail="Invalid admin secret")
    
    try:
        new_admin: Admin = await add_admin(session, admin.email, admin.password)
        return AdminCreateResponse(email=new_admin.email, created_at=new_admin.created_at)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    
@router.post("/business", response_model=BusinessCreateResponse, status_code=201)
async def create_business(
    business: BusinessCreateRequest,
    session: AsyncSession = Depends(get_session),
    admin = Depends(get_current_admin)
):
    try:
        new_business = await add_business(
            session, business.name, business.whatsapp_token, business.phone_number_id, admin.id
        )
        return BusinessCreateResponse(id=new_business.id, name=new_business.name, created_at=new_business.created_at)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))