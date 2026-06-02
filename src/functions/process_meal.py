import json
import asyncio

from ..queues.process_meal import ProcessMeal
from ..repository.meal_repository import MealRepository
from ..services.ai.ai_service.ai_client import AIClient
from ..services.storage.storage_service import StorageService
from ..db.connection import get_db

from ..observability.logger import logger


async def async_handler(event) -> None:
    logger.info(
        "Meal processing batch started",
        extra={
            "records_count": len(event["Records"])
        }
    )

    process_meal = ProcessMeal(
        meal_repository=MealRepository(db_session=get_db),
        storage_service=StorageService(),
        ai_client=AIClient(),
    )

    tasks = [
        process_meal.process(
            file_key=json.loads(record["body"])["file_key"]
        )
        for record in event["Records"]
    ]

    await asyncio.gather(*tasks)

    logger.info("Meal processing batch finished")


@logger.inject_lambda_context
def handler(event, _) -> None:
    asyncio.run(async_handler(event=event))