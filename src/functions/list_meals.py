import asyncio
from typing import Dict, Any

from ..utils.parse_protected_event import parse_protected_event
from ..utils.http import unauthorized, internal_server_error

from ..exceptions.AccessTokenNotProvided import AccessTokenNotProvided
from ..exceptions.InvalidAccessToken import InvalidAccessToken

from ..controllers.list_meals import ListMealController
from ..app_types.http import HTTPResponse

from ..observability.logger import logger
from ..observability.helper import finalize_response

from ..repository.meal_repository import MealRepository
from ..db.connection import get_db


async def async_handler(event: Dict[str, Any], context: any) -> HTTPResponse:
    response = None
    try:
        request = parse_protected_event(event=event)
        controller = ListMealController(MealRepository(db_session=get_db))
        response = await controller.handle(request=request)
    except AccessTokenNotProvided:
        response = unauthorized(body={"error": "Access token not provided."})
    except InvalidAccessToken:
        response = unauthorized(body={"error": "Invalid access token"})
    except Exception as e:
        logger.exception("Unexpected error occurred while listing meals")
        response = internal_server_error(body={"error": "Unexpected error occurred"})

    return finalize_response(response=response)


@logger.inject_lambda_context
def handler(event: Dict[str, Any], context: any) -> HTTPResponse:
    return asyncio.run(async_handler(event=event, context=context))
    