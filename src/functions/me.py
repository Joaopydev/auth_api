import asyncio
from typing import Dict, Any

from ..utils.parse_protected_event import parse_protected_event
from ..utils.parse_response import parse_response
from ..utils.http import unauthorized
from ..app_types.http import HTTPResponse
from ..controllers.MeController import MeController
from ..exceptions.AccessTokenNotProvided import AccessTokenNotProvided
from ..exceptions.InvalidAccessToken import InvalidAccessToken


async def async_handler(event: Dict[str, Any], context: Any) -> HTTPResponse:
    try:
        request = parse_protected_event(event=event)
        controller = MeController()
        response = await controller.handle(data=request)
        return parse_response(response=response)
    except AccessTokenNotProvided:
        return parse_response(response=unauthorized(body={"error": "Access token not provided."}))
    except InvalidAccessToken:
        return parse_response(response=unauthorized(body={"error": "Invalid access token"}))
    

def handler(event: Dict[str, Any], context: Any) -> HTTPResponse:
    return asyncio.run(async_handler(event=event, context=context))