
import requests
from typing import Any, Dict, List, Optional

from src.config.settings import RECRUITEE_API_KEY, RECRUITEE_BASE_URL

# Internal helpers

def _get_headers() -> Dict[str, str]:
    # Return HTTP headers required by Recruitee API (Bearer token auth).
    return {
        "Authorization": f"Bearer {RECRUITEE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _handle_response(response: requests.Response, context: str = "") -> Dict:

    try:
        response.raise_for_status()
        return response.json()
    except requests.HTTPError:
        status = response.status_code
        try:
            detail = response.json()
        except Exception:
            detail = response.text

        prefix = f"Recruitee API error [{context}] HTTP {status}"

        if status in (401, 403):
            raise PermissionError(f"{prefix}: Authentication failed. Check your RECRUITEE_API_KEY.")
        if status == 404:
            raise LookupError(f"{prefix}: Resource not found.")
        if 400 <= status < 500:
            raise ValueError(f"{prefix}: {detail}")
        raise RuntimeError(f"{prefix}: {detail}")


def _paginate_get(url: str, result_key: str, params: Optional[Dict] = None) -> List[Dict]:
    limit = 100
    offset = 0
    all_items: List[Dict] = []
    query_params = dict(params or {})

    while True:
        query_params.update({"limit": limit, "offset": offset})
        response = requests.get(url, headers=_get_headers(), params=query_params)
        data = _handle_response(response, context=result_key)
        items = data.get(result_key, [])
        all_items.extend(items)

        # Stop if we received fewer items than requested (last page)
        if len(items) < limit:
            break
        offset += limit

    return all_items


# Status normalisation helpers

# Map Recruitee offer status values to our standardized enum
_JOB_STATUS_MAP: Dict[str, str] = {
    "published": "OPEN",
    "internal": "OPEN",
    "closed": "CLOSED",
    "draft": "DRAFT",
    "archived": "CLOSED",
}

# Map Recruitee pipeline stage/disqualified flag to our status enum
_APPLICATION_STATUS_MAP: Dict[str, str] = {
    "sourced": "APPLIED",
    "application": "APPLIED",
    "phone_screen": "SCREENING",
    "interview": "SCREENING",
    "offer": "SCREENING",
    "hired": "HIRED",
    "rejected": "REJECTED",
    "disqualified": "REJECTED",
}


def _normalize_job_status(recruitee_status: str) -> str:
    """Return our standardized job status string."""
    return _JOB_STATUS_MAP.get(recruitee_status.lower(), "DRAFT")


def _normalize_application_status(candidate: Dict[str, Any]) -> str:
    if candidate.get("disqualified"):
        return "REJECTED"
    stage = (candidate.get("pipeline_stage") or {}).get("name", "")
    return _APPLICATION_STATUS_MAP.get(stage.lower(), "APPLIED")


# Public service functions

def get_jobs() -> List[Dict[str, str]]:
    """
    Fetch all job offers from Recruitee and return in standardised format.

    Returns:
        List of job dicts with keys: id, title, location, status, external_url.
    """
    url = f"{RECRUITEE_BASE_URL}/offers"
    raw_offers = _paginate_get(url, result_key="offers")

    jobs = []
    for offer in raw_offers:
        jobs.append({
            "id": str(offer.get("id", "")),
            "title": offer.get("title", ""),
            "location": offer.get("location", "") or "",
            "status": _normalize_job_status(offer.get("status", "draft")),
            "external_url": offer.get("url", "") or "",
        })

    return jobs


def create_candidate(
    name: str,
    email: str,
    job_id: str,
    phone: Optional[str] = None,
    resume_url: Optional[str] = None,
) -> Dict[str, Any]:
    # Step 1: Create the candidate profile and attach to job 
    candidate_payload = {
        "candidate": {
            "name": name,
            "emails": [email],
            "phones": [phone] if phone else [],
            "cover_letter": f"Resume: {resume_url}" if resume_url else "",
        },
        "offers": [job_id]
    }

    candidate_url = f"{RECRUITEE_BASE_URL}/candidates"
    candidate_resp = requests.post(
        candidate_url,
        headers=_get_headers(),
        json=candidate_payload,
    )
    candidate_data = _handle_response(candidate_resp, context="create_candidate")
    candidate_id = candidate_data.get("candidate", {}).get("id")

    if not candidate_id:
        raise RuntimeError("Recruitee did not return a candidate ID after creation.")

    return {
        "candidate_id": str(candidate_id),
        "message": "Candidate created and attached to job successfully.",
    }


def get_applications(job_id: str) -> List[Dict[str, str]]:

    url = f"{RECRUITEE_BASE_URL}/candidates"
    raw_candidates = _paginate_get(url, result_key="candidates", params={"offer_id": job_id})

    applications = []
    for candidate in raw_candidates:
        # Extract first email from the list
        emails = candidate.get("emails") or []
        email = emails[0] if emails else ""

        applications.append({
            "id": str(candidate.get("id", "")),
            "candidate_name": candidate.get("name", ""),
            "email": email,
            "status": _normalize_application_status(candidate),
        })

    return applications
