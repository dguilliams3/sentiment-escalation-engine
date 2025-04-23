# 📦 Sentiment Escalation Pipeline – Multi-Agent GenAI System

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

- **📺 Live Dashboard (Flask)**  
  - Interactive dashboard at `localhost:8080`  
  - Submit reviews, inspect escalations, and explore Redis state in real time

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
> →   = Redis-triggered or HTTP-triggered transition

- Escalation entries are stored in Redis under the `escalations` key
- Escalation rule: if ≥3 (configurable) negative reviews for a product (outside cooldown), escalate
- If within cooldown, novelty check via GPT must return “yes” to allow escalation

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
| `dashboard`              | Flask App    | Manual in browser        | Interactive dashboard showing live escalations, review submission, and Redis key inspection |
| `redis`                  | System Core  | N/A                      | Pub/sub and KV store powering inter-agent coordination       |

---

## 🌐 Live Dashboard

- Run via Docker (`dashboard` service)
- Accessible at: [http://localhost:8080](http://localhost:8080)
- Features:
  - Review submission UI
  - Live escalation log
  - Quick inject of batch samples (positive, negative)
  - Redis debug inspectors for:
    - `raw_reviews`
    - `classified_reviews`
    - `cooldown_state`

---

## 🧱 System Architecture and Technologies

- **LLM Backend**: GPT-4o (via OpenAI API)
- **Orchestration**: Redis pub/sub
- **Framework**: Flask (each agent)
- **Deployment**: Docker + Docker Compose
- **Storage**: Redis in-memory + optional `.jsonl` output logs
- **Config**: `.env` + prompt templates via f-strings per agent

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

## 🧪 Deployment

```bash
# Step 1: Build all services
docker-compose build

# Step 2: Run the system
docker-compose up

# Step 3: Visit the dashboard
http://localhost:8080

# Step 4: Push to DockerHub (optional)
docker-compose push
```

---

### 📄 Environment Variables (`.env`)

Create a `.env` file in your project root to configure model behavior, Redis settings, and escalation logic.

```env
# Required for OpenAI API access
OPENAI_API_KEY=sk-...

# GPT Model settings (defaults shown)
GPT_MODEL=gpt-4o-mini
GPT_MAX_TOKENS=6000
GPT_TEMPERATURE=0.3

# Escalation logic
COOLDOWN_HOURS=6
ESCALATION_THRESHOLD=3

# Output file paths
ESCALATIONS_OUTPUT=output/escalations.json
COOLDOWN_FILE=output/cooldown_state.json
DECISION_LOG_FILE=output/escalation_decision_log.jsonl
CLASSIFIED_REVIEWS_FILE=output/classified_reviews.json

# Redis config
DATA_STORE=redis
REDIS_HOST=redis
RAW_REVIEW_KEY=raw_reviews

# Optional (default = same as GPT_MODEL)
SENTIMENT_MODEL=gpt-4o-mini
EXPLANATION_MODEL=gpt-4o-mini

# Optional logging config
LOG_USERNAME=admin
LOG_PASSWORD=password
LOG_FILE_PATH=./logs/context_log.log
```

---

## 🔮 Planned Enhancements

- **🔁 Feedback Loop (Human-in-the-Loop)**
  - Allow human reviewers to submit corrections or overrides

- **📊 Confidence Scoring + Prompt Lineage**
  - Add scoring layer + version tracking for each agent

- **📈 Monitoring + Metrics Collection**
  - Track token usage, agent call counts, latency

- **📜 Prompt Management via Database**
  - Swap hardcoded f-strings for PostgreSQL-backed templates

- **🧠 Model Configuration Layer**
  - Support multiple GPT models or endpoints

- **🧩 REST API Extensions**
  - Add query routes for historical sentiment or review reprocessing

- **📦 Persistence + Store Integration**
  - Optional Postgres storage layer for long-term product review tracking

- **🔐 Auth & Access**
  - Add JWT/API key protection on ingest routes

---

## 📂 Folder Structure

```
├── agents/
│   ├── sentiment_agent.py
│   ├── explainability_agent.py
│   ├── remote_sentiment_agent.py
│   └── remote_explainability_agent.py
├── app/
│   └── GPTClient.py
├── novelty_service/
│   └── service.py
├── sentiment_service/
│   └── service.py
├── explainability_service/
│   └── service.py
├── dashboard_service/
│   └── service.py
├── run_classification.py
├── run_smart_escalation.py
├── submit_review.py
├── pipeline.py
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```
