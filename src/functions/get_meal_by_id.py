import asyncio
from typing import Dict, Any

from ..utils.parse_protected_event import parse_protected_event
from ..utils.parse_response import parse_response
from ..utils.http import unauthorized

from ..exceptions.AccessTokenNotProvided import AccessTokenNotProvided
from ..exceptions.InvalidAccessToken import InvalidAccessToken
from ..controllers.get_meal_by_id import GetMealByIdController
from ..app_types.http import HTTPResponse

from ..repository.meal_repository import MealRepository
from ..db.connection import get_db


async def async_handler(event: Dict[str, Any], content: Dict[str, Any]) -> HTTPResponse:
    response = None
    
    try:
        request = parse_protected_event(event=event)
        controller = GetMealByIdController(MealRepository(db_session=get_db))
        response = await controller.handle(request=request)
    except AccessTokenNotProvided:
        response = unauthorized(body={"error": "Access token not provided."})
    except InvalidAccessToken:
        response = unauthorized(body={"error": "Invalid access token"})
    except Exception as e:
        response = unauthorized(body={"error": str(e)})
    finally:
        print("Lambda returns:", response)
        return parse_response(response=response)


def handler(event: Dict[str, Any], content: Dict[str, Any]) -> HTTPResponse:
    return asyncio.run(async_handler(event=event, content=content))
    