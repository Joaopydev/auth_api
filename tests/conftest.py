from datetime import date
import pytest

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.db.models.base import Base
from src.services.hashed.hashed_service import HashedPasswordService
from src.controllers.signin import SigninController

from src.repository.user_repository import UserRepository
from src.repository.meal_repository import MealRepository
from src.db.models.users import GoalType, GenderType


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
    yield async_session


@pytest.fixture
async def test_user(test_session_db):
    password_hash = HashedPasswordService.hash_password("password")
    user_repository = UserRepository(test_session_db)
    user = await user_repository.insert_user(
        name="Teste",
        email="test@gmail.com",
        password=password_hash,
        goal=GoalType.gain,
        gender=GenderType.male,
        birth_date=date(2001, 3, 15),
        height=165,
        weight=90,
        activity_level=3,
        calories=0,
        proteins=0,
        carbohydrates=0,
        fats=0
    )
    return user

@pytest.fixture
async def test_login_user(test_session_db, test_user):
    controller = SigninController(
        user_repository=UserRepository(test_session_db),
        hashed_service=HashedPasswordService()
    )
    response = await controller.handle(
        body={
            "email": "test@gmail.com",
            "password": "password"
        }
    )

    return response["body"]["accessToken"]

@pytest.fixture
async def test_meal(test_session_db, test_user):
    meal_repository = MealRepository(test_session_db)
    meal = await meal_repository.create_meal(
        user_id=test_user.id,
        input_file_key="audio.mp4",
        file_type="audio/m4a"
    )
    return meal