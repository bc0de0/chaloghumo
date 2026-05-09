# The RAG Agentic System Playbook

## A Generalised Guide to Conceptualising, Designing, Architecting, and Implementing Complex RAG-Based Agentic Workflows

> Derived from the lived engineering experience of building ChaloGhumo — a multi-signal, multi-model travel intelligence engine — across four production sprints.

---

## How to Use This Document

This playbook is **sequential but not rigid**. Phases 0–3 are strictly ordered — skipping them produces systems that are technically correct but semantically incoherent. Phases 4–9 can be interleaved based on team size and risk tolerance. The document ends with a meta-section on the decisions that compound over time and are hardest to reverse.

Every section distinguishes between:

- **What to do** — the concrete action
- **Why it matters** — the first-principles reasoning
- **The trap** — what commonly goes wrong here

---

## Phase 0 — Epistemic Grounding: Before You Write a Line of Code

This phase has no code output. Its output is a set of documents that govern every technical decision that follows. Skipping it is the single most common cause of RAG systems that work mechanically but produce poor or incoherent recommendations.

### 0.1 Define the Nature of the Problem Space

Before touching architecture, answer this question in writing:

> *What is the precise nature of the "understanding" this system needs to perform, and why is a retrieval-augmented approach the right model for it?*

A RAG system is appropriate when:

- The answer requires combining **stable stored knowledge** (a vector/relational corpus) with **dynamic context** (signals, user state, live data)
- The answer cannot be fully encoded in model weights because it depends on **facts that change** faster than retraining cycles
- The answer must be **explainable** — the system must surface *why* it concluded what it did

If any of these are absent, reconsider whether RAG is the right tool.

**The trap:** Teams reach for RAG because it is fashionable. If the problem is a simple classification or a static Q&A over a fixed corpus, a fine-tuned model or a keyword search with an LLM wrapper will outperform a full RAG pipeline at a fraction of the operational cost.

### 0.2 Write Your Epistemic Foundations Document

This is your system's constitution. It defines:

#### A. The Domain Model in Natural Language

Describe the "world" your system reasons over. Identify:

- What are the primary *domains* of information? (e.g., in a travel system: Personal, Environmental, Societal)
- What is the *certainty class* of each domain? (Hard facts vs. probabilistic signals vs. subjective input)
- What are the *invariants* — rules that must never be violated regardless of model output?

#### B. The Reasoning Axioms

State the logical rules your system must follow. These become the guardrails for prompt engineering and the basis for fallback logic. Examples:

- "A recommendation is invalid if it contradicts a hard constraint, regardless of semantic similarity score"
- "Environmental safety signals take precedence over preference alignment"
- "High match scores on stale data are worse than lower scores on fresh data"

#### C. Entropy and Decay Policy

If your system uses real-time or time-sensitive data, define:

- Which signals decay (and at what rate)
- What action the system takes when signal confidence drops below a threshold: refresh, fuzzy-weight, or suppress
- What constitutes a "stale" vs. "valid" system state

**Why this matters:** Every prompt you write, every retrieval filter you design, and every scoring function you build will be an expression of these axioms. Writing them first means you are building toward a coherent system rather than reverse-engineering coherence from working code.

### 0.3 Write Your System Ontology

The ontology is the formal data model of your domain expressed as *named primitives*. It precedes the database schema, the API schema, and the LLM prompt design.

For each entity in your system, define:

```yaml
Entity: <Name>
Fields:
  - <field_name>: <type> | <enum_values> — <description>
Certainty class: [Hard | Probabilistic | Subjective]
Source of truth: [Relational DB | Vector DB | Live API | User Input]
Update frequency: [Static | Hourly | Real-time]
```

**Critical rule:** Your database schema must be a direct mechanical translation of this ontology. If a field exists in your DB schema that does not trace back to a named primitive in your ontology, it should not be there. If an ontology primitive has no DB representation, you have a gap.

