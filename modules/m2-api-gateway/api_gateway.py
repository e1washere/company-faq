from __future__ import annotations

import os
from enum import Enum
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

load_dotenv()

OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
VERTEX_PROJECT   = os.getenv("VERTEX_PROJECT")   or os.getenv("GOOGLE_PROJECT")
VERTEX_LOCATION  = os.getenv("VERTEX_LOCATION")  or os.getenv("GOOGLE_LOCATION") or "us-central1"

DEFAULT_MODEL    = "gemini-2.5-pro"        

if not OPENAI_API_KEY:
    print("[WARN] OPENAI_API_KEY not set –- OpenAI provider will fail.")

app = FastAPI(title="LLM API Gateway", version="0.1.0")

class Provider(str, Enum):
    openai  = "openai"
    vertex  = "vertex"

class ChatMessage(BaseModel):
    role: str  = Field(..., examples=["user", "system", "assistant"])
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    provider: Provider
    model:    str
    content:  str

def _call_openai(model: str, messages: list[dict]) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp   = client.chat.completions.create(model=model, messages=messages)
    return resp.choices[0].message.content.strip()

def _call_vertex(model: str, messages: list[dict]) -> str:
    import vertexai
    from vertexai.generative_models import GenerativeModel

    vertexai.init(project=VERTEX_PROJECT, location=VERTEX_LOCATION)
    chat   = GenerativeModel(model).start_chat()

    user_txt = "\n".join(m["content"] for m in messages if m["role"] == "user")
    answer   = chat.send_message(user_txt)
    return str(answer.text).strip()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    provider: Provider = Query(
        Provider.vertex,
        description="LLM backend to use (openai / vertex)"
    ),
    model: str = Query(
        DEFAULT_MODEL,
        description="Model identifier (e.g. gpt-4o-mini, gemini-2.5-pro …)"
    ),
):
    messages = [m.model_dump() for m in req.messages]

    if provider is Provider.openai:
        if not OPENAI_API_KEY:
            raise HTTPException(500, "OPENAI_API_KEY not configured")
        content = _call_openai(model, messages)
    else:
        if not VERTEX_PROJECT:
            raise HTTPException(500, "VERTEX_PROJECT env var not set")
        content = _call_vertex(model, messages)

    return ChatResponse(provider=provider, model=model, content=content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_gateway:app", host="0.0.0.0", port=8000, reload=True)
    
