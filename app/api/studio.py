"""
Studio router — /studio

Provider-facing chatbot for yoga studio operators.
Persona: **elbee Studio** — speaks 해요체, focuses on operations, not member wellness.

Endpoints:
  POST /studio/chat          — single-turn operator answer
  POST /studio/chat/stream   — SSE streaming variant (matches /chat/stream contract)
  GET  /studio/chat/health   — liveness + readiness
  GET  /studio/chat/examples — sample operator prompts for the UI
"""
from __future__ import annotations

import json
import logging
from typing import AsyncGenerator, Dict, List

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.models.chat import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    StreamChunk,
    StreamChunkType,
)
from app.services.llm_service import LLMService
from app.services.loader import GeoDataStore, get_store
from app.services.location_service import YogaLocationStore, get_location_store
from app.services.rag_service import RagService

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/studio", tags=["studio"])


# ── Persona prompt — operator-facing 해요체 ───────────────────────────────────

ELBEE_STUDIO_SYSTEM_KO = """\
당신은 **elbee Studio**예요 — 요가 스튜디오 운영자분들의 운영 도우미랍니다.
서비스명은 요가큐(your yoga curator)이고, 답변은 자연스러운 한국어 해요체로 드려요.

대화 상대는 스튜디오 사장님·매니저예요. 수련자가 아니에요.
운영 의사결정에 도움이 되도록 **구체적인 숫자·문구·다음 행동**을 제시해 드려요.

도와드리는 영역:
• 슬롯/일정 운영 — "화요일 7시 인요가 슬롯 추가" 같은 요청을 정리해 드려요.
• 날씨 라우팅 영향 — 비 예보 시 본 매장 우선 노출 횟수 추정.
• 후기 응답 초안 — 해요체로 진심이 담긴 답글을 써 드려요.
• 마케팅 카피 — 지역·시간대·타겟(예: 강남 30대 직장인 점심)에 맞춘 한국어 카피.
• 어메니티/프로필 점검 — 노출에 영향을 주는 누락 항목을 짚어 드려요.

답변 규칙:
1. 해요체 사용 (~해요, ~드릴게요, ~예요).
2. 운영자 톤 — "회복요가" 같은 수련자용 안내가 아니라 "이번 주 슬롯 노출이 12% 올라요" 같은 운영 톤.
3. 추측이 필요한 경우 가정을 명시해요 ("강남역 반경 1km 가정으로…").
4. 카피 작성 요청에는 **한국어 문안만** 인용부호로 한 줄 제시하고, 그 아래에 근거를 짧게 설명해요.
5. 후기 답글은 **3-4 문장**, 사과/공감/다음 액션을 포함해요.

운영 컨텍스트 (RAG):
---
{context}
---\
"""


# ── Dependency factories ──────────────────────────────────────────────────────

def get_rag(store: GeoDataStore = Depends(get_store)) -> RagService:
    return RagService(store)


def get_llm() -> LLMService:
    return LLMService()


