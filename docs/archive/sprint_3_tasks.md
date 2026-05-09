# Sprint 3: Infrastructure Hardening, Security & Deep Intelligence

## Overview

Sprint 3 focus shifts to **Production Readiness** and **Response Depth**. We will stabilize the Docker-first infrastructure, implement a rigorous CI/CD pipeline, and establish strict security trust boundaries. Crucially, we will deepen the recommendation intelligence by integrating **Travel Availability** (flights/hotels) and **Hyper-local Events** to provide actionable, real-world travel synthesis.

## 1. Infrastructure & Code Quality (CI/CD)

- [x] **Docker-First Reversion**: Revert all `.venv` local-first hacks (SQLite, fakeredis, Qdrant-Local) and restore full connectivity to Docker-based Postgres, Qdrant, and Redis.
- [x] **Rigorous Linting & Formatting**: Integrate `ruff` and `mypy` for strict type safety and code quality enforcement.
- [x] **Unit & E2E Testing Suite**: Implement a comprehensive test suite using `pytest` and `httpx`:
  - Unit tests for `ReasoningEngine` logic.
  - Integration tests for Qdrant and Redis connectivity.
  - E2E tests for the full `/recommendations` flow.
- [x] **CI Pipeline Definition**: Create a GitHub Action or local script to automate the test suite, linting, and Docker build verification.

## 2. Deep Intelligence & Signal Integration

- [x] **Travel Availability Synthesis**:
  - Integrate Amadeus/Skyscanner API stubs to check real-time flight feasibility for recommended destinations.
  - Add "Estimated Trip Cost" calculation based on current airfare and hotel baseline data.
- [x] **Hyper-local Event Discovery**:
  - Connect the `signals` service to real-time event feeds (e.g., Ticketmaster or PredictHQ stubs).
  - Enhance the `ReasoningChain` to mention specific events matching the user's mood/preferences.
- [x] **Database Optimization & Seeding**:
  - Implement partitioned seeding for 10k+ destinations in Qdrant and Postgres.
  - Optimize HNSW indexing for high-concurrency vector search.

## 3. Trust Boundaries & Security

- [x] **Input Sanitization & Abuse Prevention**:
  - Strict Pydantic V2 validation for all incoming requests.
  - Implement Redis-based rate limiting to prevent LLM/Vector DB exploitation.
  - **Prompt Injection Detection**: Filter input for adversarial jailbreak patterns.
- [x] **Trust Boundary Enforcement**:
  - Secure API key management (Docker Secrets / Environment masking).
  - Sanitize AI-generated narratives to prevent prompt injection or "hallucinated" safety warnings.
  - **Secure File Handling**: Implement strict MIME/Size/Filename validation for future uploads.

## 4. Enhanced User Personalization

- [ ] **Historical Contextualization**: Implement a `UserHistory` store in Postgres to allow the engine to learn from past "Vibe matches".
- [ ] **Context Snapshots**: Ensure each recommendation includes a verifiable snapshot of the environmental and societal signals used for the decision.

## Critical Success Criteria (Sprint 4 Gateway)

- [ ] **Zero-Fail CI**: All tests (Unit + E2E) pass consistently within the Docker environment.
- [ ] **Actionable Recommendations**: 100% of successful API responses must include at least one real-world event or flight feasibility signal.
- [ ] **Validated Trust Boundary**: No unvalidated input reaches the core `ReasoningEngine`.
- [ ] **Scalable Seeding**: The database can be wiped and re-seeded with 1000+ cities in under 2 minutes.
