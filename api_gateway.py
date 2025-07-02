from __future__ import annotations

import os
from enum import Enum
from typing import List

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERTEX_PROJECT = os.getenv("VERTEX_PROJECT") or os.getenv("GOOGLE_PROJECT")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION") or os.getenv("GOOGLE_LOCATION", "us-central1")

if not OPENAI_API_KEY:
    print("[WARN] OPENAI_API_KEY not set – OpenAI provider will fail.")

app = FastAPI(title="LLM API Gateway", version="0.1.0")


class Provider(str, Enum):
    openai = "openai"
    vertex = "vertex"


class ChatMessage(BaseModel):
    role: str = Field(..., examples=["user", "system", "assistant"])
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    provider: Provider
    model: str
    content: str


def _call_openai(model: str, messages: List[dict]) -> str:
    import openai

    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(model=model, messages=messages)
    return response.choices[0].message["content"].strip()


def _call_vertex(model: str, messages: List[dict]) -> str:
    try:
        from vertexai.preview.language_models import ChatModel
        import vertexai
    except ImportError as exc:
        raise RuntimeError("Install google‑cloud‑aiplatform >= 1.49 to use Vertex AI") from exc

    vertexai.init(project=VERTEX_PROJECT, location=VERTEX_LOCATION)
    chat_model = ChatModel.from_pretrained(model)
    chat = chat_model.start_chat()

    user_content = "\n".join(m["content"] for m in messages if m["role"] == "user")
    response = chat.send_message(user_content)
    return str(response.text).strip()


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    provider: Provider = Query(Provider.openai, description="LLM backend to use"),
    model: str = Query("gpt-3.5-turbo", description="Model identifier"),
):
    messages = [m.dict() for m in req.messages]

    if provider == Provider.openai:
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
        content = _call_openai(model, messages)
    else:
        if not VERTEX_PROJECT:
            raise HTTPException(status_code=500, detail="VERTEX_PROJECT env var not set")
        content = _call_vertex(model, messages)

    return ChatResponse(provider=provider, model=model, content=content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_gateway:app", host="0.0.0.0", port=8000, reload=True)
