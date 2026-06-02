import json
from zoneinfo import ZoneInfo

from ..db.models.meals import MealStatus
from ..utils.http import bad_request
from ..repository.meal_repository import MealRepository
from ..services.storage.storage_service import StorageService
from ..services.ai.ai_service.ai_client import AIClient

from ..observability.logger import logger


class ProcessMeal:

    def __init__(
        self,
        meal_repository: MealRepository,
        storage_service: StorageService,
        ai_client: AIClient,
    ):
        self.meal_repository = meal_repository
        self.storage_service = storage_service
        self.ai_client = ai_client

    async def process(self, file_key: str):
        meal = await self.meal_repository.get_meal_by_file_key(file_key)

        if not meal:
            logger.warning(
                "Meal not found for file key",
                extra={
                    "file_key": file_key
                }
            )
            return
            
        if meal.status.value in ["failed", "success"]:
            return
        
        await self.meal_repository.update_meal_status(
            meal_id=meal.id,
            new_status=MealStatus.processing
        )

        logger.info(
            "Started processing meal",
            extra={
                "meal_id": meal.id,
            }
        )
        try:
            meal_details = ""
            head_object = await self.storage_service.head_object(key=meal.input_file_key)
            timezone = head_object["Metadata"].get("timezone", "UTC")
            meal_created_at = meal.created_at.astimezone(ZoneInfo(timezone))
            if meal.input_type.value == "audio":
                audio_data = await self.storage_service.read_object_content(key=meal.input_file_key)
                transcription = await self.ai_client.transcribe_audio(
                    audio_data=audio_data,
                    key=file_key
                )
                meal_details = await self.ai_client.get_meal_details_from_text(
                    input=transcription,
                    created_at=meal_created_at,
                    file_key=file_key
                )
            elif meal.input_type.value == "picture":
                image_url = self.storage_service.get_download_url(meal.input_file_key)
                meal_details = await self.ai_client.get_meal_details_from_image(
                    image_url=image_url,
                    created_at=meal_created_at,
                    file_key=file_key
                )
                
            parse_meal_details = json.loads(meal_details)
            await self.meal_repository.update_meal_data(
                meal_id=meal.id,
                new_status=MealStatus.success,
                name=parse_meal_details.get("name", ""),
                icon=parse_meal_details.get("icon", ""),
                foods=parse_meal_details.get("foods", []),
            )

            logger.info(
                msg="Finished processing meal successfully",
                extra={"meal_id": meal.id},
            )
        except TimeoutError as e:
            """Retry if lambda throws timeout error"""
            logger.exception(
                msg="Timeout error occurred while processing meal, retrying",
                extra={
                    "meal_id": meal.id,
                }
            )
            raise
        except Exception as e:
            logger.exception(
                msg="Failed to process meal",
                extra={
                    "meal_id": meal.id,
                }
            )
            await self.meal_repository.update_meal_status(
                meal_id=meal.id,
                new_status=MealStatus.failed
            )