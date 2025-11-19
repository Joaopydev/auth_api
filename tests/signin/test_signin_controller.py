import pytest
from pydantic import ValidationError
from src.controllers.SigninController import SigninController
from src.utils.http import bad_request


@pytest.mark.asyncio
async def test_signin_controller_invalid_email(test_session_db):
    request_body = {
        "email": "invalid-email",
        "password": "password",
    }

    controller = SigninController(session=lambda: test_session_db)

    with pytest.raises(ValidationError) as exc_info:
        await controller._validate_body(body=request_body)
    
    assert isinstance(exc_info.value, ValidationError)


@pytest.mark.asyncio
async def test_signin_controller_invalid_credentials(test_session_db):
    request_body = {
        "email": "joao@gmail.com",
        "password": "password",
    }

    controller = SigninController(session=lambda: test_session_db)

    result = await controller.handle(body=request_body)

    assert result["statusCode"] == 401
    assert result["body"]["error"] == "Invalid Credentials."


@pytest.mark.asyncio
async def test_signin_controller_ok(test_session_db, test_user):
    request_body = {
        "email": "joao@gmail.com",
        "password": "password",
    }

    controller = SigninController(session=lambda: test_session_db)

    result = await controller.handle(body=request_body)

    assert result["statusCode"] == 200
    assert "access_token" in result["body"]