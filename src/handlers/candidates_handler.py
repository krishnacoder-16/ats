from src.services.recruitee_service import create_candidate
from src.utils.response_helper import success_response
from src.utils.error_handler import handle_errors, parse_request_body


# Required fields in the request body
_REQUIRED_FIELDS = ("name", "email", "job_id")


@handle_errors
def handler(event: dict, context) -> dict:
    body = parse_request_body(event)

    # Validate required fields
    missing = [f for f in _REQUIRED_FIELDS if not body.get(f)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Extract fields (phone and resume_url are optional)
    name: str = body["name"].strip()
    email: str = body["email"].strip()
    phone: str = body.get("phone", "").strip()
    resume_url: str = body.get("resume_url", "").strip()
    job_id: str = str(body["job_id"]).strip()

    result = create_candidate(
        name=name,
        email=email,
        job_id=job_id,
        phone=phone,
        resume_url=resume_url,
    )

    return success_response(result, status_code=201)
