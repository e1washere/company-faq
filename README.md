# Company FAQ — Mini RAG Bot

A tiny **retrieval‑augmented generation (RAG)** demo that answers questions about a single document (for this repo we index `data/faq.md` – Patrianna’s vacancy text).  It shows end‑to‑end flow:

- ingest raw Markdown → split → embed with **OpenAI embeddings**
- store vectors locally in **Chroma** (on‑disk DB)
- chat / single‑query interface via **LangChain ConversationalRetrievalChain**

---

\## Quick start

```bash
# create & activate venv (optional)
python3 -m venv .venv && source .venv/bin/activate

# install deps
pip install -r requirements.txt

# set your OpenAI key (or put it in .env)
export OPENAI_API_KEY=sk‑...

# first run: build the vector store and jump into chat
python rag_demo.py --source data/faq.md --rebuild

# one‑off question (store already exists)
python rag_demo.py --query "What does Patrianna do?"
```

```
You: How many offices does Patrianna have?
Bot: Patrianna is headquartered in Gibraltar and operates fully remote with team members distributed across Europe and beyond – it doesn’t maintain fixed physical offices.
```

---

\## Project layout

```
company-faq/
├─ data/                # source docs (only faq.md for now)
├─ vector_store/        # auto‑generated Chroma persistence (git‑ignored)
├─ docs/                # saved Q&A transcripts / screenshots
├─ rag_demo.py          # main script
├─ requirements.txt     # exact deps
└─ README.md            # this file
```

---

\## Suppress Chroma telemetry\
The console prints harmless “Failed to send telemetry event” messages.  Silence them with:

```bash
export CHROMA_TELEMETRY=0
```

---

\## Next steps

- Swap the loader to `UnstructuredLoader` for PDF/HTML.
- Add a `--model gpt‑4o-mini` CLI flag.
- Deploy as a FastAPI endpoint → see **M2 API Gateway**.