**The trap:** Defining the ontology *after* designing the database. This produces schemas that are technically normalised but semantically incorrect — the system stores data correctly but reasons about it wrongly.

---

## Phase 1 — System Architecture Design

### 1.1 Map Your Data Flow Before Your Service Boundaries

Draw the data flow *first*, service boundaries *second*. The shape of your architecture should emerge from how data needs to move, not from the services you think you need.

A generalised RAG agentic data flow has this shape:

```text
[User Intent / Input]
        │
        ▼
[Intent Understanding Layer]     ← Small, fast model; structured output
        │ Query expansion, constraint extraction, tool selection
        ▼
[Query Synthesis Layer]          ← Translates intent into DB-specific queries
        │ SQL, vector filter specs, API call specs
        ▼
[Parallel Retrieval Layer]       ← asyncio.gather() — all sources simultaneously
        ├── Relational DB (hard constraints, metadata)
        ├── Vector DB (semantic similarity)
        ├── Signal Cache (recent live data)
        └── Analytics/Historical (trend validation)
        │
        ▼
[Merge & Rank Layer]             ← Intersection logic, score normalisation
        │
        ▼
[Synthesis Layer]                ← Large, capable model; natural language output
        │ Reasoning chain, narrative, explanation
        ▼
[Structured Response]
```

**Key insight:** The parallel retrieval layer is where most of your latency budget is spent. The architecture must ensure that *all* retrieval sources are hit concurrently, not sequentially. Sequential retrieval is the most common cause of slow RAG systems.

### 1.2 Select Your Storage Primitives Based on Data Characteristics

Match each domain of your ontology to the storage type that fits its access pattern:

| Data Characteristic | Right Storage | Wrong Storage |
| ------------------- | ------------- | ------------- |
| Stable metadata, hard constraints, relationships | Relational DB (Postgres) | Vector DB |
| Subjective descriptions, semantic similarity queries | Vector DB (Qdrant) | Relational DB |
| High-velocity signals, TTL-based decay | Cache (Redis) | Any persistent DB |
| Historical aggregates, trend analysis | Analytical warehouse (Snowflake/BigQuery) | Operational DB |
| Event streams, high-throughput async ingestion | Message broker (Kafka) | Synchronous API |

**The trap:** Using a single database for everything because it is simpler. This seems correct early and becomes a severe constraint at scale. The dual-DB pattern (relational + vector) in particular is non-negotiable for any system that needs both hard constraint filtering and semantic search — trying to do semantic search in Postgres with pgvector while using the same table for constraint filtering works at small scale but becomes a query planning nightmare at production volumes.

### 1.3 Choose Your Model Architecture

For a production RAG pipeline, avoid using a single large model for all tasks. The cost and latency profile of a 70B model makes it unsuitable for the intermediate analytical steps.

**The Multi-Model Pattern:**

```text
Stage             Model Size    Characteristics Needed
──────────────────────────────────────────────────────
Intent Triage     1–4B          Fast, cheap, structured JSON output
Query Building    4–8B          Instruction-following, DB syntax awareness
Final Synthesis   30–70B        Fluent, contextual, reasoning depth
```

Design each model's interface as a strict structured output contract (JSON schema). The model is a function: given a prompt, return a parseable JSON object. Treat model calls as I/O with the same error handling discipline you would apply to a database call.

**Framework decision — direct orchestration vs. abstraction layer (LangChain, LlamaIndex, etc.):**

Use a framework when:

- You are prototyping and need to move fast
- Your pipeline is a standard chain (retrieve → augment → generate) without complex branching
- Your team lacks deep async Python expertise

Use direct orchestration when:

- You need sub-2s end-to-end latency (framework abstraction adds 100–400ms)
- Your pipeline has complex parallel branches
- You need sovereign control over every token in every prompt
- You need transparent, debuggable execution traces

