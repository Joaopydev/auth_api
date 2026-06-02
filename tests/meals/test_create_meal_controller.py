import pytest
import json
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timezone

from src.utils.parse_protected_event import parse_protected_event
from src.controllers.create_meal import CreateMealController
from src.repository.meal_repository import MealRepository


@pytest.mark.asyncio
async def test_create_meal_successfully(test_session_db, test_login_user):
    mock_storage_service = Mock()
    mock_storage_service.get_upload_url = Mock(return_value="https://fake-url.com/image.jpg")

    create_meal_controller = CreateMealController(
        meal_repository=MealRepository(test_session_db),
        storage_service=mock_storage_service
    )
    event = {
        "headers": {"authorization": f"Bearer {test_login_user}"},
        "body": json.dumps({
            "fileType": "image/jpeg",
            "timezone": "America/Sao_Paulo"
        })
    }
    request = parse_protected_event(event)
    response = await create_meal_controller.handle(request)

    mock_storage_service.get_upload_url.assert_called_once()
    assert response["body"]["meal"]
    assert response["body"]["presignedUrl"]