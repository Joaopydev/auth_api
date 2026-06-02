import asyncio
from typing import Dict, Any

from ..controllers.signin import SigninController
from ..app_types.http import HTTPResponse
from ..utils.parse_event import parse_event
from ..utils.parse_response import parse_response

from ..repository.user_repository import UserRepository
from ..services.hashed.hashed_service import HashedPasswordService
from ..db.connection import get_db


async def async_handler(event: Dict[str, Any], context: Any) -> HTTPResponse:
    request = parse_event(event=event)
    controller = SigninController(
        user_repository=UserRepository(db_session=get_db),
        hashed_service=HashedPasswordService(),
    )
    response = await controller.handle(body=request.get("body", {}))
    return parse_response(response=response)


def handler(event: Dict[str, Any], context: Any) -> HTTPResponse:
    return asyncio.run(async_handler(event=event, context=context))