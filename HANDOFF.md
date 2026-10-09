# AI Agent Project Handoff: FinSentinel (Finsight_CAD)

## 1. Project Overview & Scope
**Project Name:** FinSentinel  
**Type:** Autonomous Financial Risk Platform  
**Scope & Goal:**  
FinSentinel is an autonomous financial risk platform. The current state represents the **foundation layer**. The core project structure, data contracts, database models, and the event-driven wiring are complete. However, deep **business logic** is yet to be fully implemented. The new AI agent is expected to build upon this solid foundation to implement the core business rules and connect the frontend React dashboard with the live FastAPI backend.

## 2. Technical Stack
* **Backend:** Python, FastAPI (uvicorn), ARQ (background workers), SQLAlchemy (Alembic for migrations)
* **Databases:** PostgreSQL 16 (Relational data), Redis 5.0+ (Event Bus, Caching, ARQ workers)
* **Frontend:** React (Vite/TypeScript) located in the `dashboard/` directory
* **Testing:** Pytest (integration and unit tests)

## 3. What is Done
* **Event-Driven Architecture:** A real event bus powered by Redis Streams carries ingestion through the full pipeline (`financial_event` → `state_changed` → `snapshot_updated` → `risk_assessed` → `risk_assessed_complete`).
* **Idempotency & Concurrency:** Robust idempotency handling under genuine concurrency (tested up to 50 concurrent requests against PostgreSQL). Redis Stream redeliveries are correctly handled as no-ops.
* **Simulation Engine:** A real Monte Carlo collision detection engine is built to find genuine superadditive risk. Simulation compute is highly optimized (p50=3.5ms).
* **API Routers & Modules:** 17 core FastAPI routers are initialized, covering ingestion, risk, simulation, threat, decision, confidence, twin, and auth.
* **Resilience:** The application features graceful degradation. It functions completely without an LLM (using regex templates as fallbacks).
* **Load & Shadow Testing:** Foundation metrics are measured. System handles sustained publishing (~2 events/sec) with zero consumer lag. Shadow-mode precision measurement mechanics are in place.
* **Dashboard Foundation:** React dashboard skeleton is built with key pages like `Overview`, `SystemHealth`, `AuditTrail`, `ThreatIntelligence`, `Reconciliation`, and `Compliance`.

## 4. What is To Be Done (Objectives)
* **Business Logic Implementation:** The foundation is laid, but the specific business rules within modules (risk thresholds, threat heuristics, twin decision logic) need to be fleshed out.
* **Dashboard Integration:** Wire up the React dashboard pages (`src/pages/*.tsx`) to consume the live FastAPI endpoints. Add rich visualizations to display risk metrics and system health.
* **LLM Integration Expansion:** While graceful degradation is implemented, real LLM integration needs to be connected and expanded for complex, free-text financial event extraction.
* **Precision Maturation:** Allow the shadow-mode decision engine to run live for a longer horizon (7–90 days) to accurately calculate precision and false-alarm rates on predictions.
* **Load Test Optimization:** Address the 30-second timeout bottleneck observed during high-burst ingestion tests by implementing a longer polling window or event-driven completion detection.

## 5. Non-Standard Conventions & Constraints (CRITICAL)

The new AI must strictly adhere to the following architecture rules:

### 1. The Module Boundary Rule
Each package under `app/modules/` (e.g., ingestion, confidence, twin, simulation, risk, threat, decision, org, explain) **owns its own internals**. 
* **Rule:** A module must **never** import from another module's internals (e.g., `app.modules.risk` cannot import directly from `app.modules.threat`). 
* **Data Sharing:** If two modules need to share data, they must use frozen Pydantic contracts located in `app.contracts`. 
* **Shared Foundation:** Modules may import freely from `app.contracts` and `app.platform`.

### 2. Immutable Data Contracts
`app.contracts` holds frozen Pydantic event and state contracts. These are the schemas that flow between modules and across the wire. 
* **Rule:** `app.contracts` classes are **never edited in place once shipped**. Any changes or updates must result in a **new versioned class**.

### 3. Event-Driven Workflow
Avoid synchronous inter-module API calls. The architecture relies on an ARQ worker process (`app.platform.worker`) processing jobs off Redis streams. State transitions should emit events that downstream consumers pick up autonomously.

## 6. Setup & Execution Reference
* **Backend:** 
  * `docker compose up -d` (PostgreSQL + Redis)
  * `alembic upgrade head` (Migrations)
  * `uvicorn app.main:app --reload` (FastAPI Server)
  * ARQ Worker execution required for event processing.
* **Testing:** `pytest` (Focus on `tests/integration/` for full-system tests).

## 7. Timeline Summary
* **Phase 1 (Completed):** Core infrastructure, database schema, event bus wiring, baseline metrics, API routing, dashboard scaffolding.
* **Phase 2 (Immediate Next):** Implementing module-specific business rules, integrating dashboard with backend APIs.
* **Phase 3 (Future):** Long-term metrics gathering, LLM expansion, and scaling optimizations.
