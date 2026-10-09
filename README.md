# FinSentinel

Autonomous financial risk platform. This is the foundation layer: project
structure, contracts, data models, and wiring — no business logic yet.

## Setup

1. Create a virtual environment and install dependencies:

   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in real values (at minimum,
   `POSTGRES_PASSWORD` and `JWT_SECRET`).

3. Start Postgres and Redis:

   ```
   docker compose up -d
   ```

4. Apply database migrations:

   ```
   alembic upgrade head
   ```

## Running

```
uvicorn app.main:app --reload
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- DB health check: http://localhost:8000/health/db

## Testing

```
pytest
```

## Module boundary rule

Each package under `app/modules/` (ingestion, confidence, twin, simulation,
risk, threat, decision, org, explain) owns its own internals. A module may
import from `app.contracts` and `app.platform` freely — those are the shared
foundation. A module must **never** import from another module's internals
(e.g. `app.modules.risk` importing something from inside
`app.modules.threat`). If two modules need to share data, that data crosses
through a contract in `app.contracts`, not through a direct import.

`app.contracts` holds frozen Pydantic event/state contracts — the schemas
that flow between modules and across the wire. `app.contracts` classes are
never edited in place once shipped; changes go into a new versioned class.
