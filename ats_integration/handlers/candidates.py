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


REQUIRED_FIELDS = ["name", "email", "job_id"]


def create_candidate(event, _context):
    """
    Lambda handler for POST /candidates
    Expects JSON body:
      {
        "name": "string",
        "email": "string",
        "phone": "string",
        "resume_url": "string",
        "job_id": "string"
      }
    """
    if not event.get("body"):
        return _response(400, {"error": "invalid_request", "message": "Request body is required"})

    try:
        payload = json.loads(event["body"])
    except json.JSONDecodeError:
        return _response(400, {"error": "invalid_json", "message": "Request body must be valid JSON"})

    missing = [field for field in REQUIRED_FIELDS if not payload.get(field)]
    if missing:
        return _response(
            400,
            {
                "error": "validation_error",
                "message": "Missing required fields",
                "missing_fields": missing,
            },
        )

    try:
        client = ATSClient()
    except RuntimeError as exc:
        return _response(500, {"error": "configuration_error", "message": str(exc)})

    try:
        created = client.create_candidate_with_application(payload)
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

    return _response(
        201,
        {
            "message": "Candidate created and attached to job",
            "ats_payload": created,
        },
    )


