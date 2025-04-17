### **📦 Sentiment Escalation Pipeline – Multi-Agent GenAI System**

![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Redis](https://img.shields.io/badge/Redis-Pub/Sub-red)
![GPT-4o](https://img.shields.io/badge/GPT--4o-Integrated-brightgreen)
![Status](https://img.shields.io/badge/Status-Active-green)

> Containerized NLP pipeline that classifies, explains, and escalates customer reviews using GPT-4o agents coordinated via Redis pub/sub microservices.

---

## 🚀 Key Features

- **Multi-Agent NLP Orchestration**
  - Independent agents for sentiment classification, explainability, novelty detection, and smart escalation
  - Agents communicate via Redis channels and shared review records

- **Modular Containerized Architecture**
  - Each service is fully Dockerized and stateless
  - Redis persists all shared state and review logs
  - Easily extendable with new agents or review policies

- **Redis-Orchestrated Agent Mesh**
  - Agents subscribe to Redis channels:
    - `classification_trigger`
    - `escalation_trigger`
  - Reviews are passed implicitly via Redis record keys like `raw_reviews`, `classified_reviews`, and `escalations`

- **LLM-Driven Reasoning**
  - GPT-4o used for sentiment and explanation agents
  - Novelty checked via a separate LLM-backed Flask service
  - Prompt temperature and models configured via `.env`

---

## 📊 Workflow

```plaintext
[User]
   ↓
[Ingest API] — /submit_review
   ↓
[SentimentAgent] → [ExplainabilityAgent]
   ↓
[SmartEscalationAgent]
   ↓
[Optional: Novelty Check] → Escalate if novel or cooldown expired

```

> [ ] = Docker container (Flask service)
> 
> →   = Redis-triggered or HTTP-triggered transition

- Escalation entries are stored in Redis under the escalations key, containing full review history, sentiment, rationale, and escalation reason.
- Escalation rule: if ≥3 (configurable value) negative reviews for a product (outside cooldown), escalate.
- If within cooldown, novelty check via GPT must return “yes” to allow escalation.

---

## 🔍 Redis Data Schema (Example)

```json
{
  "product_id": "toaster-9000",
  "text": "It exploded",
  "created_at": "...",
  "classified_at": "...",
  "sentiment": "the review is negative.",
  "explanation": "the review is considered negative because it describes a safety hazard..."
}
```

---

## 🛠 Services Included

| Service                  | Type         | Triggered By            | Description                                                  |
|--------------------------|--------------|--------------------------|--------------------------------------------------------------|
| `ingest_api`             | REST API     | External HTTP requests   | Accepts incoming reviews at `/submit_review`                |
| `SentimentAgent`         | Flask Agent  | Redis pub/sub            | Classifies review sentiment via GPT-4o                       |
| `ExplainabilityAgent`    | Flask Agent  | Redis pub/sub            | Adds explanation via GPT-4o                                  |
| `SmartEscalationAgent`   | Flask Agent  | Redis pub/sub            | Applies rule-based escalation logic, may call novelty check  |
| `novelty-service`        | REST API     | HTTP from Escalation     | Checks review novelty using GPT-4o                           |
| `redis`                  | System Core  | N/A                      | Pub/sub and KV store powering inter-agent coordination       |

### Additional Note

> All Flask-based services **can be extended to expose REST endpoints** (e.g., `/status`, `/reclassify`) for testing, debugging, or orchestration. Currently only `ingest_api` and `novelty-service` expose HTTP routes by default.

---

## 🧱 System Architecture and Technologies

- **LLM Backend**: GPT-4o (via OpenAI API)
- **Orchestration**: Redis pub/sub
- **Framework**: Flask (each agent)
- **Deployment**: Docker + Docker Compose
- **Storage**: Redis in-memory + optional `.jsonl` output logs
  *Note: Redis is used both as a message bus (via pub/sub) and a temporary state store (via key-value records).*
- **Config**: `.env` + static prompt strings (via f-strings) tailored per-agent

---

## 📈 What This Demonstrates

| Dimension         | Signal                                                           |
|-------------------|------------------------------------------------------------------|
| **Architectural Thinking** | Stateless, decoupled service mesh via Redis               |
| **Prompt Engineering**     | Role-specific prompts and explanations from GPT-4o         |
| **Deployment Fluency**     | Dockerized deployment with .env injection and composable microservices   |
| **Trust Handling**         | Escalation logic based on count thresholds and LLM-backed novelty checks with traceable logs    |
| **Scalability**            | Easily add API routes, agent types, or downstream routing  |

---

## 🔮 Planned Enhancements

- **🔁 Feedback Loop (Human-in-the-Loop)**
  - Allow human reviewers to submit corrections or overrides
  - Store reviewed samples for prompt optimization or fine-tuning candidates

- **📊 Confidence Scoring + Prompt Lineage**
  - Add lightweight scoring layer (token count heuristics, prior prompt match rate)
  - Track per-agent prompt versions and escalation outcomes

- **📈 Monitoring + Metrics Collection**
  - Integrate basic telemetry per agent (e.g., messages processed, GPT latency, token usage)
  - Output logs to structured format for optional ingestion into ELK/Prometheus stack

- **📜 Prompt Template Management via Database**
  - Move agent prompts from hardcoded strings to versioned rows in PostgreSQL
  - Enable per-agent prompt lookup by `agent_name`, `version`, and `active` flag
  - Future-proofed for:
    - Live prompt switching without redeploy
    - Prompt lineage audits for escalated or misclassified reviews
    - Logging which prompt generated which outcome

- **🧠 Model Configuration Layer**
  - Add support for multiple model endpoints or routing by workload type

- **🧩 REST API Extensions**
  - Add new routes to:
    - Retrieve escalations
    - Query product sentiment history
    - Submit feedback or corrections
    - Trigger re-evaluation for past reviews

- **📦 Persistence + Store Integration**
  - Swap Redis with optional Postgres backend for long-term review storage
  - Add support for batch ingestion and historical retrieval

- **🔐 Auth & Access Layers**
  - Add API key validation or JWT-based auth layer on `/submit_review`
  - Optional access tiers for read/write/admin review
