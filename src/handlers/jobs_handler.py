"""
Lambda handler: GET /jobs

Fetches all job offers from Recruitee and returns them in a standardized format.
"""
from src.services.recruitee_service import get_jobs
from src.utils.response_helper import success_response
from src.utils.error_handler import handle_errors


@handle_errors
def handler(event: dict, context) -> dict:
    """
    AWS Lambda entry point for GET /jobs.

    Args:
        event: API Gateway Lambda proxy event.
        context: Lambda execution context (unused).

    Returns:
        API Gateway response with list of jobs in body.

    Example response body:
        [
            {
                "id": "123456",
                "title": "Software Engineer",
                "location": "Remote",
                "status": "OPEN",
                "external_url": "https://careers.example.com/jobs/123456"
            }
        ]
    """
    jobs = get_jobs()
    return success_response(jobs)
