from .logger import logger
from ..utils.parse_response import parse_response


def finalize_response(response: dict) -> dict:
    logger.info(
        msg="Request Finished",
        extra={
            "status_code": response["statusCode"],
        }
    )
    return parse_response(response=response)