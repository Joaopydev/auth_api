import pytest
from pydantic import ValidationError
from src.controllers.SignupController import SignupController


@pytest.mark.asyncio
async def test_signup_controller_invalid_data_entry(test_session_db):
    request_body = {
        "name": 000000,
        "email": "invalid-email",
        "password": 000000,
    }

    controller = SignupController(session=lambda: test_session_db)

    with pytest.raises(ValidationError) as exc_info:
        await controller._validate_body(body=request_body)

    assert isinstance(exc_info.value, ValidationError)


@pytest.mark.asyncio
async def test_signup_controller_created(test_session_db):
    request_body = {
        "name": "Test",
        "email": "test@gmail.com",
        "password": "password",
    }

    controller = SignupController(session=lambda: test_session_db)
    result = await controller.handle(body=request_body)

    assert result.get("statusCode", 400) == 201
    assert "access_token" in result.get("body", {})


@pytest.mark.asyncio
async def test_signup_controller_conflict(test_session_db, test_user):
    request_body = {
        "name": "Test",
        "email": "joao@gmail.com",
        "password": "password"
    }

    controller = SignupController(session=lambda: test_session_db)
    result = await controller.handle(body=request_body)

    assert result.get("statusCode", 200) == 409
    assert result["body"].get("error", "") == "Email already exists"