For production systems with custom retrieval logic, direct `asyncio`-based orchestration consistently outperforms framework-based approaches on latency and gives you full observability into what the system is actually doing.

---

## Phase 2 — Data Layer Implementation

Implement in this exact order. Each step validates the previous.

### Step 1: Implement the Relational Schema from the Ontology

Translate each ontology entity directly into a SQLAlchemy model. Rules:

- UUID primary keys (prevents enumeration, works across distributed inserts)
- JSONB (not JSON) for semi-structured fields that need to be queried
- Enums defined in Postgres (not just Python) for domain-constrained fields
- `created_at` with `server_default=func.now()`, `updated_at` with `onupdate` trigger
- Indexes on every field that will appear in a WHERE or JOIN clause

Commit every schema change via Alembic. The discipline of writing migrations from day one pays compounding dividends — it means your schema history is a complete record of how your domain understanding evolved, and it gives you safe rollback paths at every step.

**Never use `Base.metadata.create_all()` in production code.** It bypasses the migration record and creates divergence between environments.

### Step 2: Implement the Vector Collection

Before creating the collection, decide:

**Embedding model selection:**

| Dimension | Speed | Semantic Depth | Recommendation |
| --------- | ----- | -------------- | -------------- |
| 384 (all-MiniLM-L6-v2) | <20ms local | Sufficient for short descriptions | Default choice |
| 768 (all-mpnet-base-v2) | ~40ms local | Better for longer, nuanced text | When query text is rich |
| 1536 (OpenAI text-embedding-3-small) | ~150ms API | Very high | When quality > cost |

The embedding model dimension must match the collection configuration and can never be changed without re-indexing the entire corpus. Make this decision consciously before seeding.

**HNSW index configuration:**

```python
hnsw_config = HnswConfigDiff(
    m=32,              # connections per node — higher = better recall, more RAM
    ef_construct=128,  # index build quality — higher = better index, slower build
)
```

`m=16, ef_construct=100` is the default and fine for development. For production with >100k vectors and high recall requirements, `m=32, ef_construct=200` is a better starting point.

**Payload schema:** Define a Pydantic model that every vector payload must conform to. Validate before every upsert. This is the equivalent of a DB schema constraint for your vector store — without it, payload drift makes filtering unreliable.

### Step 3: Implement the Signal Cache Layer

Design your Redis key namespace before writing any code:

```text
signal:{type}:{entity_id}     → cached signal data
rate_limit:{ip}               → request counter
session:{session_id}          → in-flight reasoning state
blacklist:token:{jti}         → revoked JWT tokens
```

Assign TTLs at the key level, not as a global policy. Signal data should expire by its decay rate. Rate limit counters need short TTLs matching the rate window. Session state should outlive the longest possible reasoning chain.

### Step 4: Seed with Intent, Not Volume

The purpose of development seeding is to validate that your retrieval logic works, not to achieve statistical coverage. Seed the minimum number of records that exercise all your retrieval paths:

- At least one record matching each enum value in your ontology
- Records with edge-case field values (null optionals, max budget, extreme coordinates)
- Records that should and should not match a given test query

For production seeding from external datasets, isolate it as a Docker entrypoint job (not a startup dependency) with a configurable row limit and a completion signal that downstream services can wait on.

---

## Phase 3 — Service Layer: The "Definition Before Implementation" Principle

This is one of the most important lessons from complex agentic systems: **write the interface completely before you write the implementation.**

### 3.1 Define Services as Contracts First

For each service, write the full interface — all method signatures with complete type annotations, docstrings stating preconditions and postconditions, and stub implementations that return typed mock data. Do not write business logic yet.

