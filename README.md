# ATS Integration Microservice

A serverless Python microservice that integrates with the [Recruitee ATS API](https://docs.recruitee.com/reference) and exposes a clean, unified REST API for managing **jobs**, **candidates**, and **applications**.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Getting Started with Recruitee](#getting-started-with-recruitee)
3. [Local Setup](#local-setup)
4. [Running Locally with Serverless Offline](#running-locally-with-serverless-offline)
5. [API Reference & Examples](#api-reference--examples)
6. [Deploying to AWS](#deploying-to-aws)
7. [Environment Variables](#environment-variables)

---

## Project Structure

```
ats/
├── src/
│   ├── config/
│   │   └── settings.py          # Loads env vars (RECRUITEE_API_KEY, etc.)
│   ├── handlers/
│   │   ├── jobs_handler.py       # GET /jobs
│   │   ├── candidates_handler.py # POST /candidates
│   │   └── applications_handler.py # GET /applications
│   ├── services/
│   │   └── recruitee_service.py  # All Recruitee API calls + pagination
│   └── utils/
│       ├── response_helper.py    # Standardized JSON responses for API Gateway
│       └── error_handler.py      # Error decorator + request parsers
├── serverless.yml                # Serverless Framework configuration
├── requirements.txt              # Python dependencies
├── .env                          # Local environment variables (do not commit)
└── README.md
```

---

## Getting Started with Recruitee

### Step 1 — Create a Recruitee Account

1. Visit [https://recruitee.com](https://recruitee.com) and click **Start free trial**.
2. Fill in your company name and personal details, then verify your email.
3. You'll land on your Recruitee Dashboard.

### Step 2 — Find Your Numeric Company ID

1. Make a `GET` request to `https://api.recruitee.com/c/your_company_slug/offers` in your browser.
2. In the JSON response, look at the first offer and copy the **integer** value of `"company_id"`.
   - Example ID: `12345`
   - This means your `RECRUITEE_BASE_URL` = `https://api.recruitee.com/c/12345`
   - **Note:** `POST` candidate API endpoints only accept the numeric ID, not the string slug.

### Step 3 — Generate an API Key

1. In the dashboard, go to **Settings → Apps & Integrations → API Tokens**.
2. Click **New Token**, give it a name (e.g. `ats-microservice`), and set the scope to **Full Access**.
3. Copy the generated token — this is your `RECRUITEE_API_KEY`.

> ⚠️ The token is shown only once. Store it in your `.env` file immediately.

---

## Local Setup

### Prerequisites

| Tool | Version |
|---|---|
| Python | ≥ 3.11 |
| Node.js | ≥ 18 |
| npm | ≥ 9 |
| Serverless Framework | v3 |

### Install Steps

```bash
# 1. Clone or navigate to the project
cd c:\ats

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Serverless Framework globally (if not already installed)
npm install -g serverless@3

# 4. Install Serverless plugins
npm install

# 5. Configure environment variables
#    Copy the .env template and fill in your credentials
copy .env .env.local
# Then open .env and replace the placeholder values:
#   RECRUITEE_API_KEY=your_actual_api_key
#   RECRUITEE_BASE_URL=https://api.recruitee.com/c/your_company_slug
```

### package.json (auto-installed by npm install)

The project's `package.json` declares the two required Serverless plugins:

```json
{
  "devDependencies": {
    "serverless-offline": "^13.3.3",
    "serverless-python-requirements": "^6.1.0"
  }
}
```

---

## Running Locally with Serverless Offline

```bash
serverless offline
```

The local server starts at **http://localhost:3000**. You should see output like:

```
Starting Offline at stage dev (us-east-1)

Routes:
  GET  http://localhost:3000/jobs
  POST http://localhost:3000/candidates
  GET  http://localhost:3000/applications
```

---

## API Reference & Examples

### `GET /jobs` — List all job openings

Fetches all job offers from your Recruitee account.

**Response schema:**
```json
[
  {
    "id": "string",
    "title": "string",
    "location": "string",
    "status": "OPEN | CLOSED | DRAFT",
    "external_url": "string"
  }
]
```

**curl example:**
```bash
curl -X GET http://localhost:3000/jobs
```

**Postman:**
- Method: `GET`
- URL: `http://localhost:3000/jobs`
- Body: none

---

### `POST /candidates` — Create a candidate and apply to a job

Creates a new candidate profile in Recruitee and attaches them to a job as an applicant.

**Request body:**
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "phone": "+1-555-0100",
  "resume_url": "https://example.com/resume/jane-doe.pdf",
  "job_id": "123456"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✅ | Candidate's full name |
| `email` | string | ✅ | Candidate's email address |
| `phone` | string | ❌ | Candidate's phone number |
| `resume_url` | string | ❌ | Link to the candidate's CV |
| `job_id` | string | ✅ | Recruitee offer ID (from `GET /jobs`) |

**Response (201 Created):**
```json
{
  "candidate_id": "789",
  "candidacy_id": "101112",
  "message": "Candidate created and attached to job successfully."
}
```

**curl example:**
```bash
curl -X POST http://localhost:3000/candidates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone": "+1-555-0100",
    "resume_url": "https://example.com/resume.pdf",
    "job_id": "123456"
  }'
```

---

### `GET /applications?job_id=<id>` — List applications for a job

Fetches all candidates who have applied to a specific job.

**Query Parameters:**

| Parameter | Required | Description |
|---|---|---|
| `job_id` | ✅ | Recruitee offer ID |

**Response schema:**
```json
[
  {
    "id": "string",
    "candidate_name": "string",
    "email": "string",
    "status": "APPLIED | SCREENING | REJECTED | HIRED"
  }
]
```

**curl example:**
```bash
curl -X GET "http://localhost:3000/applications?job_id=123456"
```

**Postman:**
- Method: `GET`
- URL: `http://localhost:3000/applications`
- Params: `job_id = 123456`

---

## Error Responses

All errors return a consistent JSON structure:

```json
{
  "error": "Human-readable error message",
  "details": "Optional extra detail from upstream API"
}
```

| HTTP Code | Meaning |
|---|---|
| 400 | Bad request / missing/invalid fields |
| 403 | Invalid or missing API key |
| 404 | Job or resource not found |
| 500 | Unexpected internal server error |

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `RECRUITEE_API_KEY` | Bearer token for Recruitee API authentication | `eyJhbGci...` |
| `RECRUITEE_BASE_URL` | Recruitee base URL with numeric company ID | `https://api.recruitee.com/c/12345` |
