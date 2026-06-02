from typing import Dict, Any
from ..app_types.http import HTTPResponse

def ok(body: Dict[str, Any]) -> HTTPResponse:
    return {
        "statusCode": 200,
        "body": body,
    }


def created(body: Dict[str, Any]) -> HTTPResponse:
    return {
        "statusCode": 201,
        "body": body,
    }


def bad_request(body: Dict[str, Any]) -> HTTPResponse:
    return {
        "statusCode": 400,
        "body": body,
    }


def conflict(body: Dict[str, Any]) -> HTTPResponse:
    return {
        "statusCode": 409,
        "body": body
    }


def unauthorized(body: Dict[str, Any]):
    return {
        "statusCode": 401,
        "body": body
    }


def internal_server_error(body: Dict[str, Any]) -> HTTPResponse:
    return {
        "statusCode": 500,
        "body": body,
    }


def not_found(body: Dict[str, Any]) -> HTTPResponse:
    return {
        "statusCode": 404,
        "body": body,
    }