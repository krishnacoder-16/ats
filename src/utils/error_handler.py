import json
import traceback
from functools import wraps
from typing import Callable

from src.utils.response_helper import error_response


def handle_errors(func: Callable) -> Callable:

    @wraps(func)
    def wrapper(event, context):
        try:
            return func(event, context)
        except ValueError as e:
            return error_response(str(e), status_code=400)
        except PermissionError as e:
            return error_response(str(e), status_code=403)
        except LookupError as e:
            return error_response(str(e), status_code=404)
        except Exception as e:
            # Log the full traceback for debugging (visible in CloudWatch / serverless-offline)
            traceback.print_exc()
            return error_response(
                "An unexpected internal error occurred.",
                status_code=500,
                details=str(e),
            )

    return wrapper


def parse_request_body(event: dict) -> dict:
    body = event.get("body")
    if not body:
        raise ValueError("Request body is required but was not provided.")
    try:
        if isinstance(body, str):
            return json.loads(body)
        return body  # already parsed (e.g., in serverless-offline)
    except json.JSONDecodeError:
        raise ValueError("Request body must be valid JSON.")


def get_query_param(event: dict, param_name: str, required: bool = False) -> str | None:

    params = event.get("queryStringParameters") or {}
    value = params.get(param_name)
    if required and not value:
        raise ValueError(f"Query parameter '{param_name}' is required.")
    return value
