"""
elbee Studio agent — lightweight LangChain-style tool dispatch loop.

Per aeogeo issue #4 (Korean NLP + GEO automation), this module wires the
operator chatbot into a small set of GEO-marketing tools:

  • find_nearby_locations  — uses YogaLocationStore.find_nearby
  • get_weather_forecast   — KMA short-term forecast (stub if no API key)
  • get_district_stats     — slot/exposure trend stub for "이번 주 슬롯 노출 +12%"
  • search_yoga_books      — RAG retrieve over the existing GeoDataStore

Tool protocol (kept JSON-only so llama3 can produce it reliably):

    {"action":"tool", "tool":"<name>", "args":{...}}        ← call a tool
    {"action":"final","answer":"<해요체 운영자 답변>"}        ← finish

The agent loops up to `max_iters` times. Each tool result is fed back
to the LLM as an `OBSERVATION` system message; the model then decides
to call another tool or to emit the final answer.

The agent intentionally avoids the heavy `langchain` dependency — the
single-line JSON contract above is small enough that vanilla httpx +
llama3 is sufficient and 100 % offline-friendly. If a future task
requires `AgentExecutor`, swap `_decide_next_step` for LangChain's
runnable without touching the tools themselves.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.services.llm_service import LLMService
from app.services.location_service import YogaLocationStore
from app.services.rag_service import RagService

logger = logging.getLogger(__name__)


# ── Tool implementations ──────────────────────────────────────────────────────

async def tool_find_nearby_locations(
    loc_store: YogaLocationStore,
    *,
    lat: float,
    lng: float,
    radius_km: float = 1.0,
    weather: Optional[str] = None,
    location_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Wrap YogaLocationStore.find_nearby into a JSON-friendly dict."""
    if not loc_store.is_ready:
        return {"ok": False, "error": "location_store_empty", "results": []}
    hits = loc_store.find_nearby(
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        weather=weather,
        location_type=location_type,
    )
    results = [
        {
            "id": loc.get("id"),
            "name": loc.get("name"),
            "type": loc.get("type"),
            "district": loc.get("district"),
            "weather_indoor": loc.get("weather_indoor", True),
            "amenities": loc.get("amenities", []),
            "distance_km": dist,
        }
        for loc, dist in hits[:5]
    ]
    return {"ok": True, "count": len(results), "results": results}


async def tool_get_weather_forecast(
    *, district: str, days: int = 3
) -> Dict[str, Any]:
    """
    KMA 단기예보 stub.

    If env `KMA_API_KEY` is set, future revision can call the real
    공공데이터포털 API. For now we return a deterministic placeholder so
    the agent loop is testable end-to-end without network/secrets.
    """
    api_key = os.environ.get("KMA_API_KEY")
    if not api_key:
        # Deterministic stub — alternates rain/clear so the operator
        # can see how the model reasons about weather routing.
        sample_days = [
            {"date": f"D+{i}", "summary": "비" if i % 2 == 1 else "맑음",
             "rain_prob": 70 if i % 2 == 1 else 10, "high_c": 22, "low_c": 14}
            for i in range(days)
        ]
        return {
            "ok": True, "source": "stub", "district": district,
            "days": sample_days,
            "note": "KMA_API_KEY 미설정 — 결정론적 더미 데이터예요.",
        }
    # Placeholder for real KMA call.
    return {
        "ok": True, "source": "kma", "district": district, "days": [],
        "note": "KMA 연동은 후속 작업으로 남겨뒀어요.",
    }


async def tool_get_district_stats(*, district: str) -> Dict[str, Any]:
    """Stubbed stats — replace with a real DB query when slot table lands."""
    return {
        "ok": True,
        "district": district,
        "this_week": {
            "exposure_count": 1280,
            "exposure_delta_pct": 12,
            "top_class": "회복요가",
            "rain_routed_share_pct": 23,
        },
        "note": "운영 통계는 현재 시드값이에요. 실제 슬롯 테이블 연동은 후속.",
    }


async def tool_search_yoga_books(
    rag: RagService, *, query: str, top_k: int = 4
) -> Dict[str, Any]:
    hits = rag.retrieve(query, top_k=top_k)
    context, sources = rag.build_context(hits)
    return {
        "ok": True,
        "query": query,
        "context": context,
        "sources": [s.model_dump() for s in sources],
    }


# ── Tool registry ─────────────────────────────────────────────────────────────

