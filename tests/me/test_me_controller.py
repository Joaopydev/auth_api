import pytest

from src.controllers.MeController import MeController
from src.utils.parse_protected_event import parse_protected_event
from src.exceptions.AccessTokenNotProvided import AccessTokenNotProvided
from src.exceptions.InvalidAccessToken import InvalidAccessToken


def test_access_token_not_provided():
    event = {
        "headers": {}
    }

    with pytest.raises(AccessTokenNotProvided) as exc_info:
        parse_protected_event(event=event)

    assert isinstance(exc_info.value, AccessTokenNotProvided)


def test_invalid_access_token():
    event = {
        "headers": {"authorization": "Bearer TestToken"}
    }

    with pytest.raises(InvalidAccessToken) as exc_info:
        parse_protected_event(event=event)

    assert isinstance(exc_info.value, InvalidAccessToken)


def test_valid_access_token(test_login_user):

    event = {
        "headers": {"authorization": f"Bearer {test_login_user}"}
    }

    request = parse_protected_event(event=event)
    assert "user_id" in request


@pytest.mark.asyncio
async def test_me_controller(test_login_user, test_session_db):
    event = {
        "headers": {"authorization": f"Bearer {test_login_user}"}
    }

    request = parse_protected_event(event=event)

    controller = MeController(session=lambda: test_session_db)
    response = await controller.handle(data=request)

    assert response["statusCode"] == 200
    assert "user" in response["body"]

