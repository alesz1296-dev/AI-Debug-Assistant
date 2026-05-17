# Enterprise AI Debug Assistant

Production-minded AI Engineering portfolio project built with Spec-Driven Development.

This assistant investigates public or synthetic operational incidents by combining:

- public log datasets such as Loghub-style logs,
- public incident postmortem summaries,
- public technical documentation,
- deterministic local retrieval for development and tests,
- a future-ready boundary for PostgreSQL + pgvector, workers, observability, and deployment.

No company data belongs in this repository.

## What It Demonstrates

- FastAPI service design
- RAG ingestion and retrieval
- grounded answers with citations
- synthetic benchmark cases
- evaluation harnesses
- production data-safety rules
- observability and security scaffolding
- private learning notes excluded from Git

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir apps/api --reload
```

Then open:

- `GET http://127.0.0.1:8000/api/v1/health`
- `POST http://127.0.0.1:8000/api/v1/query`

For local protected routes, use:

```text
X-API-Key: dev-local-key
```

## Example Query

```json
{
  "question": "The API is timing out and workers are backing up after a deploy. What should I check?",
  "collections": ["incident_cases", "system_logs", "knowledge_base"],
  "top_k": 5
}
```

## Data Policy

Allowed:

- public datasets,
- public incident reports,
- public documentation,
- synthetic incidents,
- logs from local demo applications.

Forbidden:

- company logs,
- private stack traces,
- customer data,
- copied internal runbooks,
- secrets or tokens.

See [docs/data-policy.md](docs/data-policy.md).