TOOL_SPECS: List[Dict[str, Any]] = [
    {
        "name": "find_nearby_locations",
        "description": "운영 데이터에 등록된 요가 스튜디오/스팟을 좌표 반경으로 찾아요. 비 예보면 weather='비'로 호출하면 야외 스팟이 빠져요.",
        "args": {"lat": "float", "lng": "float", "radius_km": "float (default 1.0)",
                 "weather": "string optional (예: '비','맑음')",
                 "location_type": "string optional (예: 'official_elbee_club')"},
    },
    {
        "name": "get_weather_forecast",
        "description": "지역구의 단기 날씨 예보(3일치)를 받아와요. 비 라우팅 노출 영향 계산에 써요.",
        "args": {"district": "string (예: '강남구')", "days": "int (default 3)"},
    },
    {
        "name": "get_district_stats",
        "description": "지역구 운영 통계 (이번 주 노출/우천 라우팅 비중/탑 클래스).",
        "args": {"district": "string (예: '강남구')"},
    },
    {
        "name": "search_yoga_books",
        "description": "도서/문헌 RAG 검색 — 운영 인사이트 근거가 필요할 때만 사용.",
        "args": {"query": "string", "top_k": "int (default 4)"},
    },
]


def _tool_protocol_block() -> str:
    lines = ["사용 가능한 도구:"]
    for spec in TOOL_SPECS:
        lines.append(f"- {spec['name']}: {spec['description']}")
        lines.append(f"  args: {json.dumps(spec['args'], ensure_ascii=False)}")
    lines.append("")
    lines.append("응답 규칙:")
    lines.append("도구를 쓰려면 **단 한 줄 JSON**으로만 답해요:")
    lines.append('  {"action":"tool","tool":"<name>","args":{...}}')
    lines.append("운영자에게 최종 답을 드릴 때도 단 한 줄 JSON으로 답해요:")
    lines.append('  {"action":"final","answer":"해요체 한국어 답변"}')
    lines.append("JSON 외 다른 글자/마크다운 금지. 추측이 필요하면 가정을 answer 안에 명시해요.")
    lines.append('답변에 추천을 포함할 때는 항목마다 "→ 이유: …" 한 줄을 함께 적어요.')
    lines.append("운영 컨텍스트(또는 도구 결과)에 없는 스튜디오 이름은 지어내지 않고, 일반 가이드나 (예시) 표시로 답해요.")
    return "\n".join(lines)


# ── Agent ─────────────────────────────────────────────────────────────────────

@dataclass
class AgentEvent:
    """Structured event for SSE streaming."""
    type: str  # "thinking" | "tool_call" | "tool_result" | "final" | "error"
    content: str
    data: Optional[Dict[str, Any]] = None


@dataclass
class AgentState:
    messages: List[Dict[str, str]] = field(default_factory=list)
    iters: int = 0


_JSON_LINE_RE = re.compile(r"\{.*?\}", re.S)


def _find_balanced_json(raw: str) -> Optional[str]:
    """Return the first balanced `{...}` substring (string-aware brace counting)."""
    depth = 0
    start = -1
    in_str = False
    esc = False
    for i, ch in enumerate(raw):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                return raw[start:i + 1]
    return None


def _extract_json(raw: str) -> Optional[Dict[str, Any]]:
    """Try strict parse, then fall back to first balanced `{...}` substring."""
    raw = raw.strip()
    # strip code fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?|```$", "", raw, flags=re.M).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    candidate = _find_balanced_json(raw)
    if candidate:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return None
    return None


