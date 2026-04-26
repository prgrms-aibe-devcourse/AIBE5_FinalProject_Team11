"""
LangGraph state machine for the Elbee GEO matching pipeline.

Pipeline:
  parse_input → parallel_fetch → score_and_rank → crew_generate → return_response

Parallel fetch branches:
  ├─ find_nearby_studios  (calls /api/v1/studios/nearby)
  ├─ run_kill_switch      (filter contraindicated poses)
  └─ llama_index_retrieve (semantic pose chunk retrieval)

Usage::

    from app.agents.graph import build_graph, run_pipeline

    graph = build_graph()

    result = run_pipeline(graph, {
        "lat": 37.5665,
        "lng": 126.9780,
        "goals": ["Spinal_Mobility"],
        "health_flags": [],
        "experience_level": "BEGINNER",
        "available_minutes": 30,
    })
    print(result["crew_copy_ko"])

Dependencies:
    pip install langgraph langchain-core httpx
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

# ---------------------------------------------------------------------------
# State schema
# ---------------------------------------------------------------------------

class AgentState(TypedDict, total=False):
    # ── Input ──────────────────────────────────────────────────────────────
    lat: float
    lng: float
    goals: List[str]
    health_flags: List[str]
    experience_level: str
    available_minutes: int

    # ── Intermediate ───────────────────────────────────────────────────────
    expanded_goals: List[str]
    nearby_studios: List[Dict[str, Any]]
    blocked_pose_ids: List[str]
    retrieved_chunks: List[Dict[str, Any]]
    match_results: List[Dict[str, Any]]

    # ── Output ─────────────────────────────────────────────────────────────
    crew_copy_ko: str
    crew_copy_en: str
    top_poses: List[Dict[str, Any]]
    top_studio: Optional[Dict[str, Any]]
    error: Optional[str]


# ---------------------------------------------------------------------------
# GOAL_TAG_MAP  (mirrors MatchService.java)
# ---------------------------------------------------------------------------

GOAL_TAG_MAP: Dict[str, List[str]] = {
    "Spinal_Mobility":  ["mobility", "back", "flexibility", "release"],
    "Back_Pain_Relief": ["back", "relief", "stress", "posture"],
    "Core_Strength":    ["core", "strength", "stability"],
    "Hip_Flexibility":  ["hip", "flexibility", "mobility", "release"],
    "Balance":          ["balance", "stability"],
    "Stress_Relief":    ["stress", "relief", "release"],
    "Shoulder_Opening": ["shoulder", "release", "flexibility"],
    "Strength":         ["strength", "core", "stability"],
}


# ---------------------------------------------------------------------------
# Node functions (stubs — implement per T-031)
# ---------------------------------------------------------------------------

def parse_input(state: AgentState) -> AgentState:
    """Validate input and expand goals via GOAL_TAG_MAP."""
    goals = state.get("goals", [])
    expanded: List[str] = []
    for g in goals:
        expanded.extend(GOAL_TAG_MAP.get(g, [g.lower()]))
    return {**state, "expanded_goals": list(set(expanded))}


def find_nearby_studios(state: AgentState) -> AgentState:
    """Call /api/v1/studios/nearby and populate nearby_studios."""
    import httpx
    try:
        r = httpx.get(
            "http://localhost:19090/api/v1/studios/nearby",
            params={
                "lat": state["lat"],
                "lng": state["lng"],
                "radius": 10,
            },
            timeout=5.0,
        )
        studios = [item["studio"] for item in r.json()] if r.is_success else []
    except Exception:
        studios = []
    return {**state, "nearby_studios": studios}


def run_kill_switch(state: AgentState) -> AgentState:
    """Identify poses to block based on health_flags.
    
    Full implementation requires calling /api/v1/match or reading
    contraindications directly from the DB.  Stub returns empty block list.
    """
    return {**state, "blocked_pose_ids": []}


def llama_index_retrieve(state: AgentState) -> AgentState:
    """Retrieve semantically relevant pose chunks via LlamaIndex.
    
    Falls back to empty list if the index is not yet built (T-032).
    """
    try:
        from app.agents.pose_index import get_query_engine
        qe = get_query_engine()
        query = " ".join(state.get("expanded_goals", state.get("goals", [])))
        response = qe.query(query)
        chunks = [{"text": str(response), "score": 1.0}]
    except Exception:
        chunks = []
    return {**state, "retrieved_chunks": chunks}


def score_and_rank(state: AgentState) -> AgentState:
    """Call /api/v1/match and store ranked results."""
    import httpx
    try:
        r = httpx.post(
            "http://localhost:19090/api/v1/match",
            json={
                "goals": state.get("goals", []),
                "healthFlags": state.get("health_flags", []),
                "experienceLevel": state.get("experience_level", "BEGINNER"),
                "availableMinutes": state.get("available_minutes", 30),
                "topK": 5,
            },
            timeout=10.0,
        )
        results = r.json() if r.is_success else []
    except Exception:
        results = []

    top_poses = [r for r in results if not r.get("blocked")][:3]
    top_studio = state.get("nearby_studios", [None])[0] if state.get("nearby_studios") else None

    return {**state, "match_results": results, "top_poses": top_poses, "top_studio": top_studio}


def crew_generate(state: AgentState) -> AgentState:
    """Delegate to CrewAI crew for Korean GEO copy generation.
    
    Falls back to a template if crewai is not installed (T-033).
    """
    try:
        from app.agents.crew import run_crew
        copy_ko, copy_en = run_crew(state)
    except Exception:
        poses = [p.get("poseId", "") for p in state.get("top_poses", [])]
        studio = state.get("top_studio", {})
        studio_name = studio.get("name", "") if studio else ""
        copy_ko = f"추천 포즈: {', '.join(poses)}"
        if studio_name:
            copy_ko += f" — 가까운 스튜디오: {studio_name}"
        copy_en = f"Recommended poses: {', '.join(poses)}"

    return {**state, "crew_copy_ko": copy_ko, "crew_copy_en": copy_en}


def return_response(state: AgentState) -> AgentState:
    """Final passthrough — state IS the response."""
    return state


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_graph():
    """Construct and compile the LangGraph state machine.
    
    Returns a compiled graph ready to invoke.
    Requires: pip install langgraph
    """
    try:
        from langgraph.graph import StateGraph, END
    except ImportError as e:
        raise ImportError(
            "langgraph is required: pip install langgraph langchain-core"
        ) from e

    g = StateGraph(AgentState)

    g.add_node("parse_input", parse_input)
    g.add_node("find_nearby_studios", find_nearby_studios)
    g.add_node("run_kill_switch", run_kill_switch)
    g.add_node("llama_index_retrieve", llama_index_retrieve)
    g.add_node("score_and_rank", score_and_rank)
    g.add_node("crew_generate", crew_generate)
    g.add_node("return_response", return_response)

    g.set_entry_point("parse_input")
    g.add_edge("parse_input", "find_nearby_studios")
    g.add_edge("parse_input", "run_kill_switch")
    g.add_edge("parse_input", "llama_index_retrieve")
    g.add_edge("find_nearby_studios", "score_and_rank")
    g.add_edge("run_kill_switch", "score_and_rank")
    g.add_edge("llama_index_retrieve", "score_and_rank")
    g.add_edge("score_and_rank", "crew_generate")
    g.add_edge("crew_generate", "return_response")
    g.add_edge("return_response", END)

    return g.compile()


def run_pipeline(graph, input_state: Dict[str, Any]) -> AgentState:
    """Convenience wrapper to invoke the compiled graph."""
    return graph.invoke(input_state)
