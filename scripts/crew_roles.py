"""
aeogeo CrewAI roles
===================

Three role-played agents that collaborate on top of the LangGraph
orchestrator's `generate` node. Pure-Python fallbacks are always wired
in so the demo runs offline; real `crewai` + LLM is used when both
the package and an API key are present.

Roles
-----
- Researcher: extracts the strongest 1–3 evidence snippets from RAG
  citations and instructor manual context.
- Curator:    sequences a 3-step session (warm-up / main / cool-down)
  consistent with the safety modifications and the studio's specs.
- Marketer:   writes Korean-first concierge copy that highlights why
  this studio matches the user (need fit / proximity / specialization).

Usage from orchestrator.node_generate:
    from crew_roles import run_crew
    state["answer"] = run_crew(state)["copy"]
"""

from __future__ import annotations

import os
from typing import Any

# ---------------------------------------------------------------------------
# Lightweight LLM call (shared with orchestrator semantics)
# ---------------------------------------------------------------------------

def _llm(prompt: str, llm: str = "none") -> str | None:
    try:
        if llm == "gemini" and os.environ.get("GOOGLE_API_KEY"):
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-pro").generate_content(prompt).text
        if llm == "openai" and os.environ.get("OPENAI_API_KEY"):
            from openai import OpenAI  # type: ignore
            return (
                OpenAI()
                .chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                )
                .choices[0]
                .message.content
            )
    except Exception:
        return None
    return None


# ---------------------------------------------------------------------------
# Role 1 — Researcher
# ---------------------------------------------------------------------------

def researcher(state: dict[str, Any]) -> dict[str, Any]:
    """Pick the top evidence snippets from RAG citations."""
    cites = state.get("citations", []) or []
    evidence = []
    for c in cites[:3]:
        snippet = (c.get("text") or "").strip().replace("\n", " ")
        if len(snippet) > 220:
            snippet = snippet[:217] + "…"
        evidence.append({
            "page": c.get("page"),
            "book": c.get("book"),
            "snippet": snippet,
        })
    return {"evidence": evidence, "evidence_count": len(evidence)}


# ---------------------------------------------------------------------------
# Role 2 — Curator
# ---------------------------------------------------------------------------

_DEFAULT_SEQUENCE = {
    "Lower back pain": [
        ("Warm-up", "Cat-Cow + Pelvic tilts (5 min)"),
        ("Main",    "Supported Bridge, Sphinx, Modified Locust (15 min)"),
        ("Cool-down", "Reclined twist + Legs-up-the-wall (10 min)"),
    ],
    "Pregnancy": [
        ("Warm-up", "Side-lying breathing + Cat-Cow (5 min)"),
        ("Main",    "Wide-leg supported squats, Goddess pose (15 min)"),
        ("Cool-down", "Side-lying Savasana with bolster (10 min)"),
    ],
    "Knee injury": [
        ("Warm-up", "Seated ankle circles + Reclined leg stretches (5 min)"),
        ("Main",    "Chair-supported Warrior II, Bridge variations (15 min)"),
        ("Cool-down", "Supine figure-4, Legs-up-the-wall (10 min)"),
    ],
    "Wrist injury": [
        ("Warm-up", "Forearm warm-up + shoulder rolls (5 min)"),
        ("Main",    "Forearm Plank, Dolphin, fist-supported Down Dog (15 min)"),
        ("Cool-down", "Child's pose with forearms, supine twist (10 min)"),
    ],
}


def curator(state: dict[str, Any]) -> dict[str, Any]:
    """Build a 3-step session consistent with safety + studio specs."""
    need = state.get("need") or "General"
    seq = _DEFAULT_SEQUENCE.get(need, [
        ("Warm-up", "Gentle breathing + joint mobility (5 min)"),
        ("Main",    "Studio's signature flow adapted to your level (20 min)"),
        ("Cool-down", "Savasana with guided relaxation (5 min)"),
    ])
    mods = state.get("safety_modifications", []) or []
    return {
        "sequence": [{"phase": p, "detail": d} for p, d in seq],
        "modifications": mods,
    }


