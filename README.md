# Company-FAQ • Mini AI Portfolio

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![LangChain](https://img.shields.io/badge/LangChain-0.2+-orange)
![CI](https://github.com/e1washere/company-faq/actions/workflows/ci.yml/badge.svg)

A collection of bite-sized projects that together showcase a full AI-Engineer skill-set — from **RAG** and **LLM gateways** to **SQL ETL** and **Vertex AI notebooks**.

![architecture diagram](docs/architecture.png)

---

## Project map

| Module | Folder | What it proves |
| ------ | ------ | -------------- |
| **M1 – RAG FAQ Bot**         | [`modules/m1-rag-faq`](./modules/m1-rag-faq/)                 | Embeddings, retrieval, LangChain basics              |
| **M2 – LLM API Gateway**     | [`modules/m2-api-gateway`](./modules/m2-api-gateway/)         | FastAPI ↔ OpenAI / Vertex, production patterns       |
| **M3 – Auto-Reporter Agent** | [`modules/m3-auto-reporter`](./modules/m3-auto-reporter/)     | LangChain Agent, BigQuery, Slack integration         |
| **M4 – n8n Flow**            | [`modules/m4-n8n`](./modules/m4-n8n/)                         | Low-code orchestration (Webhook → HTTP → Slack)      |
| **M5 – SQL + ETL**           | [`modules/m5-sql-etl`](./modules/m5-sql-etl/)                 | Window functions, scheduling, data-engineering chops |
| **M6 – Vertex Notebook**     | [`modules/m6-vertex-notebook`](./modules/m6-vertex-notebook/) | Gemini 2.5 Flash, GCP ML tooling                     |
| **M7 – Vector-DB Swap**      | [`modules/m7-vector-swap`](./modules/m7-vector-swap/)         | Pinecone ↔ Chroma hot-swap                           |

*(Each folder contains its own README with 30-sec run instructions & screenshots.)*

---

## Quick start (RAG demo)

```bash
# 1. Clone & enter
git clone https://github.com/e1washere/company-faq.git
cd company-faq

# 2. Python env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Mandatory keys
export OPENAI_API_KEY="sk-…"

# 4. (Optional) Pinecone creds for live index
export PINECONE_API_KEY="pc-…"      # v3 or v2 key
export PINECONE_REGION="us-east-1"   # v3, default aws/us-east-1
# OR legacy
env var
export PINECONE_ENV="my-env-id"      # v2 environment name

# 5. Build vectors & ask one question
python pinecone_demo.py --rebuild --query "What is Patrianna?"

# 6. Chat interactively
python pinecone_demo.py
```

> No Pinecone? No FAISS? The script automatically falls back to local **Chroma**, so it always works out-of-the-box.

---

## Module walk-through

| # | Highlight |
| - | -------- |
| **M1** | LangChain 0.2, `ConversationalRetrievalChain`, Chroma → Pinecone vector stores |
| **M2** | Production-grade REST gateway (FastAPI) with pluggable LLM back-ends + streaming responses |
| **M3** | Autonomous agent that queries BigQuery and posts rich Slack reports on schedule |
| **M4** | Pure n8n flow file demonstrating low-code webhook → transformation → notification |
| **M5** | Advanced SQL (window, CTE) + cron-ready ETL scripts |
| **M6** | Vertex AI Workbench notebook running Gemini Flash for rapid prototyping |
| **M7** | `pinecone_demo.py` – swap-able vector-DB layer (Pinecone v3/v2 → FAISS → Chroma) |

---

## 🚀 One-Command Cloud Run Deploy

Deploy the LLM API Gateway to Google Cloud Run in seconds:

```bash
# 1. Prerequisites
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Deploy in one command
./deploy.sh YOUR_PROJECT_ID us-central1

# 3. Set API keys (after deployment)
gcloud run services update company-faq-api --region=us-central1 \
  --set-env-vars="OPENAI_API_KEY=sk-...,VERTEX_PROJECT=YOUR_PROJECT_ID"
```

**What gets deployed:**
- **Production-ready FastAPI server** (Module M2) with OpenAI + Vertex AI support
- **Auto-scaling** from 0 to 10 instances based on traffic
- **Built-in monitoring** and logging via Cloud Run
- **Public HTTPS endpoint** with automatic SSL

**Example usage:**
```bash
# Test the deployed API
curl -X POST https://company-faq-api-xxx.a.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello!"}]}'
```

**Requirements:**
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
- Active GCP project with billing enabled
- Docker (automatically handled by Cloud Build)

---

## Environment variables

| Var | Purpose | Example |
| --- | ------- | ------- |
| `OPENAI_API_KEY` | Required for embeddings / chat | `sk-…` |
| `PINECONE_API_KEY` | Use managed Pinecone (v3 or v2) | `pc-…` |
| `PINECONE_REGION` | v3 region (default `us-east-1`) | `us-east-1` |
| `PINECONE_CLOUD` | v3 cloud provider (`aws`/`gcp`) | `aws` |
| `PINECONE_ENV` / `PINECONE_ENVIRONMENT` | v2 environment ID | `gcp-starter` |
| `CHROMA_TELEMETRY_ENABLED` | Disable Chroma telemetry | `false` |

---

## Tech stack

* Python 3.11
* LangChain 0.2 + `langchain_openai`
* Vector DBs: **Pinecone**, **FAISS**, **Chroma**
* FastAPI, BigQuery, Slack SDK
* n8n (low-code), SQL (BigQuery dialect)
* GCP Vertex AI + Gemini 2.5 Flash

See each folder for 30-sec run instructions & screenshots.
