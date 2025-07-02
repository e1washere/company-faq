## LLM API Gateway (M2)

FastAPI сервис с единственным эндпоинтом `/chat`.

| provider | модели                           |
|----------|----------------------------------|
| openai   | gpt-3.5-turbo, gpt-4o-mini       |
| vertex   | gemini-pro (us-central1)         |

### Запуск
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=…
export VERTEX_PROJECT=patrianna-rag-demo
export VERTEX_LOCATION=us-central1
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/keys/vertex-sa.json
uvicorn api_gateway:app --port 8000
