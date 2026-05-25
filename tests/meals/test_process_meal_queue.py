import json
from datetime import datetime, timezone

import pytest
from unittest.mock import AsyncMock, Mock

from src.queues.process_meal import ProcessMeal
from src.db.models.meals import MealStatus, InputType

MEAL_DETAILS_MOCK = {
    "name": "Lunch",
    "icon": "🍗",
    "foods": [
        {
            "name": "Test White Rice",
            "quantity": "200g",
            "carbohydrates": 42,
            "proteins": 3.5,
            "fats": 0.4,
        },
        {
            "name": "Test Chicken",
            "quantity": "100g",
            "calories": 165,
            "carbohydrates": 32,
            "proteins": 31,
            "fats": 3.6,
        },
    ]
}

@pytest.mark.asyncio
async def test_should_process_audio_meal_successfully():
    meal_mock = Mock(
        id="meal-test-1",
        status=MealStatus.uploading,
        input_file_key="audio.mp4",
        input_type=InputType.audio,
        created_at=datetime.now(tz=timezone.utc)
    )

    meal_repository_mock = Mock()
    meal_repository_mock.get_meal_by_file_key = AsyncMock(return_value=meal_mock)
    meal_repository_mock.update_meal_status = AsyncMock()
    meal_repository_mock.update_meal_data = AsyncMock()

    storage_service_mock = Mock()
    storage_service_mock.read_object_content = AsyncMock(return_value=b"fake-audio")
    storage_service_mock.head_object = AsyncMock(return_value={
        "Metadata": {
            "timezone": "America/Sao_Paulo"
        }
    })

    ai_client_mock = Mock()
    ai_client_mock.transcribe_audio = AsyncMock(
        return_value="200 grams of rice and 100 grams of chicken"
    )
    ai_client_mock.get_meal_details_from_text = AsyncMock(return_value=json.dumps(MEAL_DETAILS_MOCK))

    process_meal = ProcessMeal(
        meal_repository=meal_repository_mock,
        storage_service=storage_service_mock,
        ai_client=ai_client_mock,
    )

    await process_meal.process(file_key=meal_mock.input_file_key)

    meal_repository_mock.update_meal_status.assert_any_await(
        meal_id=meal_mock.id,
        new_status=MealStatus.processing
    )

    storage_service_mock.head_object.assert_awaited_once()
    storage_service_mock.read_object_content.assert_awaited_once()

    ai_client_mock.transcribe_audio.assert_awaited_once()
    ai_client_mock.get_meal_details_from_text.assert_awaited_once()

    meal_repository_mock.update_meal_data.assert_awaited_once_with(
        meal_id=meal_mock.id,
        new_status=MealStatus.success,
        name=MEAL_DETAILS_MOCK["name"],
        icon=MEAL_DETAILS_MOCK["icon"],
        foods=MEAL_DETAILS_MOCK["foods"],
    )


#TODO implement test for picture meal processing
async def test_should_process_picture_meal_successfully():
    meal_mock = Mock(
        id="meal-test-2",
        status=MealStatus.uploading,
        input_file_key="image.jpg",
        input_type=InputType.picture,
        created_at=datetime.now(timezone.utc)
    )

    meal_repository_mock = Mock()
    meal_repository_mock.get_meal_by_file_key = AsyncMock(return_value=meal_mock)
    meal_repository_mock.update_meal_status = AsyncMock()
    meal_repository_mock.update_meal_data = AsyncMock()

    storage_service_mock = Mock()
    storage_service_mock.get_download_url = Mock(return_value="https://fake-url.com/image.jpg")
    storage_service_mock.head_object = AsyncMock(return_value={
        "Metadata": {
            "timezone": "America/Sao_Paulo"
        }
    })


    ai_client_mock = Mock()
    ai_client_mock.get_meal_details_from_image = AsyncMock(return_value=json.dumps(MEAL_DETAILS_MOCK))

    process_meal = ProcessMeal(
        meal_repository=meal_repository_mock,
        storage_service=storage_service_mock,
        ai_client=ai_client_mock,
    )

    await process_meal.process(meal_mock.input_file_key)

    meal_repository_mock.get_meal_by_file_key.assert_awaited_once_with(meal_mock.input_file_key)
    meal_repository_mock.update_meal_status.assert_any_await(
        meal_id=meal_mock.id,
        new_status=MealStatus.processing
    )

    storage_service_mock.head_object.assert_awaited_once()
    storage_service_mock.get_download_url.assert_called_once_with(meal_mock.input_file_key)
    ai_client_mock.get_meal_details_from_image.assert_awaited_once()

    meal_repository_mock.update_meal_data.assert_awaited_once_with(
        meal_id=meal_mock.id,
        new_status=MealStatus.success,
        name=MEAL_DETAILS_MOCK["name"],
        icon=MEAL_DETAILS_MOCK["icon"],
        foods=MEAL_DETAILS_MOCK["foods"],
    )

@pytest.mark.asyncio
async def test_should_failed_to_process_meal():
    meal_mock = Mock(
        id="meal-test-3",
        status=MealStatus.uploading,
        input_file_key="audio.mp4",
        input_type=InputType.audio,
        created_at=datetime.now(timezone.utc)
    )

    meal_repository_mock = Mock()
    meal_repository_mock.get_meal_by_file_key = AsyncMock(return_value=meal_mock)
    meal_repository_mock.update_meal_status = AsyncMock()
    meal_repository_mock.update_meal_data = AsyncMock()

    storage_service_mock = Mock()
    storage_service_mock.read_object_content = AsyncMock(return_value=b"fake-audio")
    storage_service_mock.head_object = AsyncMock(return_value={
        "Metadata": {
            "timezone": "America/Sao_Paulo"
        }
    })


    ai_client_mock = Mock()
    ai_client_mock.transcribe_audio = AsyncMock(side_effect=Exception("AI service error"))

    process_meal = ProcessMeal(
        meal_repository=meal_repository_mock,
        storage_service=storage_service_mock,
        ai_client=ai_client_mock,
    )

    await process_meal.process(file_key=meal_mock.input_file_key)

    meal_repository_mock.update_meal_status.assert_any_await(
        meal_id=meal_mock.id,
        new_status=MealStatus.processing
    )

    storage_service_mock.head_object.assert_awaited_once_with(key=meal_mock.input_file_key)
    storage_service_mock.read_object_content.assert_awaited_once_with(key=meal_mock.input_file_key)
    ai_client_mock.transcribe_audio.assert_awaited_once()

    meal_repository_mock.update_meal_data.assert_not_awaited()
    meal_repository_mock.update_meal_status.assert_any_await(
        meal_id=meal_mock.id,
        new_status=MealStatus.failed
    )