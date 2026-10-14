# M2 — LLM API gateway experiment

A FastAPI adapter with provider-specific OpenAI and Vertex AI calls. The current endpoint returns one JSON response. It does not stream tokens or invoke the RAG and mock-agent modules.

## Request contract

- Endpoint: `POST /chat`
- JSON body: `messages`, a list of objects containing `role` and `content`
- Query parameters: `provider` and `model`
- Response: provider, model, content, decision ID, and timestamp

The source defaults to Vertex and a fixed model identifier. Select an accessible provider/model explicitly; current provider availability has not been verified in this review.

## Local setup

From the repository root, inside your Python environment:

```bash
python -m pip install -r modules/m2-api-gateway/requirements.txt
cd modules/m2-api-gateway
python -m uvicorn api_gateway:app --host 127.0.0.1 --port 8000
```

Configure `OPENAI_API_KEY` for OpenAI. The Vertex path uses `VERTEX_PROJECT`, optional `VERTEX_LOCATION`, and the Google SDK's configured credentials.

Example request shape, with a model available to your account:

```bash
curl -X POST 'http://127.0.0.1:8000/chat?provider=openai&model=YOUR_MODEL_ID' \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

This request invokes an external provider and may incur charges. It has not been executed as part of this documentation update.

## Read the code

- `chat_endpoint()` validates the request, selects a provider, and returns a response.
- `_call_openai()` forwards the supplied messages.
- `_call_vertex()` concatenates user-message content; it does not preserve equivalent system/assistant-role semantics.
- `log_decision()` writes request messages, responses, and timing to local JSON files.

## Limitations

Provider calls are synchronous inside an async endpoint. The example has no demonstrated authentication, rate limiting, retry policy, or production load behavior. Logs may include the full request and response, so use synthetic data during exploration.

See [api_gateway.py](api_gateway.py) for the implementation. Installation, live provider calls, and the full test suite still require verification.
