from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_session
from src.schemas.client import ClientCreateRequest, ClientCreateResponse
from src.services.client import create_client_to_business


router = APIRouter(prefix="/api/v1/business", tags=["business"])

@router.post("/{id}/clients", response_model=ClientCreateResponse, status_code=201)
async def create_client(
    id: int,
    client: ClientCreateRequest,
    session: AsyncSession = Depends(get_session)
):
    try:
        new_client = await create_client_to_business(session, id, client.name, client.scopes)
        return ClientCreateResponse(
            id=new_client.id,
            name=new_client.name,
            business_id=new_client.business_id,
            scopes=new_client.scopes,
            api_key=new_client.api_key,
            created_at=new_client.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
