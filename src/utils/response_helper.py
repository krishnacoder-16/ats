
import json
from typing import Any, Dict, Optional


def success_response(data: Any, status_code: int = 200) -> Dict:

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
