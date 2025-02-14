import secrets

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.database.models import Client, Business


def generate_api_key() -> str:
    return secrets.token_hex(32)


async def create_client_to_business(session: AsyncSession, business_id: int, name: str, scopes: str) -> Client:
    # Check if the business exists
    stmt = select(Business).where(Business.id == business_id)
    result = await session.execute(stmt)
    business = result.scalar_one_or_none()

    if not business:
        raise ValueError("Business not found. Ensure the business ID is correct.")

    # Generate API key
    api_key = generate_api_key()
    new_client = Client(business_id=business_id, name=name, scopes=scopes, api_key=api_key)
    session.add(new_client)

    try:
        await session.commit()
        await session.refresh(new_client)
        return new_client

    except IntegrityError as e:
        await session.rollback()
        
        error_message = str(e.orig).lower()
        if "unique constraint" in error_message and "clients.api_key" in error_message:
            raise ValueError("Client creation failed. The generated API key already exists. Please try again.")
        elif "foreign key constraint" in error_message:
            raise ValueError("Client creation failed. The associated business does not exist.")
        
        raise ValueError("Client creation failed due to a database constraint violation.")


async def get_client_by_api_key(session: AsyncSession, api_key: str) -> Client:
    result = await session.execute(select(Client).filter(Client.api_key == api_key))
    client = result.scalar_one_or_none()

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
