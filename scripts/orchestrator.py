"""
aeogeo Orchestrator (LangGraph state machine)
=============================================

Wires together every layer of the Modoo spec into one explicit graph:

    [user query]
         |
         v
     +-------+        +--------+        +-------+
     |  NLU  | -----> | Safety | -----> |  RAG  |
     +-------+        +--------+        +-------+
                          |                 |
                  (unsafe?)|                 v
                          |             +-------+
                          |             | Match |  <-- studio match score
                          |             +-------+
                          |                 |
                          v                 v
                       +---------------------+
                       |      Generate       |  <-- Gemini / HyperCLOVA X
                       +---------------------+
                                 |
                                 v
                          [final response]

Why LangGraph (per issue #4):
- LangChain is linear; real flows need loops + conditional edges.
- LangGraph is the most "reliable" choice for production-grade agents
  with precise state control.

Run:
    # Dry-run (no LLM keys, no network):
    python scripts/orchestrator.py --query "허리가 아픈데 강남에서 추천해줘"

    # With real LLM (set GOOGLE_API_KEY or OPENAI_API_KEY):
    python scripts/orchestrator.py --query "..." --llm gemini

This module imports langgraph lazily so the dry-run path works without
the dependency installed. When langgraph is missing, a minimal in-house
state machine with the same node signatures runs instead — same logic,
same trace output, useful for CI and the video screen-capture.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, TypedDict

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from math import asin, cos, radians, sin, sqrt  # noqa: E402

from safety_rules import INJURY_RULES, resolve_conditions  # type: ignore  # noqa: E402

log = logging.getLogger("orchestrator")


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class State(TypedDict, total=False):
    # input
    query: str
    user_lat: float
    user_lon: float
    max_km: float
    lang: str
    llm: str

    # NLU output
    intent: str
    need: str
    duration_min: int

    # Safety output
    forbidden_tags: list[str]
    safety_modifications: list[str]
    safety_block: bool

    # RAG output
    citations: list[dict]

    # Match output
    top_studio: dict
    ranked_studios: list[dict]

    # Generate output
    answer: str

    # Trace
    trace: list[dict]


def _trace(state: State, node: str, **payload) -> None:
    state.setdefault("trace", []).append({"node": node, **payload})


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

# --- 1. NLU ----------------------------------------------------------------

_NEED_HINTS = {
    "Lower back pain":   ("back", "허리", "disc", "디스크", "sciatica", "좌골", "lumbar"),
    "Prenatal":          ("pregnant", "임신", "prenatal", "출산"),
    "Stress / sleep":    ("stress", "sleep", "수면", "잠", "anxious", "불안", "calm"),
    "Build strength":    ("strength", "근력", "tone", "power", "강해"),
    "Senior / mobility": ("senior", "어르신", "mobility", "노인"),
    "General flexibility": ("flex", "유연", "stretch", "스트레칭"),
}

_DURATION_RE = __import__("re").compile(r"(\d+)\s*(?:min|m|분)")


def node_nlu(state: State) -> State:
    q = state["query"].lower()
    need = "General flexibility"
    for label, hints in _NEED_HINTS.items():
        if any(h in q for h in hints):
            need = label
            break
    duration = 15
    m = _DURATION_RE.search(state["query"])
    if m:
        duration = int(m.group(1))
    intent = "pain relief" if "pain" in q or "아프" in q or "통증" in q else "wellness"
    state["need"] = need
    state["intent"] = intent
    state["duration_min"] = duration
    state["lang"] = "ko" if any("\uac00" <= ch <= "\ud7a3" for ch in state["query"]) else "en"
    _trace(state, "nlu", need=need, intent=intent, duration_min=duration, lang=state["lang"])
    return state


# --- 2. Safety -------------------------------------------------------------

def node_safety(state: State) -> State:
    matches = resolve_conditions(state["query"])
    forbidden: set[str] = set()
    mods: list[str] = []
    for rid, _, _ in matches:
        rule = INJURY_RULES[rid]
        forbidden |= rule["forbidden_tags"]
        if rule["modification"]:
            mods.append(f"{rule['label']}: {rule['modification']}")
    state["forbidden_tags"] = sorted(forbidden)
    state["safety_modifications"] = mods
    state["safety_block"] = False  # block only on hard contraindications
    _trace(state, "safety",
           matched=[INJURY_RULES[rid]["label"] for rid, _, _ in matches],
           forbidden=sorted(forbidden))
    return state


# --- 3. RAG ----------------------------------------------------------------

RAG_INDEX_PATH = REPO_ROOT / "data" / "rag" / "index_generative-engine-optimization.jsonl"


def _bm25_lite(query: str, docs: list[dict], k: int = 3) -> list[dict]:
    """Tiny lexical scorer for the dry-run path. Production swaps to
    Pinecone vector search via LlamaIndex retriever."""
    import re as _re
    qtoks = set(_re.findall(r"\w+", query.lower()))
    if not qtoks:
        return []
    scored = []
    for d in docs:
        toks = set(_re.findall(r"\w+", d["text"].lower()))
        overlap = len(qtoks & toks)
        if overlap:
            scored.append((overlap, d))
    scored.sort(key=lambda x: -x[0])
    return [d for _, d in scored[:k]]


def node_rag(state: State) -> State:
    if not RAG_INDEX_PATH.exists():
        log.warning("No RAG index at %s — run scripts/rag_ingest.py first", RAG_INDEX_PATH)
        state["citations"] = []
        _trace(state, "rag", hits=0, source="missing_index")
        return state
    with RAG_INDEX_PATH.open(encoding="utf-8") as fh:
        docs = [json.loads(line) for line in fh]
    hits = _bm25_lite(state["query"], docs, k=3)
    state["citations"] = [
        {
            "chunk_id": h["chunk_id"],
            "page": h["page"],
            "type": h["chunk_type"],
            "snippet": h["text"][:240],
            "source": h["metadata"].get("source_path"),
        }
        for h in hits
    ]
    _trace(state, "rag", hits=len(hits), backend="jsonl-bm25-lite")
    return state


# --- 4. Match (studio score) -----------------------------------------------

@dataclass(frozen=True)
class _Studio:
    name: str
    lat: float
    lon: float
    specs: tuple[str, ...]
    certs: tuple[str, ...]
    rating: float


_STUDIOS = [
    _Studio("Gangnam Vinyasa House", 37.4979, 127.0276,
            ("vinyasa", "alignment"), ("RYT-500", "Anatomy"), 4.6),
    _Studio("Sinsa Prenatal Studio", 37.5171, 127.0202,
            ("prenatal", "restorative"),
            ("Prenatal Certified", "RYT-200"), 4.8),
    _Studio("Itaewon Therapy Yoga", 37.5347, 126.9947,
            ("therapy", "back care", "alignment"),
            ("Physical Therapy Specialist", "Yoga Therapist"), 4.9),
    _Studio("Hongdae Power Flow", 37.5563, 126.9236,
            ("power", "vinyasa", "ashtanga"), ("RYT-500",), 4.4),
    _Studio("Yongsan Iyengar Center", 37.5326, 126.9905,
            ("iyengar", "alignment", "back care"),
            ("Iyengar Certified", "Anatomy"), 4.8),
]

_NEED_TO_SPECS = {
    "Lower back pain":   {"therapy", "back care", "alignment", "iyengar", "restorative"},
    "Prenatal":          {"prenatal", "restorative"},
    "Stress / sleep":    {"yin", "restorative", "meditation"},
    "Build strength":    {"power", "vinyasa", "ashtanga"},
    "Senior / mobility": {"senior", "chair", "restorative"},
    "General flexibility": {"vinyasa", "iyengar", "alignment", "yin"},
}
_NEED_TO_CERTS = {
    "Lower back pain":   {"Yoga Therapist", "Physical Therapy Specialist", "Iyengar Certified", "Anatomy"},
    "Prenatal":          {"Prenatal Certified"},
    "Stress / sleep":    {"Meditation Teacher"},
    "Build strength":    {"RYT-500"},
    "Senior / mobility": {"Senior Certified"},
    "General flexibility": {"RYT-500", "Anatomy"},
}


def _km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * R * asin(sqrt(a))


def node_match(state: State) -> State:
    need = state["need"]
    user_lat = state.get("user_lat", 37.4979)
    user_lon = state.get("user_lon", 127.0276)
    max_km = state.get("max_km", 8.0)

    wanted_specs = _NEED_TO_SPECS.get(need, set())
    wanted_certs = _NEED_TO_CERTS.get(need, set())

    ranked = []
    for s in _STUDIOS:
        dist = _km(user_lat, user_lon, s.lat, s.lon)
        prox = max(0.0, 1.0 - dist / max_km)
        spec_overlap = wanted_specs & set(s.specs)
        need_fit = min(1.0, len(spec_overlap) / 2.0)
        cert_overlap = wanted_certs & set(s.certs)
        cert_score = min(1.0, len(cert_overlap) / max(1, min(2, len(wanted_certs)))) if wanted_certs else 0.5
        rating_score = max(0.0, min(1.0, (s.rating - 4.0)))
        spec = 0.7 * cert_score + 0.3 * rating_score
        total = 0.40 * need_fit + 0.30 * prox + 0.30 * spec
        ranked.append({
            "studio": s.name,
            "match_pct": round(total * 100, 1),
            "need_fit_pct": round(need_fit * 100),
            "proximity_pct": round(prox * 100),
            "specialization_pct": round(spec * 100),
            "distance_km": round(dist, 2),
            "matched_specs": sorted(spec_overlap),
            "matched_certs": sorted(cert_overlap),
            "rating": s.rating,
            "lat": s.lat,
            "lon": s.lon,
        })
    ranked.sort(key=lambda r: -r["match_pct"])
    state["ranked_studios"] = ranked
    state["top_studio"] = ranked[0]
    _trace(state, "match", top=ranked[0]["studio"], score=ranked[0]["match_pct"])
    return state


# --- 5. Generate -----------------------------------------------------------

def _llm_call(prompt: str, llm: str) -> str | None:
    try:
        if llm == "gemini" and os.environ.get("GOOGLE_API_KEY"):
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-pro").generate_content(prompt).text
        if llm == "openai" and os.environ.get("OPENAI_API_KEY"):
            from openai import OpenAI  # type: ignore
            client = OpenAI()
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            return r.choices[0].message.content
    except Exception as e:  # noqa: BLE001
        log.warning("LLM call failed (%s); falling back to template: %s", llm, e)
    return None


def _template_answer(state: State) -> str:
    top = state["top_studio"]
    cites = state.get("citations", [])
    cite_str = "; ".join(f"p.{c['page']}" for c in cites) or "—"
    mods = " | ".join(state.get("safety_modifications", [])) or "no modifications needed"
    if state.get("lang") == "ko":
        return (
            f"추천 스튜디오: **{top['studio']}** (매칭 {top['match_pct']}%, "
            f"거리 {top['distance_km']}km).\n"
            f"이유: {', '.join(top['matched_specs']) or '전문 분야 매칭'}. "
            f"강사 자격: {', '.join(top['matched_certs']) or '일반'}.\n"
            f"안전 가이드: {mods}.\n"
            f"근거 매뉴얼: {cite_str}."
        )
    return (
        f"Top studio: **{top['studio']}** (match {top['match_pct']}%, "
        f"{top['distance_km']} km away).\n"
        f"Why: specs {top['matched_specs']}, certs {top['matched_certs']}.\n"
        f"Safety: {mods}.\n"
        f"Cited from instructor manual pages: {cite_str}."
    )


def node_generate(state: State) -> State:
    if state.get("use_crew"):
        from crew_roles import run_crew  # local import keeps base path light
        crew_out = run_crew(state, llm=state.get("llm", "none"))
        state["answer"] = crew_out["copy"]
        state["crew"] = {
            "sequence":      crew_out["sequence"],
            "modifications": crew_out["modifications"],
            "evidence":      crew_out["evidence"],
            "engine":        crew_out["engine"],
        }
        _trace(state, "generate", engine=f"crew:{crew_out['engine']}",
               chars=len(crew_out["copy"]))
        return state

    prompt = (
        f"You are a yoga concierge. User said: {state['query']!r}.\n"
        f"Top studio: {state['top_studio']}.\n"
        f"Safety modifications: {state.get('safety_modifications', [])}.\n"
        f"RAG citations: {state.get('citations', [])}.\n"
        f"Reply in {state.get('lang', 'en')}, 3 short sentences, cite pages."
    )
    answer = _llm_call(prompt, state.get("llm", "none")) or _template_answer(state)
    state["answer"] = answer
    _trace(state, "generate", llm=state.get("llm", "template"),
           chars=len(answer))
    return state


# ---------------------------------------------------------------------------
# Graph wiring (LangGraph if available, fallback otherwise)
# ---------------------------------------------------------------------------

NODES: dict[str, Callable[[State], State]] = {
    "nlu":      node_nlu,
    "safety":   node_safety,
    "rag":      node_rag,
    "match":    node_match,
    "generate": node_generate,
}

EDGES = [("nlu", "safety"), ("safety", "rag"), ("rag", "match"), ("match", "generate")]


def _run_fallback(state: State) -> State:
    order = ["nlu", "safety", "rag", "match", "generate"]
    for n in order:
        state = NODES[n](state)
    return state


def run_graph(state: State) -> State:
    try:
        from langgraph.graph import END, StateGraph  # type: ignore
    except ImportError:
        log.info("langgraph not installed — using built-in fallback runner")
        return _run_fallback(state)

    g: Any = StateGraph(dict)
    for name, fn in NODES.items():
        g.add_node(name, fn)
    g.set_entry_point("nlu")
    for src, dst in EDGES:
        g.add_edge(src, dst)
    g.add_edge("generate", END)
    app = g.compile()
    return app.invoke(state)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="aeogeo LangGraph orchestrator")
    p.add_argument("--query", required=True)
    p.add_argument("--lat", type=float, default=37.4979)
    p.add_argument("--lon", type=float, default=127.0276)
    p.add_argument("--max-km", type=float, default=8.0)
    p.add_argument("--llm", choices=["none", "gemini", "openai"], default="none")
    p.add_argument("--crew", action="store_true",
                   help="Use CrewAI roles (Researcher+Curator+Marketer) in generate node")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s | %(message)s",
    )

    state: State = {
        "query": args.query,
        "user_lat": args.lat,
        "user_lon": args.lon,
        "max_km": args.max_km,
        "llm": args.llm,
        "use_crew": args.crew,
    }
    final = run_graph(state)

    print(json.dumps({
        "query":   final["query"],
        "need":    final.get("need"),
        "lang":    final.get("lang"),
        "top":     final.get("top_studio"),
        "safety":  final.get("safety_modifications"),
        "cites":   final.get("citations"),
        "answer":  final.get("answer"),
        "crew":    final.get("crew"),
        "trace":   final.get("trace"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