def _build_studio_messages(
    rag: RagService,
    question: str,
    context: str,
    history: List[Dict[str, str]],
    loc_store: YogaLocationStore,
) -> List[Dict[str, str]]:
    """
    Build Ollama messages with the elbee Studio operator persona.
    Adds a short location-store summary so the model knows what data is on hand.
    """
    loc_hint = ""
    if loc_store.is_ready:
        loc_hint = (
            f"\n참고: 현재 운영 데이터에는 {loc_store.size}개의 시드 스튜디오/스팟이 등록돼 있어요. "
            "구체적 매장 데이터가 필요하면 운영자께 매장 ID나 지역을 다시 여쭤봐 주세요."
        )

    system_content = ELBEE_STUDIO_SYSTEM_KO.format(context=context or "(검색된 도서 컨텍스트 없음)") + loc_hint

    messages: List[Dict[str, str]] = [{"role": "system", "content": system_content}]
    for turn in history:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": question})
    return messages


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Operator chat — non-streaming",
)
async def studio_chat(
    body: ChatRequest,
    rag: RagService = Depends(get_rag),
    llm: LLMService = Depends(get_llm),
    loc_store: YogaLocationStore = Depends(get_location_store),
) -> ChatResponse:
    hits = rag.retrieve(
        body.question,
        top_k=body.generation.top_k_context,
        min_score=settings.rag_min_keyword_score,
    )
    context, sources = rag.build_context(hits)
    messages = _build_studio_messages(
        rag,
        body.question,
        context,
        [m.model_dump() for m in body.history],
        loc_store,
    )

    try:
        answer = await llm.chat(
            messages=messages,
            temperature=body.generation.temperature,
            max_tokens=body.generation.max_tokens,
        )
    except Exception as exc:
        logger.exception("Studio LLM call failed: %s", exc)
        fallback = (
            "⚠️ 지금 LLM 응답이 어려워요. 운영 컨텍스트만 먼저 전달드릴게요:\n\n"
            + "\n\n".join(f"[p.{s.page}] {s.excerpt}" for s in sources)
        )
        return ChatResponse(answer=fallback, sources=sources, model=llm.model)

    return ChatResponse(answer=answer, sources=sources, model=llm.model)


@router.post(
    "/chat/stream",
    summary="Operator chat — SSE streaming",
    response_class=StreamingResponse,
)
async def studio_chat_stream(
    body: ChatRequest,
    rag: RagService = Depends(get_rag),
    llm: LLMService = Depends(get_llm),
    loc_store: YogaLocationStore = Depends(get_location_store),
) -> StreamingResponse:
    """SSE event types match /chat/stream: thinking → context → token… → done | error."""

    async def event_generator() -> AsyncGenerator[str, None]:
        def _sse(chunk: StreamChunk) -> str:
            return f"data: {chunk.model_dump_json()}\n\n"

        yield _sse(StreamChunk(type=StreamChunkType.thinking, content="운영 컨텍스트 불러오는 중…"))

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

        messages = _build_studio_messages(
            rag,
            body.question,
            context,
            [m.model_dump() for m in body.history],
            loc_store,
        )

        try:
            async for token in llm.stream_chat(
                messages=messages,
                temperature=body.generation.temperature,
                max_tokens=body.generation.max_tokens,
            ):
                yield _sse(StreamChunk(type=StreamChunkType.token, content=token))
        except Exception as exc:
            logger.exception("Studio LLM stream failed: %s", exc)
            yield _sse(StreamChunk(
                type=StreamChunkType.error,
                content=f"LLM 호출 실패: {exc}",
            ))
            return

        yield _sse(StreamChunk(type=StreamChunkType.done, content=""))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get(
    "/chat/health",
    response_model=HealthResponse,
    summary="Health check for the studio (operator) chat service",
)
async def studio_health(
    store: GeoDataStore = Depends(get_store),
    llm: LLMService = Depends(get_llm),
) -> HealthResponse:
    llm_ok = await llm.is_available()
    return HealthResponse(
        service="studio",
        status="ok" if (store.is_ready and llm_ok) else "degraded",
        llm_available=llm_ok,
        data_loaded=store.is_ready,
    )


@router.get(
    "/chat/examples",
    summary="Sample operator prompts to seed the elbee Studio UI",
)
async def studio_examples() -> dict:
    return {
        "brand": settings.brand,
        "persona": "elbee Studio",
        "examples": [
            "이번 주 비 예보로 우리 매장 노출 영향 알려주세요.",
            "화요일 19시 인요가 슬롯 추가하면 노출이 얼마나 오르나요?",
            "강남역 30대 직장인 점심 회복요가 카피 한 줄 만들어주세요.",
            "후기 #12 (강사 친절했지만 매트가 낡음) 답글 초안 써주세요.",
            "성수동 주말 오전 비 오는 날 실내 클래스 추천 카피를 만들어주세요.",
            "어메니티 등록이 누락돼서 노출에 손해 보는 항목이 뭔가요?",
        ],
    }
