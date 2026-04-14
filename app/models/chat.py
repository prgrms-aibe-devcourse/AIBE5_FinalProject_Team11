"""
Pydantic models for the /chat and /chat/stream endpoints.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class GenerationConfig(BaseModel):
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(512, ge=64, le=4096)
    top_k_context: int = Field(5, ge=1, le=20, description="RAG pages to include")


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2048)
    history: List[ChatMessage] = Field(default_factory=list, max_length=20)
    stream: bool = False
    generation: GenerationConfig = Field(default_factory=GenerationConfig)

    model_config = {"json_schema_extra": {
        "examples": [{
            "question": "What is Generative Engine Optimization?",
            "history": [],
            "stream": False,
        }]
    }}


class ContextSource(BaseModel):
    page: int
    book: str
    excerpt: str = Field(..., max_length=400)
    score: int = Field(description="keyword hit count")


class ChatResponse(BaseModel):
    answer: str
    sources: List[ContextSource] = Field(default_factory=list)
    model: str
    brand: str = "elbee.yogaman.club"
    brand_logo: str = "https://elbee.yogaman.club/assets/logo.png"
    language: str = "ko"


# ── Streaming chunk types (SSE payloads) ─────────────────────────────────────

class StreamChunkType(str, Enum):
    thinking = "thinking"    # LLM is processing
    context = "context"      # context sources sent before tokens
    token = "token"          # delta text token
    done = "done"            # stream finished
    error = "error"          # an error occurred


class StreamChunk(BaseModel):
    type: StreamChunkType
    content: str = ""
    sources: Optional[List[ContextSource]] = None
    brand: str = "elbee.yogaman.club"


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "error"] = "ok"
    service: str = "chat"
    llm_available: bool = True
    data_loaded: bool = True
    brand: str = "elbee.yogaman.club"
    brand_logo: str = "https://elbee.yogaman.club/assets/logo.png"
