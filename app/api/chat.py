"""
Chat router — /chat

Endpoints:
  POST /chat          — single-turn RAG + LLM answer
  POST /chat/stream   — SSE streaming tokens
  GET  /chat/health   — liveness + readiness probe
  GET  /chat/examples — sample questions for the UI
"""
from __future__ import annotations

import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.models.chat import (
    ChatRequest, ChatResponse, ContextSource,
    HealthResponse, StreamChunk, StreamChunkType,
)
from app.services.loader import GeoDataStore, get_store
from app.services.llm_service import LLMService
from app.services.rag_service import RagService

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/chat", tags=["chat"])

# ── Dependency factories ───────────────────────────────────────────────────────

def get_rag(store: GeoDataStore = Depends(get_store)) -> RagService:
    return RagService(store)


def get_llm() -> LLMService:
    return LLMService()


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ChatResponse,
    summary="Ask a question about GEO marketing",
)
async def chat(
    body: ChatRequest,
    rag: RagService = Depends(get_rag),
    llm: LLMService = Depends(get_llm),
) -> ChatResponse:
    """
    Non-streaming RAG-powered chat.
    Retrieves relevant GEO-book chunks, then sends them to Ollama.
    """
    hits = rag.retrieve(
        body.question,
        top_k=body.generation.top_k_context,
        min_score=settings.rag_min_keyword_score,
    )
    context, sources = rag.build_context(hits)
    messages = rag.build_prompt(
        query=body.question,
        context=context,
        history=[m.model_dump() for m in body.history],
    )

    try:
        answer = await llm.chat(
            messages=messages,
            temperature=body.generation.temperature,
            max_tokens=body.generation.max_tokens,
        )
    except Exception as exc:
        logger.exception("LLM call failed: %s", exc)
        # Graceful degradation: return raw context if LLM is unavailable
        fallback = (
            "⚠️ The LLM is currently unavailable. "
            "Here are the most relevant passages from the GEO reference book:\n\n"
            + "\n\n".join(f"[Page {s.page}] {s.excerpt}" for s in sources)
        )
        return ChatResponse(
            answer=fallback,
            sources=sources,
            model=llm.model,
        )

    return ChatResponse(answer=answer, sources=sources, model=llm.model)


@router.post(
    "/stream",
    summary="Streaming RAG chat (Server-Sent Events)",
    response_class=StreamingResponse,
)
async def chat_stream(
    body: ChatRequest,
    rag: RagService = Depends(get_rag),
    llm: LLMService = Depends(get_llm),
) -> StreamingResponse:
    """
    SSE streaming chat. 

    Event types emitted in order:
      1. `thinking` — retrieval is in progress
      2. `context`  — sources used (JSON list in `content`)
      3. `token`    — each text fragment from the LLM
      4. `done`     — stream is complete
      5. `error`    — if something goes wrong
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        def _sse(chunk: StreamChunk) -> str:
            return f"data: {chunk.model_dump_json()}\n\n"

        yield _sse(StreamChunk(type=StreamChunkType.thinking, content="Retrieving context…"))

        hits = rag.retrieve(
            body.question,
            top_k=body.generation.top_k_context,
            min_score=settings.rag_min_keyword_score,
        )
        context, sources = rag.build_context(hits)

        yield _sse(StreamChunk(
            type=StreamChunkType.context,
            content=json.dumps([s.model_dump() for s in sources]),
            sources=sources,
        ))

        messages = rag.build_prompt(
            query=body.question,
            context=context,
            history=[m.model_dump() for m in body.history],
        )

        try:
            async for token in llm.stream_chat(
                messages=messages,
                temperature=body.generation.temperature,
                max_tokens=body.generation.max_tokens,
            ):
                yield _sse(StreamChunk(type=StreamChunkType.token, content=token))
        except Exception as exc:
            logger.exception("LLM stream failed: %s", exc)
            yield _sse(StreamChunk(
                type=StreamChunkType.error,
                content=f"LLM unavailable: {exc}",
            ))
            return

        yield _sse(StreamChunk(type=StreamChunkType.done, content=""))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check for the chat service",
)
async def health(
    store: GeoDataStore = Depends(get_store),
    llm: LLMService = Depends(get_llm),
) -> HealthResponse:
    llm_ok = await llm.is_available()
    return HealthResponse(
        status="ok" if (store.is_ready and llm_ok) else "degraded",
        llm_available=llm_ok,
        data_loaded=store.is_ready,
    )


@router.get(
    "/examples",
    summary="Sample questions to seed the chat UI",
)
async def examples() -> dict:
    return {
        "brand": settings.brand,
        "examples": [
            "What is Generative Engine Optimization (GEO)?",
            "How do I optimize content for Google SGE?",
            "What role do citations play in AI-generated search results?",
            "How is GEO different from traditional SEO?",
            "What are the best strategies for Perplexity AI visibility?",
            "How can I measure my GEO performance?",
        ],
    }
