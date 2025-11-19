import pytest
import bcrypt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.db.models.base import Base
from src.db.models.users import User


@pytest.fixture
async def test_engine():
    engine = create_async_engine(
        url="sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
  
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session_db(test_engine):
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


@pytest.fixture
async def test_user(test_session_db):
    password_hash = bcrypt.hashpw(
        password="password".encode("utf-8"),
        salt=bcrypt.gensalt(8),
    )

    user = User(
        name="Teste",
        email="joao@gmail.com",
        password=password_hash,
    )

    test_session_db.add(user)
    await test_session_db.commit()
    await test_session_db.refresh(user)

    return user