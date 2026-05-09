# Sprint 4 Task: Sovereign Query Expansion & Parallel Retrieval

## Overview

This document defines the strategy for the **Sovereign Query Builder**, a high-performance orchestration layer that translates the Triage Plan into concurrent queries across three distinct data domains: **Postgres** (Relational), **Qdrant** (Semantic), and **External APIs** (Real-time).

---

## 1. The Sovereign Query Builder (Intelligence Layer)

To achieve optimum results, we will use **google/gemma-3n-4b-it** to translate the Triage JSON into specific query dialects. This model provides the high reasoning depth required for SQL synthesis with significantly lower latency than 70B counterparts.

### Execution Plan

- **Input**: Triage JSON (`search_terms`, `constraints`, `signal_requirements`).
- **Output**: A "Universal Retrieval Payload" containing:
  - **SQL Query**: Optimized for Postgres indexing (e.g., `SELECT id FROM destinations WHERE budget_level = 'Luxury' AND safety_index > 0.8`).
  - **Vector Search Parameters**: Semantic terms and Qdrant-specific boolean filters.
  - **API Tooling Specs**: Specific locations and parameters for Weather/Events/Flights.

---

## 2. Parallel Dual-Tier Architecture

Instead of querying databases sequentially, the `ReasoningEngine` will execute a **Parallel Burst**:

```python
# Conceptual Implementation
async def execute_burst_retrieval(query_plan):
    results = await asyncio.gather(
        postgres_service.fetch_candidates(query_plan.sql),
        vector_service.search_by_vibe(query_plan.vector_params),
        signal_service.fetch_all_required(query_plan.signal_reqs)
    )
    return merge_context(results)
```

### Database Roles

- **Postgres**: Responsibility is **Hard Constraints**. It prunes the search space based on budget, safety, and physical location.
- **Qdrant**: Responsibility is **Soft Vibe**. It ranks the pruned candidates based on the "mood" of the traveler.

---

## 3. Intelligent Data Source Selection

The Query Builder will determine the "Information Density" required for each request:

- **Low Entropy Queries**: (e.g., "Paris in May") -> Minimal external calls, rely on cached historical data in Snowflake.
- **High Entropy Queries**: (e.g., "Where is it sunny right now near libraries?") -> Triggers real-time Weather and Google Places API calls.

---

## 4. Proposed Implementation Structure

### New Component: `services/query_builder.py`

- `class UniversalQueryBuilder`:
  - `synthesize_queries(triage_plan)`: The Llama 3 70B call.
  - `validate_query_safety()`: Sanitize generated SQL to prevent injection.

### Updated Component: `services/reasoning.py`

- Refactor `generate_recommendation` to use the `UniversalQueryBuilder`.
- Implement the `asyncio.gather` orchestration logic.

---

## 5. Optimum Results Matrix

| Scenario | Logic Path | Result |
| :--- | :--- | :--- |
| **Strict Budget** | Postgres-First | 100% adherence to financial limits. |
| **Vague Mood** | Qdrant-Heavy | High semantic alignment with "vibes". |
| **Urgent Travel** | API-Heavy | Validates flight availability and weather *before* suggesting. |

---
**Status**: Ready for Implementation of `services/query_builder.py`.