```python
class ReasoningEngine:
    async def generate_recommendation(
        self,
        persona: UserPersona
    ) -> RecommendationResult:
        """
        Orchestrates the full RAG pipeline for a single user request.

        Preconditions:
            - persona.preferences must be non-empty
            - At least one destination must exist in the vector store

        Postconditions:
            - Returns a RecommendationResult with a non-empty reasoning_chain
            - match_score is in range [0.0, 1.0]
            - context_snapshot contains the state at time of generation (for audit)

        Raises:
            NoMatchFoundError: if pruning eliminates all candidates
            SignalUnavailableError: if required signals cannot be fetched within timeout
        """
        raise NotImplementedError
```

This forces you to make every dependency explicit, every error case named, and every data contract typed *before* the complexity of implementation obscures these decisions.

### 3.2 The Service Dependency Graph

Map your services into a directed acyclic graph:

```text
ReasoningEngine
    ├── TriageRouter (→ LLMService with small model)
    ├── QueryBuilder (→ LLMService with mid model)
    ├── VectorService (→ Qdrant)
    ├── PostgresService (→ SQLAlchemy)
    ├── SignalService (→ Redis → external APIs)
    └── AnalyticsService (→ Snowflake)
```

**Rules for this graph:**

- Services at the bottom of the graph (leaf nodes) should have no knowledge of services above them
- Only the top-level orchestrator (`ReasoningEngine`) should know about all services
- Services should never call each other laterally — all coordination flows through the orchestrator

### 3.3 LLM-as-a-Function Pattern

Every LLM call in your pipeline should be treated as a typed function call:

```text
Input:  { model, messages[], temperature, max_tokens }
Output: { parsed_json | null }
```

Build a single `IntelligenceService` wrapper that:

1. Makes the API call with error handling and timeout
2. Extracts the text content from the response object
3. Strips markdown fences (`\`\`\`json`) that models commonly add
4. Parses JSON safely with a fallback
5. Sanitises output for injection patterns before returning

Never let raw model output reach your business logic. It must pass through this sanitisation layer every time.

---

## Phase 4 — The RAG Pipeline: Detailed Implementation

### 4.1 Stage 1: Intent Understanding (The Triage Router)

**Purpose:** Convert the raw user input (natural language, preferences, constraints) into a structured plan that downstream stages can consume deterministically.

**Model choice:** The smallest model that reliably produces valid JSON for your schema. At the time of writing, 1–4B instruction-tuned models (Qwen 1.5B, Gemma 4B, Llama 3.2 3B) are capable of this at sub-400ms latency.

**Prompt discipline for structured output:**

- Specify the exact JSON schema in the prompt, including field names and types
- Give a concrete example of valid output
- Use `temperature=0.1` — you want determinism, not creativity
- Set a fallback in code: if the model output cannot be parsed as your schema, fall back to a default plan derived from the raw input

**Output contract:**

```json
{
    "search_terms": ["term1", "term2", "term3"],
    "constraints": { "budget_max": 2000, "climate": "temperate" },
    "signal_requirements": { "weather": true, "events": false }
}
```

### 4.2 Stage 2: Query Synthesis

**Purpose:** Translate the triage plan into executable queries for each retrieval source.

**This stage is where most teams cut corners and pay later.** Query synthesis should be its own LLM call, not embedded in the triage or synthesis prompts. This separation means:

- You can optimise each prompt independently
- You can test query quality in isolation
- You can add a new retrieval source by adding one branch here, not by modifying the triage logic

**LLM-generated SQL safety:** When using an LLM to generate SQL, always validate the output before execution:

1. Parse with `sqlparse` and confirm it is a `SELECT` statement
2. Verify the statement targets only allowed tables
3. Check for forbidden keywords (`DROP`, `DELETE`, `UPDATE`, `--`)
4. Execute with a read-only DB user that has no write permissions

**Output contract:**

```json
{
    "postgres_sql": "SELECT id FROM destinations WHERE region_type = 'Coastal' LIMIT 20",
    "qdrant_params": {
        "search_text": "peaceful coastal retreat off the beaten path",
        "filters": { "must": [{ "key": "base_vibe", "match": { "value": "quiet" }}] }
    },
    "api_specs": {
        "weather": { "required": true },
        "events": { "required": false }
    }
}
```

