# Snowflake Optimization & ETL Strategy: The Analytical Memory Layer

## 1. Objective

To transform Snowflake from a passive data warehouse into an active "Predictive Memory" layer that validates traveler "vibes" against historical travel trends, seasonality, and global event patterns.

---

## 2. External Data Sourcing Strategy

To build a high-fidelity reasoning engine, we must ingest data that provides historical depth.

### Primary Data Sources

- **OpenTravelData (OPTD)**: [GitHub - opentraveldata/opentraveldata](https://github.com/opentraveldata/opentraveldata)
  - *Utility*: IATA/ICAO mappings, airline routes, and city population dynamics.
- **UNWTO Global Tourism Data**: [UN Tourism Data Portal](https://www.unwto.org/tourism-data-portal)
  - *Utility*: Historical arrival trends and economic tourism impact.
- **Google Trends (via PyTrends)**: [Kaggle: Travel Trends Dataset](https://www.kaggle.com/datasets/google/google-trends-travel)
  - *Utility*: Seasonal "vibe" popularity (e.g., "When does 'Dark Academia' trend in Edinburgh?").
- **PredictHQ / Ticketmaster Archives**:
  - *Utility*: Historical event density for calculating "Vibe Stability" scores.

---

## 3. Snowflake ETL Architecture (The Pulse)

We will implement a **Medallion Architecture** within Snowflake to ensure data quality and speed.

### A. Ingestion (Bronze Layer)

- **Snowpipe**: Automated ingestion from AWS S3/Azure Blob stages where localized API signals (Weather, Events) are dumped as raw JSON.
- **GitHub Gist Integration**: Using Snowflake External Tables to pull in curated metadata lists stored in public Gists.

### B. Transformation (Silver Layer)

- **Dynamic Tasks**: Scheduled SQL/Python tasks that normalize raw JSON into structured travel signals.
- **Vibe Encoding**: Mapping semantic search terms from our logs back to successful destination matches to "train" the historical weights.

### C. Analytical (Gold Layer)

- **Materialized Views**: Pre-calculated views for "Seasonality Scores" and "Safety Trends" per IATA code to ensure sub-200ms retrieval.

---

## 4. Analytical Metrics for Reasoning Enhancement

The `ReasoningEngine` will query Snowflake for the following metrics to justify its choices:

1. **Vibe Stability Index (VSI)**:
   - *Formula*: Historical Event Density / Seasonal Variance.
   - *Utility*: "Is Edinburgh actually 'Dark Academia' in November, or is it just rainy and closed?"
2. **Seasonality Alignment Score (SAS)**:
   - *Formula*: Correlation between User Mood and Historical Arrival Peaks.
   - *Utility*: Prevents suggesting tropical beaches during monsoon seasons.
3. **Trend Momentum**:
   - *Formula*: 30-day delta in Google Search volume for a specific destination tag.

---

## 5. Optimization & Performance

### Warehouse Management

- **Multi-Cluster Warehouses**: Set to `Auto-scale` (X-Small) to handle concurrent bursts from multiple `ReasoningEngine` instances without queuing.
- **Result Caching**: Leverage Snowflake's metadata cache to avoid re-computing identical seasonality lookups.

### Query Strategy

- **Search Optimization Service (SOS)**: Enabled for the `iata_code` and `tag` columns to accelerate point lookups during the "Parallel Burst" retrieval phase.

---

## 6. Security & Governance

### Access Control & Privacy

- **Role-Based Access (RBAC)**:
  - `CHALOGHUMO_ETL_ROLE`: Write access to Bronze/Silver.
  - `CHALOGHUMO_REASONER_ROLE`: Read-only access to Gold (Materialized Views).
- **Data Anonymization**: Using Snowflake's **Dynamic Data Masking** on any user-identifiable constraints before storage.

---
**Status**: Strategy Defined.
**Next Step**: Implementation of `snowflake_service.py` using the `snowflake-connector-python`.
