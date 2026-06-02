import asyncio
from typing import Dict, Any

from ..utils.parse_protected_event import parse_protected_event
from ..utils.parse_response import parse_response
from ..utils.http import unauthorized

from ..app_types.http import HTTPResponse
from ..exceptions.AccessTokenNotProvided import AccessTokenNotProvided
from ..exceptions.InvalidAccessToken import InvalidAccessToken
from ..controllers.create_meal import CreateMealController

from ..services.storage.storage_service import StorageService
from ..repository.meal_repository import MealRepository
from ..db.connection import get_db


async def async_handler(event: Dict[str, Any], context: Any) -> HTTPResponse:
    response = None
    
    try:
        request = parse_protected_event(event=event)
        controller = CreateMealController(
            meal_repository=MealRepository(db_session=get_db),
            storage_service=StorageService(),
        )
        response = await controller.handle(request=request)
    except AccessTokenNotProvided:
        response = unauthorized(body={"error": "Access token not provided."})
    except InvalidAccessToken:
        response = unauthorized(body={"error": "Invalid access token"})
    except Exception as e:
        response = unauthorized(body={"error": str(e)})
    finally:
        return parse_response(response=response)
    

def handler(event: Dict[str, Any], context: Any) -> HTTPResponse:
    return asyncio.run(async_handler(event=event, context=context))