### 4.3 Stage 3: Parallel Retrieval Burst

**Purpose:** Execute all retrieval operations simultaneously.

This stage has a single implementation rule: **use `asyncio.gather()` for everything.**

```python
results = await asyncio.gather(
    postgres_service.fetch_candidate_ids(query_strategy["postgres_sql"]),
    vector_service.search_by_vibe(query_vector, filters=qdrant_filters),
    signal_service.get_environmental_state(destination_id),
    analytics_service.get_historical_trend(destination_id, mood)
)
```

The difference between sequential and parallel retrieval here is typically 1–3 seconds at P99. In a sub-2s SLA system, sequential retrieval makes the SLA structurally impossible.

**Error handling:** `asyncio.gather()` raises on the first exception by default. Use `return_exceptions=True` and handle partial failures gracefully — a failed signal fetch should degrade the recommendation quality, not abort the entire request.

**Timeout strategy:** Every I/O call should have an explicit timeout. External API calls: 2–3s. Database calls: 1s. Vector search: 500ms. If a source exceeds its timeout, use the cached value or a stub default — never let one slow external API block your response.

### 4.4 Stage 4: Merge, Rank, and Filter

**Purpose:** Combine results from heterogeneous sources into a single ordered candidate list.

**The intersection pattern:**

1. Postgres gives you a set of IDs that satisfy hard constraints
2. Qdrant gives you a ranked list of semantically similar results
3. The merge step filters Qdrant results to only those also in the Postgres set

**Important:** If the intersection is empty (no candidates satisfy both constraints and semantic match), fall back to the Qdrant results only rather than returning nothing. This is a product decision — do you prefer precision (only return valid results) or recall (return the best available even if constraints are not fully met)? Make it explicit.

**Score normalisation:** If you are combining scores from different sources (semantic similarity + historical trend score + signal-based penalty), normalise each to [0.0, 1.0] before combining, and apply explicit weights that you can tune.

### 4.5 Stage 5: Synthesis (The Cognitive Layer)

**Purpose:** Convert the top candidate(s) and their associated context into a natural language explanation with structured reasoning steps.

**Model choice:** This is the only stage that justifies a large model (30–70B). Every other stage should be done by the cheapest model that produces reliable structured output. The synthesis model is the one that talks to the user.

**Prompt structure:**

```text
SYSTEM: Define the model's persona, output format, and constraints
CONTEXT: The retrieved data (destination metadata + signals + trends)
USER CONTEXT: The original user intent and preferences
TASK: Generate a reasoning_chain[] with explicit domain attribution
OUTPUT FORMAT: JSON array of reasoning steps with step_id, logic, domain, impact_weight
```

**Reasoning chain output contract:**

```json
[
    {
        "step_id": 1,
        "logic": "Matches the 'isolation and creativity' preference cluster with 0.92 semantic similarity",
        "domain": "Persona",
        "impact_weight": 0.6
    },
    {
        "step_id": 2,
        "logic": "Current weather (12°C, clear) is within the user's stated 'cool but not freezing' constraint",
        "domain": "Environmental",
        "impact_weight": 0.3
    }
]
```

**Why structured reasoning chains?** They serve three purposes: (1) the end user can see *why* the recommendation was made, (2) you can audit the system's logic for quality assurance, and (3) you can use them as training signal for improving the pipeline over time.

---

## Phase 5 — API Layer

### 5.1 Endpoint Design Principles

Define the minimum surface area needed. For a RAG recommendation system, the core endpoints are:

```text
POST   /api/v1/{resource}/              → trigger the pipeline, return result
GET    /api/v1/{resource}/{id}          → retrieve a specific result by ID
GET    /api/v1/health                   → liveness + readiness check
POST   /api/v1/auth/login               → issue access token
POST   /api/v1/auth/refresh             → exchange refresh token
```

