from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from elimina import config

engine = create_async_engine(config.DB_URI, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
