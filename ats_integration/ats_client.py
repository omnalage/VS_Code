import os
import logging
from typing import Any, Dict, List, Optional, Tuple

import requests


logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


class ATSClientError(Exception):
    """Error raised when the underlying ATS returns an error or cannot be reached."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class ATSClient:
    """
    Minimal, generic ATS client.

    This client assumes the underlying ATS exposes the following REST endpoints:

    - GET {base_url}/jobs
    - POST {base_url}/candidates
    - GET {base_url}/applications

    All calls authenticate using a bearer token in the Authorization header.

    You can adapt this class to your assigned ATS by changing the endpoint
    URLs and mapping functions (see map_job, map_application).
    """

    def __init__(self) -> None:
        base_url = os.getenv("ATS_BASE_URL")
        api_key = os.getenv("ATS_API_KEY")

        if not base_url or not api_key:
            raise RuntimeError("ATS_BASE_URL and ATS_API_KEY environment variables must be set")

        # Strip trailing slash to make URL joins consistent
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    # ---------- Public API used by Lambda handlers ----------

    def list_jobs(
        self, page: Optional[int] = None, per_page: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Return jobs in unified format plus optional pagination metadata.
        """
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        raw = self._request("GET", "/jobs", params=params)

        # We support two shapes:
        # 1) {"items": [...], "pagination": {...}}
        # 2) direct list: [...]
        if isinstance(raw, dict) and "items" in raw:
            items = raw.get("items", [])
            pagination = raw.get("pagination") or raw.get("meta") or {}
        else:
            items = raw
            pagination = {}

        jobs = [self.map_job(job) for job in items]
        return jobs, pagination or None

    def create_candidate_with_application(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a candidate in the ATS and attach them to a given job.

        For a real ATS you may need to:
        1) Create the candidate (POST /candidates)
        2) Create an application or pipeline entry (POST /applications)

        Here we assume the ATS accepts a single POST /candidates that both
        creates the candidate and attaches them to the job.
        """
        body = {
            "name": payload["name"],
            "email": payload["email"],
            "phone": payload.get("phone"),
            "resume_url": payload.get("resume_url"),
            "job_id": payload["job_id"],
        }

        created = self._request("POST", "/candidates", json=body)
        return created

    def list_applications(
        self, job_id: str, page: Optional[int] = None, per_page: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        List applications for a given job in unified format.
        """
        params: Dict[str, Any] = {"job_id": job_id}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        raw = self._request("GET", "/applications", params=params)

        if isinstance(raw, dict) and "items" in raw:
            items = raw.get("items", [])
            pagination = raw.get("pagination") or raw.get("meta") or {}
        else:
            items = raw
            pagination = {}

        apps = [self.map_application(app) for app in items]
        return apps, pagination or None

    # ---------- Mapping helpers ----------

    @staticmethod
    def map_job(job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map ATS-specific job fields into the unified job schema.

        Expected unified format:
            {
              "id": "string",
              "title": "string",
              "location": "string",
              "status": "OPEN|CLOSED|DRAFT",
              "external_url": "string"
            }

        Adjust this mapping to your actual ATS.
        """
        status = (job.get("status") or job.get("state") or "").upper()

        # Normalise a few common variants
        if status in {"PUBLISHED", "ACTIVE"}:
            status = "OPEN"

        return {
            "id": str(job.get("id") or job.get("job_id") or ""),
            "title": job.get("title") or job.get("name") or "",
            "location": job.get("location") or job.get("office") or "",
            "status": status or "OPEN",
            "external_url": job.get("external_url")
            or job.get("apply_url")
            or job.get("url")
            or "",
        }

    @staticmethod
    def map_application(app: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map ATS-specific application fields into the unified schema:

            {
              "id": "string",
              "candidate_name": "string",
              "email": "string",
              "status": "APPLIED|SCREENING|REJECTED|HIRED"
            }
        """
        status = (app.get("status") or app.get("stage") or "").upper()

        # Very light normalisation
        if status in {"NEW", "SUBMITTED"}:
            status = "APPLIED"

        candidate = app.get("candidate") or {}

        return {
            "id": str(app.get("id") or app.get("application_id") or ""),
            "candidate_name": candidate.get("name")
            or f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()
            or app.get("candidate_name")
            or "",
            "email": candidate.get("email") or app.get("email") or "",
            "status": status or "APPLIED",
        }

    # ---------- Low-level HTTP helper ----------

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.request(method, url, timeout=10, **kwargs)
        except requests.RequestException as exc:
            logger.error("Error calling ATS: %s", exc)
            raise ATSClientError("Failed to reach ATS", details={"error": str(exc)})

        if not resp.ok:
            try:
                payload = resp.json()
            except ValueError:
                payload = {"raw": resp.text}

            logger.warning("ATS error %s: %s", resp.status_code, payload)
            raise ATSClientError(
                "ATS returned an error",
                status_code=resp.status_code,
                details=payload,
            )

        if resp.status_code == 204:
            return None

        try:
            return resp.json()
        except ValueError:
            logger.error("ATS response is not JSON: %s", resp.text)
            raise ATSClientError(
                "Invalid response from ATS", status_code=resp.status_code, details={"raw": resp.text}
            )


