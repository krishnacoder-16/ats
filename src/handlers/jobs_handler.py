from src.services.recruitee_service import get_jobs
from src.utils.response_helper import success_response
from src.utils.error_handler import handle_errors


@handle_errors
def handler(event: dict, context) -> dict:

    jobs = get_jobs()
    return success_response(jobs)