**Schema-first:** Define Pydantic models for every request and response before implementing the endpoint logic. The schema is the API contract. Changing it later is a breaking change.

**Versioning from day one:** All routes under `/api/v1/`. When you introduce breaking changes, add `/api/v2/` alongside. Never mutate a versioned route.

### 5.2 Request Validation as a Security Layer

Every input to the RAG pipeline is potentially adversarial. Validate at the schema level (Pydantic) and at the semantic level (middleware):

```python
# Schema level: Pydantic rejects malformed input before it reaches your logic
class UserPersona(BaseModel):
    preferences: Dict[str, Annotated[float, Field(ge=0.0, le=1.0)]]
    constraints: List[str] = Field(max_length=20)
    mood: Optional[str] = Field(None, max_length=500)

# Semantic level: middleware rejects prompt injection attempts
injection_patterns = [
    "ignore all previous instructions",
    "you are now",
    "system prompt",
    "override"
]
```

---

## Phase 6 — Authentication, Authorisation, and Policy

### 6.1 Authentication

Implement JWT with short-lived access tokens and long-lived refresh tokens from the start — adding auth to an existing codebase is significantly harder than building it in.

Standard pattern:

- Access token: 15–30 minutes, used for every API call
- Refresh token: 7 days, stored securely, used only to get a new access token
- Token blacklist: store revoked refresh tokens in Redis until their natural expiry

### 6.2 Authorisation Model

Start with RBAC (roles stored in the users table) and add a policy layer for resource-level rules:

```text
RBAC: user | moderator | admin → coarse-grained (which endpoints)
Policy: owner check → fine-grained (which specific records)
```

For complex organisations (multi-tenant, per-tenant permissions), consider OPA (Open Policy Agent) as an authorisation sidecar.

### 6.3 Service-to-Service Auth

Internal services (Kafka consumers, cron jobs, seeder scripts) should authenticate with static API keys, not JWTs. Store them in your secrets manager, not in the environment files committed to your repo.

---

## Phase 7 — Security

Treat these as production blockers, not post-launch tasks.

**LLM-specific threats:**

| Threat | Mitigation |
| ------ | ---------- |
| Prompt injection via user input | Sanitise all user text before embedding in prompts; detect injection patterns in middleware |
| LLM-generated SQL injection | Validate all generated SQL against an allowlist before execution; use read-only DB user |
| Model output exfiltration | Sanitise model outputs before returning to client; never include internal prompts in responses |
| Stale/hallucinated data | Always ground synthesis in retrieved context; include `context_snapshot` in response for audit |

**Infrastructure threats:**

| Threat | Mitigation |
| ------ | ---------- |
| API key exposure | Secrets manager (AWS SSM / Vault); never in code or committed env files |
| Dependency CVEs | `pip-audit` in CI; Trivy for container images |
| Enumeration via UUIDs | Use UUIDs as primary keys, not sequential integers |
| SSRF via external API calls | Validate URLs against an allowlist before making outbound requests |

---

## Phase 8 — DevOps, CI/CD, and Cloud

### 8.1 Pipeline Stages

A production CI/CD pipeline for a RAG system has these stages, in order:

```text
1. Quality Gate
   ├── Linting (ruff)
   ├── Type checking (mypy --strict)
   └── Security scan (bandit, pip-audit)

2. Test Suite
   ├── Unit tests (mocked dependencies, fast)
   ├── Integration tests (real DBs via testcontainers)
   └── LLM contract tests (mock API, validate JSON schema output)

3. Build
   └── Docker image build + push to registry

4. Deploy to Staging
   └── Automated (on main branch merge)

5. Deploy to Production
   └── Manual approval gate
```

### 8.2 Dockerfile Best Practices for AI Systems

