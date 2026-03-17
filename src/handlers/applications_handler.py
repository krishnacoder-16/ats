from src.services.recruitee_service import get_applications
from src.utils.response_helper import success_response
from src.utils.error_handler import handle_errors, get_query_param


@handle_errors
def handler(event: dict, context) -> dict:

    # Extract required job_id query param (raises ValueError if missing)
    job_id = get_query_param(event, "job_id", required=True)

    applications = get_applications(job_id)
    return success_response(applications)
