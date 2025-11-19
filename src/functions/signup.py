import asyncio
from typing import Dict, Any

from ..controllers.SignupController import SignupController
from ..app_types.http import HTTPResponse
from ..utils.parse_event import parse_event
from ..utils.parse_response import parse_response


async def async_handler(event: Dict[str, Any], context: Any) -> HTTPResponse:
    request = parse_event(event=event)
    response = await SignupController.handle(body=request.get("body", {}))
    return parse_response(response=response)


def handler(event: Dict[str, Any], context: Any) -> HTTPResponse:
    return asyncio.run(async_handler(event=event, context=context))