```dockerfile
FROM python:3.11-slim AS builder
# Install dependencies into /install prefix
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim AS production
# Non-root user — required for container security
RUN adduser --system appuser
USER appuser

# Copy only the compiled dependencies, not build tools
COPY --from=builder /install /usr/local
COPY . /app
WORKDIR /app

# Health check that validates the full dependency chain
HEALTHCHECK CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Gunicorn with Uvicorn workers for production concurrency
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4"]
```

**Model loading:** If you are using local embedding models (SentenceTransformers), load them at startup, not per-request. The `HEALTHCHECK` should only return 200 after the model is loaded.

### 8.3 Environment Strategy

Maintain three fully isolated environments backed by separate infrastructure:

| Environment | Purpose | Data Policy |
| ----------- | ------- | ----------- |
| `local` | Development | Seeded test data, no PII |
| `staging` | Pre-production validation | Anonymised production copy |
| `production` | Live system | Full data, PII-protected |

The same Docker image must be deployed to staging and production. If staging passes, production will pass. If they use different images, staging proves nothing.

### 8.4 Infrastructure as Code

Every infrastructure resource should be defined in Terraform (or equivalent). The Snowflake provider in this project is the right pattern — extend it to cover your application infrastructure (ECS/Cloud Run, RDS, ElastiCache, MSK).

Medallion architecture for your analytics warehouse:

```text
Bronze (RAW)    → raw ingested events, immutable, append-only
Silver (CLEAN)  → deduplicated, typed, enriched
Gold (ANALYTICS)→ aggregated, business-ready, used by the reasoning engine
```

---

## Phase 9 — Observability

### 9.1 Replace Print Statements with Structured Logs

Every `print()` in your codebase is a gap in your observability. Replace all of them with structured log calls before the first production deployment:

```python
import structlog
logger = structlog.get_logger()

logger.info("rag.pipeline.complete",
    stage="synthesis",
    destination_id=dest_id,
    match_score=score,
    latency_ms=elapsed,
    model=synthesis_model,
    user_id=user.id,
    request_id=request.state.request_id
)
```

Every log event should be parseable as JSON and should include the `request_id` so you can trace a single request across all service layers.

### 9.2 Metrics to Instrument from Day One

```text
rag.pipeline.latency_ms          (breakdown by stage)
rag.llm.call_duration_ms         (breakdown by model)
rag.vector_search.latency_ms
rag.signal.cache_hit_rate
rag.pipeline.error_rate          (breakdown by stage)
kafka.consumer.lag               (if using event streaming)
```

Set SLA alerts on `rag.pipeline.latency_ms` P99 and `rag.pipeline.error_rate` from day one. Finding out your P99 is 8 seconds from a customer complaint is not acceptable.

### 9.3 The Request ID Pattern

Every request that enters your system must carry a `request_id` (UUID) that is:

- Generated by the API gateway if not provided by the client
- Attached to every log event for that request
- Attached to every downstream service call (as an HTTP header)
- Included in the response to the client

Without this, debugging multi-stage pipelines in production is essentially impossible.

---

## Phase 10 — Internationalisation

If your system serves multiple locales or languages, add i18n infrastructure before your first production release. Retrofitting it is expensive.

**Key decisions:**

1. **Locale detection:** Accept-Language header → user profile preference → system default
2. **Message catalogue:** GNU gettext / Babel for error messages and system strings
3. **LLM output localisation:** Pass the target locale to the synthesis prompt explicitly. Do not rely on the model to infer locale from context.
4. **Data localisation:** Store destination names in multiple locales in your relational DB, not just the English name.

---

## Meta-Decisions: What Compounds Most

These are the decisions that, once made, are hardest to reverse. Make them consciously and early.

### M1: Embedding Model and Dimension

Changing your embedding model requires re-indexing your entire vector corpus. If you start with `all-MiniLM-L6-v2` (384-dim) and later want to upgrade to a 1536-dim model, you must re-embed and re-upsert every record. At scale, this is a significant operational event. Decide your embedding model before your first production seeding run.

### M2: Primary Key Strategy

