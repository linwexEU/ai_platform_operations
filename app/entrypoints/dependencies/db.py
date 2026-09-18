from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.base import session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]: 
    async with session_factory() as session: 
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
