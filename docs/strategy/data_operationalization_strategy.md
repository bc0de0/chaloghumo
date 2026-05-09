# Data Operationalization Strategy: Hybrid Retrieval & Context Fusion

## 1. Objective

To establish a production-grade data ecosystem that seamlessly integrates structured relational data, high-dimensional vectors, historical analytics, and real-time signals into the ChaloGhumo reasoning engine.

---

## 2. The Data Quadrant

### A. Postgres (Relational Metadata & Hard Constraints)

- **Role**: The "Ground Truth" for structured attributes.
- **Data Scope**:
  - Destination metadata (IATA codes, Coordinates).
  - Hard constraints (Budget levels, Safety indices, Climate categories).
- **Operational Pattern**: Used for initial candidate pruning via the Sovereign Query Builder's SQL generation.

### B. Qdrant (Semantic Vibes & High-Dimensional Search)

- **Role**: The "Intuition" layer.
- **Data Scope**:
  - 384-D embeddings of destination vibes.
  - Tag-based semantic clusters.
- **Operational Pattern**: HNSW-indexed vector search filtered by Postgres-derived candidate IDs.

### C. Snowflake (Historical Trends & Predictive Analytics)

- **Role**: The "Long-term Memory".
- **Data Scope**:
  - Historical destination popularity vs. mood.
  - Predictive crowd density and "vibe reliability" scores.
- **Operational Pattern**: Queried asynchronously during the retrieval burst to validate model-generated "hallucinations" against historical reality.

### D. External APIs (Real-time Localized Signals)

- **Role**: The "Immediate Reality".
- **Data Scope**:
  - **Weather (OpenWeather)**: Current and 7-day forecasts.
  - **Events (Ticketmaster/PredictHQ)**: Hyper-local festivals, concerts, and closures.
  - **Travel (Amadeus)**: Live flight availability and hotel pricing baseline.
- **Operational Pattern**: Triggered dynamically by the Triage Router to inject the "Now" into the synthesis engine.

---

## 3. Data Flow & Synchronization

### The Retrieval Pipeline (The "Flash Burst")

1. **Parallel Execution**: All four sources are queried simultaneously via `asyncio.gather`.
2. **Context Fusion**:
    - Relational data prunes the search space.
    - Vector data ranks the results.
    - Historical data validates the ranking.
    - Real-time data adds the final layer of feasibility.

### Data Refresh Pattern

- **Static Meta (Postgres/Qdrant)**: Refreshed monthly via the `scripts/seed.py` pipeline.
- **Historical (Snowflake)**: Weekly ETL from application logs and external travel trend datasets.
- **Real-time (APIs)**: Cached in Redis with aggressive TTLs (1-6 hours) to mitigate API costs and latency.

---

## 4. Operational Excellence

### Reliability & Error Handling

- **Graceful Degradation**: If an external API is down, the system falls back to historical Snowflake averages or cached Redis values.
- **Observability**: Every "Flash Burst" is logged with detailed latency metrics for each source.
- **Security**: Strict IAM roles control access to Snowflake stages and S3 buckets.

---
**Status**: Data Operationalization Strategy Finalized.
