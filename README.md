# Company FAQ — LLM application experiments

A personal Python portfolio exploring document Q&A, LLM API adapters, reporting, SQL, and workflow orchestration.

**Status:** independent learning experiments, not a single integrated production platform. Some modules contain provider-integration code; M8 is an explicitly mocked workflow. External-service integrations and the complete test suite have not been revalidated as part of this documentation update.

## Module map

| Module | Scope | Status and boundary |
| --- | --- | --- |
| [M1: document Q&A](modules/m1-rag-faq/) | Markdown/text ingestion, chunking, OpenAI embeddings, Chroma, conversational retrieval | Implementation present; requires an API key and compatible dependencies |
| [M2: LLM API gateway](modules/m2-api-gateway/) | FastAPI adapter for OpenAI or Vertex AI | Provider calls present; returns one JSON response, not a token stream |
| [M3: reporting](modules/m3-auto-reporter/) | CSV/BigQuery events → prompt → Vertex AI summary → console/Slack | Integration experiment; external services not verified in this review |
| [M4: n8n](modules/m4-n8n/) | Exported workflow | Example configuration; execution not verified |
| [M5: SQL](modules/m5-sql-etl/) | Small BigQuery staging/table example and a ranking window function | Learning example; not a deployed scheduler or full ETL service |
| [M6: Vertex notebook](modules/m6-vertex-notebook/) | Notebook and Python experiment | Historical experiment; execution not verified |
| [M7: vector-store experiment](modules/m7-vector-swap/) | Separate retrieval demo | Experimental; inspect its source before relying on backend-selection behavior |
| [M8: mock workflow](modules/m8-crew-agents/) | Role-specific Python classes with JSON history | No CrewAI framework or LLM calls; analytical conclusions are hard-coded |

## Start with the smallest document-Q&A example

[M1 source](modules/m1-rag-faq/rag_demo.py) provides a concrete flow to inspect:

1. `ingest_docs()` reads a source file.
2. `RecursiveCharacterTextSplitter` splits it with a chunk size of 1,000 and overlap of 200.
3. `OpenAIEmbeddings` encodes the chunks and Chroma stores them.
4. `single_query()` uses `ConversationalRetrievalChain` and the retriever to generate an answer.
5. `chat_loop()` keeps question/answer history in memory for the session.

An API key is required for this module. Embedding and chat calls may incur provider charges. Commands below describe the current file layout; live provider compatibility has not been revalidated.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r modules/m1-rag-faq/requirements.txt
# Configure OPENAI_API_KEY in your local environment.
cd modules/m1-rag-faq
python rag_demo.py --source data/faq.md --rebuild --query "What information is in this FAQ?"
```

The code currently uses a fixed model identifier. Check model access and dependency compatibility before attempting a live run. Re-ingestion behavior and citation output need verification; the function currently returns the answer string only.

## Gateway boundary

M2 accepts `messages` in the JSON body and `provider` / `model` as query parameters. It does not automatically call M1, M8, or a vector store. See the [gateway README](modules/m2-api-gateway/README.md).

## What the workflow experiment demonstrates

M8 demonstrates class composition, sequential execution, keyword-based routing, and JSON persistence. Its agents do not perform model-based reasoning. Saving history does not train a model or prove that an agent improves over time. See the [M8 README](modules/m8-crew-agents/README.md).

## Verification and limitations

- Source-level behavior is described above; an end-to-end green build is not claimed.
- Existing tests need to be run and checked for meaningful assertions before relying on their results.
- Older module notes and screenshots are historical context, not proof of current service availability.
- Reporting and gateway examples can write request/report data to local files. Use synthetic data while exploring them.
- The modules are intentionally presented separately until their integration is demonstrated.

## License

[MIT](LICENSE).
