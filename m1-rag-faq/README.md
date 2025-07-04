# RAG FAQ Bot (M1)

Minimal retrieval-augmented chatbot that answers questions about the company FAQ using **LangChain 0.2** + **Chroma** (local) or **Pinecone** (see M7).

---

## How it works
1. `rag_demo.py` loads `data/faq.md`.
2. Splits into 1 000-character chunks (200 overlap).
3. Generates OpenAI embeddings and persists to a local Chroma store (`m1-rag-faq/vector_store/`).
4. On every user question a `ConversationalRetrievalChain` retrieves the top k chunks and feeds them to GPT-3.5-turbo.

---

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export OPENAI_API_KEY="sk-..."

cd m1-rag-faq
python rag_demo.py --rebuild   # builds vectors & starts chat
```

### Example session
```text
You: What products does Patrianna build?
Bot: Patrianna specialises in creating engaging iGaming and web-based gaming products for millions of players worldwide.
```

### Screenshot tip *(optional)*
Run the bot, ask *"Which industries does Patrianna operate in?"* and capture the terminal. Save as `docs/m1_demo.png` and the image will appear below:

![demo](../docs/m1_demo.png)

---

## Files
| File              | Purpose                                         |
| ----------------- | ----------------------------------------------- |
| `data/faq.md`     | Source markdown document (company FAQ)          |
| `rag_demo.py`     | Loader → splitter → embedder → RAG chat loop    |
| `requirements.txt`| Module-level deps (inherits root file)          |

---

## Customisation tips
* **Embedding chunk size** – adjust `chunk_size` / `chunk_overlap` in `rag_demo.py`.
* **Switch to Pinecone** – set `PINECONE_API_KEY` then rerun with `--rebuild` (handled automatically by M7 logic).
* **Upgrade model** – change `gpt-3.5-turbo` to `gpt-4o-mini` in one line.

```