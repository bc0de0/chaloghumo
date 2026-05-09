# Strategic Blueprint: Triage Routing & Hybrid Retrieval

This document outlines the architectural strategy for the **ChaloGhumo Triage Router** and the **Hybrid Retrieval** engine in Sprint 4. The goal is to transition from a linear search to a dynamic, intelligence-first orchestration layer.

## 1. The Triage Router: The "Analyst" (Qwen-2 1.5B)

The Router serves as the entry point for all reasoning requests. It performs high-dimensional analysis on the user's mood and persona before any retrieval occurs.

### Logic Flow

1. **Query Expansion**: Qwen-2 converts abstract moods (e.g., "Dark academia vibes") into 3-5 specific semantic keywords for Qdrant.
2. **Constraint Extraction**: Identifies explicit and implicit filters (e.g., "Must be under $2000", "Avoid tropical humidity").
3. **Tool Selection (Gatekeeping)**: Determines which signal clusters are required:
    - **Environmental**: Weather, AQI.
    - **Societal**: Events, Safety, Local News.
    - **Historical**: Snowflake trend validation.

### Router Implementation Strategy

- **Prompt Architecture**: Uses a strict JSON schema output to ensure the `ReasoningEngine` can parse decisions programmatically.
- **Model**: `arize-ai/qwen-2-1.5b-instruct` (via Together AI). Selected for its ultra-low latency and efficient instruction following.

---

## 2. Embedding Model Selection

We must balance **semantic depth** with **TTFT (Time To First Token)**.

### Option A: Remote (Together AI)

- **Model**: `togethercomputer/m2-bert-80M-8k-retrieval`
- **Pros**: Higher dimensionality, unified provider.
- **Cons**: Network latency (+150-300ms per request).

### Option B: Local (SentenceTransformers) - **RECOMMENDED**

- **Model**: `all-MiniLM-L6-v2` or `BGE-Small-EN-v1.5`
- **Pros**: Sub-20ms latency, zero API cost, works offline.
- **Cons**: Limited context window (512 tokens).

**Strategic Choice**: We will stick with **Local Embeddings (all-MiniLM-L6-v2)** to keep the sub-2s latency goal achievable, as the Router's expanded query will fit well within the 512-token limit.

---

## 3. Tool Chain Orchestration: Qdrant vs. External Signals

The Router will dynamically construct the tool chain for each request.

### Primary Tool Chain

1. **Vector Layer (Qdrant)**:
    - Performs the initial "Vibe Match" search.
    - Returns Top-10 candidates.
2. **Predictive Layer (Snowflake)**:
    - **Historical Validation**: Checks if the Top candidates align with historical trends for the specific mood.
    - **Persona Filtering**: Cross-references with user persona history.
3. **Signal Layer (Live APIs)**:
    - **Real-time Filter**: Only invoked if the Router marks `weather: true` or `events: true`.
    - Prevents wasting API credits and reducing latency on simple queries.

---

## 4. Latency Mitigation Tactics

- **Parallel Execution**: Retrieval from Qdrant and Snowflake will happen concurrently with Signal fetching.
- **Prefetching**: Persona trends can be prefetched from Snowflake during the Router's "Thinking" phase.
- **Streaming Triage**: The system will start fetching vector results as soon as the Router outputs the first semantic term (if using streaming output for the router).

---

## 5. Success Metrics

- **Triage Accuracy**: >90% (Manual audit of query expansion quality).
- **Latency**: Triage phase < 400ms.
- **Hybrid Depth**: 100% of recommendations must include at least one signal-based justification.

---
**Next Step**: Implementation of `TriageRouter` in `services/reasoning.py`.
