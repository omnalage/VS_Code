## ATS Integration Microservice (Python + Serverless)

This project is a small backend service built with **Python** and the **Serverless Framework** (AWS Lambda + API Gateway).
It exposes a **unified REST API** for jobs, candidates, and applications while internally calling a (configurable) ATS API.

The service is deliberately implemented against a **generic ATS REST API** so that you can adapt it to your assigned ATS
by editing `ats_client.py` only.

---

### 1. Features & Endpoints

- **GET `/jobs`**
  - Returns a list of open jobs in a standard JSON format:

    ```json
    {
      "jobs": [
        {
          "id": "string",
          "title": "string",
          "location": "string",
          "status": "OPEN",
          "external_url": "string"
        }
      ],
      "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 42
      }
    }
    ```

  - Optional query params:
    - `page` – page number (integer)
    - `per_page` – page size (integer)

- **POST `/candidates`**
  - Accepts a candidate payload in a unified format:

    ```json
    {
      "name": "string",
      "email": "string",
      "phone": "string",
      "resume_url": "string",
      "job_id": "string"
    }
    ```

  - Creates the candidate in the underlying ATS and attaches them to the specified job
    (in this template we assume a single `POST /candidates` does both; if your ATS splits
    this into multiple calls, implement that in `ATSClient.create_candidate_with_application`).

- **GET `/applications?job_id=...`**
  - Lists applications for a given job in a unified format:

    ```json
    {
      "applications": [
        {
          "id": "string",
          "candidate_name": "string",
          "email": "string",
          "status": "APPLIED"
        }
      ],
      "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 10
      }
    }
    ```

  - Required query param:
    - `job_id` – ID of the job whose applications you want
  - Optional query params:
    - `page`
    - `per_page`

- **Error handling**
  - If the ATS returns an error, the service returns a clean JSON error:

    ```json
    {
      "error": "ats_error",
      "message": "ATS returned an error",
      "details": { "raw": "..." },
      "source_status_code": 500
    }
    ```

---

### 2. Architecture Overview

- **AWS Lambda + API Gateway** via **Serverless Framework**
- **Python 3.11** runtime
- **`ats_client.py`**:
  - Encapsulates all ATS-specific HTTP calls.
  - Provides:
    - `list_jobs(page, per_page)` → unified job objects
    - `create_candidate_with_application(payload)` → creates candidate + attaches to job
    - `list_applications(job_id, page, per_page)` → unified application objects
  - Contains mapping helpers (`map_job`, `map_application`) where you adapt field names and statuses.
- **Handlers**:
  - `handlers/jobs.py` → `GET /jobs`
  - `handlers/candidates.py` → `POST /candidates`
  - `handlers/applications.py` → `GET /applications`

---

### 3. Environment Variables & Configuration

All sensitive or environment-specific data is passed via environment variables in `serverless.yml`:

- **`ATS_BASE_URL`**: Base URL of your ATS API (e.g. `https://api.your-ats.com/v1`).
- **`ATS_API_KEY`**: API key or token for your ATS.
- **`ATS_ACCOUNT_ID`** (optional): Account ID / tenant identifier if your ATS requires it.
- **`LOG_LEVEL`** (optional): Python log level (`DEBUG`, `INFO`, `WARN`, etc.). Defaults to `INFO`.

You set them in your shell before running locally, for example:

```bash
export ATS_BASE_URL="https://api.your-ats.com/v1"
export ATS_API_KEY="your_api_key_here"
export ATS_ACCOUNT_ID="your-account-id"
export LOG_LEVEL="DEBUG"
```

The Serverless Framework then injects these into Lambda via the `provider.environment` block in `serverless.yml`.

---

### 4. How to Adapt to *Your* ATS

This template assumes a generic ATS API with:

- `GET /jobs` – list jobs
- `POST /candidates` – create candidate (and attach to job)
- `GET /applications` – list applications for a job

**In reality, every ATS is different.** To integrate with your assigned ATS:

1. Open `ats_client.py`.
2. Update the URL paths and request bodies in:
   - `_request(...)` caller paths (`/jobs`, `/candidates`, `/applications`)
   - `create_candidate_with_application(...)` (if your ATS needs a separate call to create an application).
