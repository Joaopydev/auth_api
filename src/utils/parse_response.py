import json
from typing import Dict, Any

from ..app_types.http import HTTPResponse

def parse_response(response: Dict[str, Any]) -> HTTPResponse:
    return {
        "statusCode": response.get("statusCode"),
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response.get("body")) if response.get("body") else None
    }