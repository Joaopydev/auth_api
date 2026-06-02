import pytest

from src.controllers.signup import SignupController
from src.repository.user_repository import UserRepository
from src.services.hashed.hashed_service import HashedPasswordService


@pytest.mark.asyncio
async def test_signup_controller_invalid_data_entry(test_session_db):
    request_body = {
        "goal": "lose",
        "gender": "male",
        "birthDate": "1990-01-01",
        "height": 180,
        "weight": 75,
        "activityLevel": 3,
        "account": {
            "name": 000000,
            "email": "invalid-email",
            "password": 000000,
        }
    }

    controller = SignupController(
        user_repository=UserRepository(test_session_db),
        hashed_service=HashedPasswordService()
    )

    response = await controller.handle(body=request_body)
    assert response["statusCode"] == 400
    assert response["body"]["errors"][0]["type"] == "string_type"
    assert response["body"]["errors"][1]["type"] == "value_error"

@pytest.mark.asyncio
async def test_signup_controller_created(test_session_db):
    request_body = {
        "goal": "gain",
        "gender": "female",
        "birthDate": "1995-06-15",
        "height": 165,
        "weight": 60,
        "activityLevel": 2,
        "account": {
            "name": "Test",
            "email": "test@gmail.com",
            "password": "password",
        }
    }

    controller = SignupController(
        user_repository=UserRepository(db_session=test_session_db),
        hashed_service=HashedPasswordService()
    )
    response = await controller.handle(body=request_body)

    assert response.get("statusCode", 400) == 201
    assert "accessToken" in response.get("body", {})


@pytest.mark.asyncio
async def test_signup_controller_conflict(test_session_db, test_user):
    request_body = {
        "goal": "gain",
        "gender": "male",
        "birthDate": "2001-03-15",
        "height": 165,
        "weight": 90,
        "activityLevel": 3,
        "account": {
            "name": "Teste",
            "email": "test@gmail.com",
            "password": "password"
        }
    }

    controller = SignupController(
        user_repository=UserRepository(db_session=test_session_db),
        hashed_service=HashedPasswordService()
    )
    response = await controller.handle(body=request_body)

    assert response.get("statusCode", 200) == 409
    assert response["body"].get("error", "") == "Email already exists"
