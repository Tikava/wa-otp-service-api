from typing import Optional

from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Business

async def add_business(
    session: AsyncSession, admin_id: int, name: str, whatsapp_api_token: str, whatsapp_phone_number_id: int
) -> Business:
    business = Business(
        admin_id=admin_id, 
        name=name, 
        whatsapp_api_token=whatsapp_api_token, 
        whatsapp_phone_number_id=whatsapp_phone_number_id
    )
    session.add(business)
    
    try:
        await session.flush()
        await session.commit()
        return business
    except IntegrityError:
        await session.rollback()
        raise ValueError("Business creation failed due to integrity error.")
    
async def get_business(session: AsyncSession, business_id: int) -> Optional[Business]:
    result = await session.get(Business, business_id)
    return result


async def get_all_businesses(session: AsyncSession) -> list[Business]:
    result = await session.execute(select(Business))
    return result.scalars().all()
