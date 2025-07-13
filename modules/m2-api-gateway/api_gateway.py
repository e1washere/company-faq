from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
VERTEX_PROJECT   = os.getenv("VERTEX_PROJECT")   or os.getenv("GOOGLE_PROJECT")
VERTEX_LOCATION  = os.getenv("VERTEX_LOCATION")  or os.getenv("GOOGLE_LOCATION") or "us-central1"

DEFAULT_MODEL    = "gemini-2.5-pro"        

# Decision logging directory
DECISION_LOG_DIR = Path("logs/decisions")
DECISION_LOG_DIR.mkdir(parents=True, exist_ok=True)

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set – OpenAI provider will fail.")

app = FastAPI(
    title="LLM API Gateway", 
    version="0.2.0",
    description="Enhanced API Gateway with decision logging and monitoring"
)

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
    decision_id: Optional[str] = None
    timestamp: Optional[str] = None

class DecisionLog(BaseModel):
    decision_id: str
    timestamp: str
    provider: Provider
    model: str
    messages: List[Dict]
    response: str
    processing_time: float
    success: bool
    error: Optional[str] = None

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

def log_decision(decision_log: DecisionLog):
    """Log decision for audit and monitoring."""
    try:
        log_file = DECISION_LOG_DIR / f"{decision_log.decision_id}.json"
        with open(log_file, 'w') as f:
            json.dump(decision_log.model_dump(), f, indent=2)
        logger.info(f"Decision logged: {decision_log.decision_id}")
    except Exception as e:
        logger.error(f"Failed to log decision: {e}")

def generate_decision_id() -> str:
    """Generate unique decision ID."""
    return f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

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
    decision_id = generate_decision_id()
    timestamp = datetime.now().isoformat()
    start_time = datetime.now()
    
    try:
        messages = [m.model_dump() for m in req.messages]
        logger.info(f"Processing chat request {decision_id} with {provider.value} provider")

        if provider is Provider.openai:
            if not OPENAI_API_KEY:
                raise HTTPException(500, "OPENAI_API_KEY not configured")
            content = _call_openai(model, messages)
        else:
            if not VERTEX_PROJECT:
                raise HTTPException(500, "VERTEX_PROJECT env var not set")
            content = _call_vertex(model, messages)

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Log successful decision
        decision_log = DecisionLog(
            decision_id=decision_id,
            timestamp=timestamp,
            provider=provider,
            model=model,
            messages=messages,
            response=content,
            processing_time=processing_time,
            success=True
        )
        log_decision(decision_log)

        return ChatResponse(
            provider=provider, 
            model=model, 
            content=content,
            decision_id=decision_id,
            timestamp=timestamp
        )
        
    except Exception as e:
        # Log failed decision
        processing_time = (datetime.now() - start_time).total_seconds()
        decision_log = DecisionLog(
            decision_id=decision_id,
            timestamp=timestamp,
            provider=provider,
            model=model,
            messages=messages if 'messages' in locals() else [],
            response="",
            processing_time=processing_time,
            success=False,
            error=str(e)
        )
        log_decision(decision_log)
        
        logger.error(f"Chat request {decision_id} failed: {e}")
        raise e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_gateway:app", host="0.0.0.0", port=8000, reload=True)
    
