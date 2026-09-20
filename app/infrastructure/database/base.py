from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.domain.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL, 
    pool_size=10, 
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True
)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
