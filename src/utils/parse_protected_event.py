from typing import Dict, Any
from ..lib.jwt import validate_access_token
from ..app_types.http import ProtectedHttpRequest
from ..utils.parse_event import parse_event
from ..exceptions.AccessTokenNotProvided import AccessTokenNotProvided
from ..exceptions.InvalidAccessToken import InvalidAccessToken

def parse_protected_event(event: Dict[str, Any]) -> ProtectedHttpRequest:
    base_event = parse_event(event=event)
    header = event.get("headers", {})
    authorization = header.get("authorization")

    if authorization is None:
        raise AccessTokenNotProvided()

    token = authorization.split(" ")[1]    
    user_id = validate_access_token(token_jwt=token)

    if not user_id:
        raise InvalidAccessToken()
    
    base_event.update({"user_id": user_id})

    return base_event