# ---------------------------------------------------------------------------
# Role 3 — Marketer (KO-first concierge copy)
# ---------------------------------------------------------------------------

def _marketer_template(state: dict[str, Any], plan: dict[str, Any]) -> str:
    top = state.get("top_studio") or {}
    lang = state.get("lang", "en")
    seq_lines = " → ".join(s["phase"] for s in plan["sequence"])
    cite_str = (
        "; ".join(f"p.{e['page']}" for e in plan.get("evidence", []) if e.get("page"))
        or "—"
    )
    mods = " | ".join(plan.get("modifications", [])) or (
        "별도 수정 동작 없음" if lang == "ko" else "no modifications needed"
    )

    if lang == "ko":
        return (
            f"💡 **{top.get('studio', '추천 스튜디오')}** 을(를) 추천드립니다 "
            f"(매칭 {top.get('match_pct', 0)}%, 거리 {top.get('distance_km', 0)}km).\n"
            f"맞춤 세션: {seq_lines}.\n"
            f"안전 가이드: {mods}.\n"
            f"강사 자격: {', '.join(top.get('matched_certs', [])) or '일반'}. "
            f"근거: {cite_str}.\n"
            f"지금 예약하시면 첫 클래스 안전 상담을 무료로 제공합니다."
        )
    return (
        f"💡 We recommend **{top.get('studio', 'this studio')}** "
        f"(match {top.get('match_pct', 0)}%, {top.get('distance_km', 0)} km away).\n"
        f"Tailored session: {seq_lines}.\n"
        f"Safety guidance: {mods}.\n"
        f"Instructor credentials: {', '.join(top.get('matched_certs', [])) or 'general'}. "
        f"Cited: {cite_str}.\n"
        f"Book today for a complimentary first-class safety consult."
    )


def marketer(state: dict[str, Any], plan: dict[str, Any], llm: str = "none") -> dict[str, Any]:
    """Compose the final concierge copy. Uses LLM if available, else template."""
    if llm in ("gemini", "openai"):
        prompt = (
            "You are a Korean-first yoga concierge marketer. "
            f"User said: {state.get('query')!r}. "
            f"Need: {state.get('need')}. "
            f"Top studio: {state.get('top_studio')}. "
            f"Curated session: {plan.get('sequence')}. "
            f"Safety modifications: {plan.get('modifications')}. "
            f"Evidence: {plan.get('evidence')}. "
            f"Reply in {state.get('lang', 'en')} in 4 short sentences. "
            "Be warm, specific, and end with a soft CTA."
        )
        text = _llm(prompt, llm)
        if text:
            return {"copy": text.strip(), "engine": llm}
    return {"copy": _marketer_template(state, plan), "engine": "template"}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_crew(state: dict[str, Any], llm: str | None = None) -> dict[str, Any]:
    """Run Researcher → Curator → Marketer and return their joint output."""
    llm = llm or state.get("llm", "none")
    research = researcher(state)
    plan = {**research, **curator(state)}
    copy = marketer(state, plan, llm=llm)
    return {
        "evidence":      plan["evidence"],
        "sequence":      plan["sequence"],
        "modifications": plan["modifications"],
        "copy":          copy["copy"],
        "engine":        copy["engine"],
    }


if __name__ == "__main__":
    import json
    demo_state = {
        "query": "허리가 아픈데 강남에서 추천해줘",
        "lang": "ko",
        "need": "Lower back pain",
        "top_studio": {
            "studio": "Itaewon Therapy Yoga",
            "match_pct": 80.3,
            "distance_km": 5.02,
            "matched_specs": ["alignment", "back care", "therapy"],
            "matched_certs": ["Physical Therapy Specialist", "Yoga Therapist"],
        },
        "safety_modifications": [
            "Herniated disc / Lower back: Substitute supported bridge for full wheel.",
        ],
        "citations": [],
    }
    print(json.dumps(run_crew(demo_state), ensure_ascii=False, indent=2))
