import pytest
from unittest.mock import Mock, AsyncMock

from src.controllers.signin import SigninController
from src.services.hashed.hashed_service import HashedPasswordService
from src.repository.user_repository import UserRepository


@pytest.mark.asyncio
async def test_signin_controller_invalid_email():
    request_body = {
        "email": "invalid-email",
        "password": "password",
    }

    controller = SigninController(
        user_repository=Mock(),
        hashed_service=Mock(),
    )
    response = await controller.handle(request_body)
    assert response["statusCode"] == 400
    assert response["body"]["errors"][0]["type"] == "value_error"

@pytest.mark.asyncio
async def test_signin_controller_invalid_credentials():
    request_body = {
        "email": "joao@gmail.com",
        "password": "password",
    }

    user_repository_mock = AsyncMock()
    user_repository_mock.get_user_by_email.return_value = None
    controller = SigninController(
        user_repository=user_repository_mock,
        hashed_service=Mock()
    )

    result = await controller.handle(body=request_body)

    user_repository_mock.get_user_by_email.assert_called_once_with(email="joao@gmail.com")
    assert result["statusCode"] == 401
    assert result["body"]["error"] == "Invalid Credentials."


@pytest.mark.asyncio
async def test_signin_controller_ok(test_session_db, test_user):
    request_body = {
        "email": "test@gmail.com",
        "password": "password",
    }

    user_repository = UserRepository(test_session_db)
    hashed_service = HashedPasswordService()

    controller = SigninController(
        user_repository=user_repository,
        hashed_service=hashed_service
    )
    result = await controller.handle(body=request_body)

    assert result["statusCode"] == 200
    assert "accessToken" in result["body"]