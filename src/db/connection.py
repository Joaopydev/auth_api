import os
import ssl

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

DATA_BASE_URL = os.getenv("DATA_BASE_URL").split("?")[0]

def get_async_engine() -> AsyncEngine:
    # Crie uma engine separada para cada loop de uma requisição para evitar estouro entre loops do asyncio
    return create_async_engine(
            url=DATA_BASE_URL,
            echo=True,
            future=True,
            connect_args={"ssl": ssl_context}, #async entende esse formato de ssl
        )

# Async context manager para o DB
@asynccontextmanager
async def get_db():
    async_engine = get_async_engine()
    # Fábrica de sessões assíncronas
    async_session = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    session = async_session()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
        await async_engine.dispose()