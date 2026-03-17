"""
Response helper utilities.
Provides standardized JSON response formatting for AWS Lambda handlers.
"""
import json
from typing import Any, Dict, Optional


def success_response(data: Any, status_code: int = 200) -> Dict:
    """
    Build a standardized success response dict for API Gateway.

    Args:
        data: The response payload (list or dict).
        status_code: HTTP status code (default 200).

    Returns:
        API Gateway-compatible response dict.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        "body": json.dumps(data),
    }


def error_response(message: str, status_code: int = 500, details: Optional[str] = None) -> Dict:
    """
    Build a standardized error response dict for API Gateway.

    Args:
        message: Human-readable error message.
        status_code: HTTP status code (default 500).
        details: Optional extra detail string (e.g., upstream error message).

    Returns:
        API Gateway-compatible response dict.
    """
    body: Dict[str, Any] = {"error": message}
    if details:
        body["details"] = details

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        "body": json.dumps(body),
    }
