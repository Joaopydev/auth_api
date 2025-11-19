import json
from typing import Dict, Any
from ..app_types.http import HTTPResquest

def parse_event(event: Dict[str, Any]) -> HTTPResquest:
    body = json.loads(event.get("body", "{}"))
    params = event.get("pathParameters", {})
    query_params = event.get("queryStringParameters", {})

    return {
        "body": body,
        "params": params,
        "query_params": query_params,
    }