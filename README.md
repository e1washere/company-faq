# Company FAQ RAG Bot

A **retrieval‑augmented generation (RAG)** chatbot that answers questions about any Markdown/PDF/HTML document – for this demo we feed it the *Patrianna* vacancy/FAQ.  The script shows:

- ingesting raw docs → chunking & embedding with **OpenAI**
- storing vectors locally in **Chroma** (persistent DB on disk)
- serving answers via **LangChain ConversationalRetrievalChain**



---

## Quick start

```bash
# 1 · clone & enter the repo
$ git clone https://github.com/e1washere/company-faq.git && cd company-faq

# 2 · create venv & install deps
$ python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt

# 3 · put your OpenAI key (or Vertex) into .env – NOT committed
$ echo "OPENAI_API_KEY=sk‑…" > .env

# 4 · build the vector store (first run only)
$ python rag_demo.py --source data/faq.md --rebuild

# 5 · ask a one‑off question
$ python rag_demo.py --query "What does Patrianna build?"

# or start interactive chat
$ python rag_demo.py
> How big is the AI team?
```

---

## Repo layout

```
company-faq/
├── data/           # raw corpus to embed (FAQ, job post, etc.)
├── docs/           # demo logs / screenshots
├── vector_store/   # auto‑generated Chroma DB (ignored in git)
├── rag_demo.py     # main demo script
├── requirements.txt
└── README.md
```

---

## How it works (high level)

1. **ingest\_docs()** – loads *data/faq.md*, splits into \~1‑2k‑token chunks, embeds via `OpenAIEmbeddings`.
2. Stores vectors in a local Chroma DB (`./vector_store`) so further runs are instant.
3. **chat()** – wraps `ChatOpenAI` with `ConversationalRetrievalChain` to combine context + chat history.
4. CLI flags `--source`, `--rebuild`, `--query`, `--model` make the script flexible.

You can swap **Chroma → Pinecone/Weaviate** or **OpenAI → VertexAI** in minutes (see later mini‑projects M6 & M7).

---

## Next steps / Roadmap

| Mini‑project                  | Skill demonstrated                      |
| ----------------------------- | --------------------------------------- |
| **M2** – FastAPI LLM Gateway  | prod‑grade API wrapper, Vertex ↔ OpenAI |
| **M3** – CrewAI auto‑reporter | agent orchestration & autonomy          |
| **M4** – n8n flow             | JS/n8n integration                      |
| …                             | …                                       |

Each lives in its own folder with the same commit discipline.

---

## License

MIT © 2025 Ivan Stankevich