3. Update the mappers:
   - `map_job(...)` – map ATS fields to:
     - `id`, `title`, `location`, `status`, `external_url`
   - `map_application(...)` – map ATS fields to:
     - `id`, `candidate_name`, `email`, `status`
4. If your ATS uses pagination via cursors / offsets instead of `(page, per_page)`, modify:
   - `list_jobs(...)` and `list_applications(...)` to accept and forward e.g. `cursor` or `offset`.
   - Return those tokens in the `pagination` dict.

Because all handlers call the ATS only via `ATSClient`, you don’t have to touch the Lambda handlers themselves.

---

### 5. “Sandbox / Trial” Setup (for a Real ATS)

The exact steps depend on the ATS vendor, but typically follow this pattern:

1. **Create a sandbox / trial account**
   - Go to the ATS provider’s website (e.g. Lever, Greenhouse, Workable, etc.).
   - Look for “Free trial”, “Developer sandbox”, or “Get started” and sign up.
   - Complete any onboarding steps and verify your email.

2. **Enable API access**
   - Once logged in, look for sections such as:
     - `Settings` → `API`, `Integrations`, or `Developers`
   - Turn on or request access to their REST API (some ATSs require approval).

3. **Generate an API key / token**
   - In the API/developer section, create a new API key or personal access token.
   - Give it a descriptive name (e.g. “serverless-ats-integration”).
   - Copy the token and store it in a password manager; you will **not** see it again.

4. **Find the API base URL**
   - In the ATS API docs, look for a base URL, often something like:
     - `https://api.<atsname>.com/v1`
     - or `https://<your-subdomain>.atsprovider.com/api`
   - Set this as `ATS_BASE_URL`.

5. **Configure environment variables**
   - Export them in your shell as shown in section 3.
   - Optionally, use a `.env` file and a tool like `direnv` or your IDE to load them.

6. **Map fields**
   - Use the ATS’s API reference to see exact job / candidate / application fields.
   - Update `map_job` and `map_application` in `ats_client.py` so the unified JSON your
     UI/consumers see is clean and consistent.

---

### 6. Running the Service Locally (serverless-offline)

#### 6.1. Prerequisites

- Node.js and npm installed (`node -v` / `npm -v`).
- Python 3.11 installed.
- AWS credentials configured (even for local offline, Serverless expects them):

```bash
aws configure
```

#### 6.2. Install dependencies

From the `ats_integration` directory:

```bash
npm install --save-dev serverless serverless-offline serverless-python-requirements
pip install -r requirements.txt
```

#### 6.3. Start the offline server

Make sure you’ve exported the environment variables (`ATS_BASE_URL`, `ATS_API_KEY`, etc.), then run:

```bash
npx serverless offline
```

By default, the HTTP endpoints will be available at something like:

- `http://localhost:3000/jobs`
- `http://localhost:3000/candidates`
- `http://localhost:3000/applications`

Check the console output from `serverless offline` for the exact URLs.

---

### 7. Deploying to AWS

With AWS credentials configured and environment variables set, deploy via:

```bash
npx serverless deploy
```

The command output will list the deployed HTTP endpoints (API Gateway URLs).

---

### 8. Example `curl` / Postman Calls

Assume your local URL from `serverless offline` is `http://localhost:3000`.

- **List jobs**

```bash
curl "http://localhost:3000/jobs?page=1&per_page=20"
```

- **Create candidate and attach to job**

```bash
curl -X POST "http://localhost:3000/candidates" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone": "+1-555-0100",
    "resume_url": "https://example.com/resumes/jane-doe.pdf",
    "job_id": "job_123"
  }'
```

- **List applications for a job**

```bash
curl "http://localhost:3000/applications?job_id=job_123&page=1&per_page=20"
```

You can import these into Postman by creating a new collection and adding three requests with the same URLs and payloads.

---

### 9. Summary

- Unified API for:
  - `GET /jobs`
  - `POST /candidates`
  - `GET /applications?job_id=...`
- All ATS-specific logic isolated in `ats_client.py`.
- Environment variables used for API base URL, token, and other secrets.
- Supports basic pagination and consistent JSON error responses.


