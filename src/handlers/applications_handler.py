"""
Lambda handler: GET /applications?job_id=<id>

Fetches all applications (candidacies) for a given job from Recruitee
and returns them in a standardized format.
"""
from src.services.recruitee_service import get_applications
from src.utils.response_helper import success_response
from src.utils.error_handler import handle_errors, get_query_param


@handle_errors
def handler(event: dict, context) -> dict:
    """
    AWS Lambda entry point for GET /applications.

    Query parameters:
        job_id (required): The Recruitee offer ID to fetch applications for.

    Returns:
        200 response with list of applications.

    Example response body:
        [
            {
                "id": "111",
                "candidate_name": "Jane Smith",
                "email": "jane@example.com",
                "status": "SCREENING"
            }
        ]
    """
    # Extract required job_id query param (raises ValueError if missing)
    job_id = get_query_param(event, "job_id", required=True)

    applications = get_applications(job_id)
    return success_response(applications)
