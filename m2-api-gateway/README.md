# LLM API Gateway (M2)

Thin FastAPI layer that hides differences between **OpenAI** and **Vertex AI** chat endpoints.

*Single POST endpoint*: `/chat` accepts `{provider, model, messages}` and streams the reply.

| Provider | Supported models             |
|----------|------------------------------|
| openai   | gpt-3.5-turbo, gpt-4o-mini   |
| vertex   | gemini-pro (us-central1)     |

---

## Quick start
```bash
cd m2-api-gateway
pip install -r requirements.txt

# minimum env vars
export OPENAI_API_KEY="sk-..."      # for OpenAI requests
export VERTEX_PROJECT="my-gcp-proj"
export VERTEX_LOCATION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/keys/vertex-sa.json

uvicorn api_gateway:app --port 8000 --reload
```

### Example request
```bash
curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{
           "provider": "openai",
           "model":    "gpt-3.5-turbo",
           "messages": [{"role":"user","content":"Ping"}]
         }'
```

Expected stream:
```
{"provider":"vertex","model":"gemini-2.5-pro","content":"Pong.\n\nI'm here! Received your message loud and clear.\n\nHow can I help you?"}%                                                             
```
