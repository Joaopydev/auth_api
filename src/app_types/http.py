from typing import TypedDict, Dict, Any

class HTTPResponse(TypedDict):
    statusCode: int
    headers: Dict[str, Any]
    body: Dict[str, Any]


class HTTPResquest(TypedDict):
    body: Dict[str, Any]
    query_params: Dict[str, Any]
    params: Dict[str, Any]

class ProtectedHttpRequest(HTTPResquest):
    user_id: str