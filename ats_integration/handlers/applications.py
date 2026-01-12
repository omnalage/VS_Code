import json
import os
import sys
from typing import Any, Dict

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ats_client import ATSClient, ATSClientError


def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }


def get_applications(event, _context):
    """
    Lambda handler for GET /applications?job_id=...
    Optional query params:
      - page
      - per_page
    """
    query = event.get("queryStringParameters") or {}
    job_id = query.get("job_id")
    if not job_id:
        return _response(
            400,
            {
                "error": "validation_error",
                "message": "job_id query parameter is required",
            },
        )

    page_raw = query.get("page")
    per_page_raw = query.get("per_page")

    page = int(page_raw) if page_raw is not None else None
    per_page = int(per_page_raw) if per_page_raw is not None else None

    try:
        client = ATSClient()
    except RuntimeError as exc:
        return _response(500, {"error": "configuration_error", "message": str(exc)})

    try:
        apps, pagination = client.list_applications(job_id=job_id, page=page, per_page=per_page)
    except ATSClientError as exc:
        status = exc.status_code or 502
        return _response(
            status,
            {
                "error": "ats_error",
                "message": str(exc),
                "details": exc.details,
                "source_status_code": exc.status_code,
            },
        )

    body: Dict[str, Any] = {"applications": apps}
    if pagination:
        body["pagination"] = pagination

    return _response(200, body)


