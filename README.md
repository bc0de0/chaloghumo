# ChaloGhumo: The Intelligence-Driven Travel Reasoning Engine

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)

ChaloGhumo is a state-of-the-art **Retrieval-Augmented Generation (RAG)** system designed to redefine travel discovery. Unlike traditional booking platforms that rely on static filters, ChaloGhumo utilizes a sophisticated **Reasoning Engine** to synthesize user "moods" and "vibes" with real-time global signals—providing hyper-personalized recommendations at the speed of thought.

---

## 🌟 The ChaloGhumo Vision: "Beyond Filtering"

Most travel platforms treat users like database administrators, forcing them to toggle rigid filters. ChaloGhumo treats users like travelers, allowing for natural language exploration of "soul-states" and "vibes."

### 🚀 Our Competitive Edge

* **Perceptual Immediacy**: Powered by **Together AI**, we achieve sub-2-second reasoning loops, beating legacy players by an order of magnitude.
* **Epistemic Depth**: We don't just "guess"; we provide transparent reasoning chains that explain *why* a destination matches your specific context.
* **Live Entropy Ingestion**: Our RAG architecture injects real-time weather, crowd density, and societal signals into every query.

---

## 🛠️ The Technical Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Logic Layer** | **FastAPI** | High-concurrency ASGI orchestrator |
| **Reasoning** | **Together AI (Llama 3 / Mixtral)** | Ultra-low latency cognitive core |
| **Vector Store** | **Qdrant** | High-dimensional semantic vibe memory |
| **Relational** | **PostgreSQL** | Durable destination and user metadata |
| **Signal Cache** | **Redis** | High-velocity signal entropy management |
| **Analytics** | **Snowflake** | Long-term historical trend prediction |

---

## 📚 Deep Dive Documentation

Explore our foundational principles and architectural blueprints:

* 🏗️ **[RAG Architecture](./docs/together_ai_rag_architecture.md)**: Our Together AI & Snowflake strategic roadmap.
* 🧪 **[Epistemic Foundations](./docs/epistemic_foundations.md)**: The logic and philosophy of our reasoning engine.
* 📐 **[Technical Stack](./docs/tech_stack.md)**: Detailed system design and component rationales.
* 📉 **[Invariants & Entropy](./docs/invariants_and_entropy.md)**: Safety rules and signal decay strategies.

---

## ⚡ Getting Started

### Prerequisites

* Docker & Docker Compose
* Together AI API Key
* Python 3.11+ (for local development)

### Launching the Stack

1. **Clone the repository** and navigate to the root directory.
2. **Setup Environment**:

   ```bash
   cp .env.example .env
   # Update your TOGETHER_API_KEY and database credentials
   ```

3. **Run with Docker**:

   ```bash
   docker-compose up --build
   ```

4. **Access the Engine**:

   * API: `http://localhost:8000`
   * Documentation: `http://localhost:8000/docs`

---

## ⚖️ License & Ownership

Conceptualized and Maintained by **Kunal Gupte and contributors**.

Licensed under a **Proprietary License**. All rights reserved. See [LICENSE.md](./LICENSE.md) for full details.

---
*Note: This project is in its early developmental stages and is evolving rapidly to achieve a "no-competition" market position.*