class StudioAgent:
    """
    LangChain-style tool dispatch loop for elbee Studio.
    """

    def __init__(
        self,
        llm: LLMService,
        rag: RagService,
        loc_store: YogaLocationStore,
        max_iters: int = 4,
    ) -> None:
        self.llm = llm
        self.rag = rag
        self.loc_store = loc_store
        self.max_iters = max_iters

    # ── Tool dispatch ────────────────────────────────────────────────────

    async def _call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if name == "find_nearby_locations":
                return await tool_find_nearby_locations(self.loc_store, **args)
            if name == "get_weather_forecast":
                return await tool_get_weather_forecast(**args)
            if name == "get_district_stats":
                return await tool_get_district_stats(**args)
            if name == "search_yoga_books":
                return await tool_search_yoga_books(self.rag, **args)
            return {"ok": False, "error": f"unknown_tool:{name}"}
        except TypeError as exc:
            return {"ok": False, "error": f"bad_args:{exc}"}
        except Exception as exc:  # pragma: no cover — defensive
            logger.exception("Tool %s failed", name)
            return {"ok": False, "error": f"tool_exception:{exc}"}

    # ── Prompt construction ──────────────────────────────────────────────

    def _system_prompt(self) -> str:
        from app.api.studio import ELBEE_STUDIO_SYSTEM_KO
        base = ELBEE_STUDIO_SYSTEM_KO.format(
            context="(에이전트 모드 — 필요 시 도구를 호출해 직접 데이터를 가져와요.)"
        )
        return base + "\n\n" + _tool_protocol_block()

    def _initial_messages(
        self, question: str, history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        msgs: List[Dict[str, str]] = [{"role": "system", "content": self._system_prompt()}]
        for turn in history:
            role = turn.get("role")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                msgs.append({"role": role, "content": content})
        msgs.append({"role": "user", "content": question})
        return msgs

    # ── Main loop (async generator of AgentEvent) ───────────────────────

    async def stream(
        self,
        question: str,
        history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 768,
    ) -> AsyncGenerator[AgentEvent, None]:
        state = AgentState(messages=self._initial_messages(question, history or []))

        yield AgentEvent(type="thinking", content="에이전트 시작 — 도구 사용 여부 판단 중…")

        for step in range(self.max_iters):
            state.iters = step + 1
            try:
                # Use streaming under the hood to avoid ReadTimeout on slow models;
                # we accumulate tokens then parse the full JSON line.
                chunks: List[str] = []
                async for tok in self.llm.stream_auto(
                    messages=state.messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                ):
                    chunks.append(tok)
                raw = "".join(chunks).strip()
            except Exception as exc:
                import traceback
                tb = traceback.format_exc(limit=3)
                yield AgentEvent(
                    type="error",
                    content=f"LLM 호출 실패: {type(exc).__name__}: {exc!r}",
                    data={"traceback": tb},
                )
                return

            parsed = _extract_json(raw)
            if not parsed or "action" not in parsed:
                # Model didn't follow protocol — treat raw as final answer.
                yield AgentEvent(
                    type="final",
                    content=raw or "(응답이 비어 있어요.)",
                    data={"fallback": True, "iter": state.iters},
                )
                return

            action = parsed.get("action")

            if action == "final":
                yield AgentEvent(
                    type="final",
                    content=str(parsed.get("answer", "")).strip()
                            or "(빈 답변이에요.)",
                    data={"iter": state.iters},
                )
                return

            if action == "tool":
                tool_name = parsed.get("tool", "")
                tool_args = parsed.get("args", {}) or {}
                yield AgentEvent(
                    type="tool_call",
                    content=tool_name,
                    data={"tool": tool_name, "args": tool_args, "iter": state.iters},
                )
                result = await self._call_tool(tool_name, tool_args)
                yield AgentEvent(
                    type="tool_result",
                    content=tool_name,
                    data={"tool": tool_name, "result": result, "iter": state.iters},
                )
                # Feed result back as system observation; ask for next JSON line.
                state.messages.append({"role": "assistant", "content": json.dumps(parsed, ensure_ascii=False)})
                state.messages.append({
                    "role": "system",
                    "content": (
                        f"OBSERVATION ({tool_name}):\n"
                        f"{json.dumps(result, ensure_ascii=False)}\n"
                        "위 결과를 반영해 다음 단계를 결정해요. "
                        '도구를 더 쓰거나, 충분하면 {"action":"final","answer":"..."} 한 줄로 마무리해요.'
                    ),
                })
                continue

            # Unknown action
            yield AgentEvent(
                type="error",
                content=f"unknown_action:{action!r}",
                data={"raw": raw[:400]},
            )
            return

        # Hit max iterations without final
        yield AgentEvent(
            type="final",
            content="(에이전트 반복 횟수 초과 — 최종 답을 내지 못했어요. 질문을 더 구체적으로 주시면 다시 시도해 드려요.)",
            data={"iter": state.iters, "max_iters_reached": True},
        )

    # ── Convenience: collect full run ────────────────────────────────────

    async def run(
        self,
        question: str,
        history: Optional[List[Dict[str, str]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        events: List[Dict[str, Any]] = []
        final_answer = ""
        async for ev in self.stream(question, history, **kwargs):
            events.append({"type": ev.type, "content": ev.content, "data": ev.data})
            if ev.type == "final":
                final_answer = ev.content
        return {"answer": final_answer, "trace": events}
