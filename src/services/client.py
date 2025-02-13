from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.database.models import Client

async def create_client(session: AsyncSession, business_id: int, scopes: str, api_key: str) -> Client:
    client = Client(business_id=business_id, scopes=scopes, api_key=api_key)
    session.add(client)

    try:
        await session.flush()
        await session.commit()
        return client
    except IntegrityError:
        await session.rollback()
        raise ValueError("Client with this API key already exists.")


async def get_client_by_api_key(session: AsyncSession, api_key: str) -> Client:
    result = await session.execute(select(Client).filter(Client.api_key == api_key))
    client = result.scalar_one_or_none()

    if client is None:
        raise ValueError("Client not found.")
    
    return client


async def get_client_by_business_id(session: AsyncSession, business_id: int) -> Client:
    result = await session.execute(
        select(Client)
        .filter(Client.business_id == business_id)
        .options(joinedload(Client.business))
    )
    client = result.scalar_one_or_none()

    if client is None:
        raise ValueError("Client not found for the provided business.")
    
    return client


async def update_client(session: AsyncSession, client_id: int, scopes: str, api_key: str) -> Client:
    result = await session.execute(select(Client).filter(Client.id == client_id))
    client = result.scalar_one_or_none()

    if client is None:
        raise ValueError("Client not found.")

    client.scopes = scopes
    client.api_key = api_key

    try:
        await session.commit()
        return client
    except IntegrityError:
        await session.rollback()
        raise ValueError("Error updating client.")


async def delete_client(session: AsyncSession, client_id: int) -> bool:
    result = await session.execute(select(Client).filter(Client.id == client_id))
    client = result.scalar_one_or_none()

    if client is None:
        raise ValueError("Client not found.")

    await session.delete(client)
    await session.commit()
    return True