Switching from sequential integer IDs to UUIDs (or vice versa) after you have data in production is a painful migration. Start with UUIDs.

### M3: Database Schema Evolution Contract

The practice of using Alembic for every schema change is a convention that must be established before any production data exists. Establishing it after the fact means backfilling migration history and carries risk of environment divergence.

### M4: The Prompt-as-Code Discipline

Every LLM prompt in your system is code. It should be version-controlled, reviewed, and tested like code. The pattern of embedding prompts as inline strings in function bodies makes them invisible to your review process and untestable in isolation. Consider externalising prompts into dedicated prompt template files that are loaded at startup.

### M5: API Versioning

Adding versioning (`/api/v1/`) after you have clients consuming your API requires coordinating a migration. Add it before you have any external consumers.

### M6: The Separation Between Triage and Synthesis Models

The decision to use different models for different stages of the pipeline (small, fast models for structured extraction; large, capable models for synthesis) is an architectural commitment that affects your cost model, your latency profile, and your failure modes. Establishing this pattern early means you can tune each stage independently. Collapsing everything into a single model call makes optimisation much harder later.

---

## Sprint Structure Template

Derived from the ChaloGhumo sprint sequence, this is the generalised sprint cadence for a RAG agentic system:

```text
Sprint 0:  Epistemic foundations, ontology, architecture design
           (no code, all documents)

Sprint 1:  Data layer — schema, vector store, seeding, service stubs
           (working infrastructure, defined contracts, no business logic)

Sprint 2:  Intelligence layer — real LLM integration, external signals,
           embedding pipeline, end-to-end test (single curl-based flow)
           (system works, quality is not yet optimised)

Sprint 3:  Hardening — CI/CD, security, rate limiting, auth,
           prompt injection protection, structured logging
           (system is safe to deploy)

Sprint 4:  RAG optimisation — multi-model pipeline, parallel retrieval,
           query expansion, reasoning chain quality, latency profiling
           (system is good, not just working)

Sprint 5:  Production readiness — observability, load testing,
           i18n, documentation, runbooks
           (system is ready for real traffic)
```

The deliberate ordering here reflects a hard-won lesson: teams that try to optimise their RAG quality (Sprint 4 work) before their infrastructure is solid (Sprint 1–3 work) build systems that are fast to demo but impossible to operate.

---

## Appendix — Common Failure Patterns

These are the patterns observed most frequently in RAG system failures. Each has a preventive measure that is cheap to implement early and expensive to retrofit.

| Failure Pattern | Root Cause | Prevention |
| --------------- | ---------- | ---------- |
| Hallucinated recommendations | Synthesis model not grounded in retrieved context | Always pass `context_snapshot` to synthesis prompt; include retrieval confidence scores |
| Ghost recommendations | Stale signals, no TTL enforcement | Define signal decay policy in ontology; implement TTL at Redis key level |
| SQL injection via query builder | Unsanitised LLM-generated SQL | Validate all generated SQL before execution; use read-only DB user |
| Prompt injection | User input passed directly to LLM prompt | Sanitise all user text; detect injection patterns in middleware |
| 5-second P99 latency | Sequential retrieval | Use `asyncio.gather()` for all retrieval stages |
| Schema drift between Postgres and Qdrant | No payload schema enforcement | Validate every Qdrant upsert against a Pydantic model |
| Incoherent reasoning chains | No epistemic foundations | Write the Epistemic Foundations document before any code |
| Embedding dimension mismatch | Model changed post-seeding | Decide embedding model before first seeding run; document in ontology |
| Environment divergence | Manual DB changes bypassing migrations | Alembic for every change from day one; no `create_all()` in production |
| Untraceable production errors | No request ID propagation | Add request ID middleware before the first production deployment |

---

*Playbook version 1.0 — synthesised from ChaloGhumo sprints 1–4.*
*Intended audience: engineers building production RAG agentic systems from scratch.*
