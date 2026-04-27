"""
aeogeo Demo (supporting): AEO Safety Filter
===========================================

This is a SUPPORTING demo for the video, not the headline.
The headline is the Studio/Instructor Match Score (see
`scripts/demo_match_score.py`).

Flow:
    User TYPES their injury / constraint in natural language
        -> Free-text search resolves it to canonical condition tags
           (production: Typesense / Meilisearch typo-tolerant index;
            this demo: in-memory token + difflib fuzzy match)
        -> Safety Filter rule engine cross-references contraindications
        -> Dangerous poses are grayed out *before* the LLM is invoked.

Why a search box (not a dropdown):
    Real users type "my wrist hurts", "손목이 아파요", "sciatica",
    "40주 임신". A dropdown can't cover that long tail; Typesense /
    Meilisearch with synonyms + typo tolerance can.

Run:
    pip install streamlit
    streamlit run scripts/demo_safety_filter.py
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from safety_rules import INJURY_RULES, resolve_conditions

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
POSES_PATH = REPO_ROOT / "data" / "poses" / "poses_eat_schema.json"


@st.cache_data
def load_poses() -> list[dict]:
    with POSES_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _pose_tags(pose: dict) -> set[str]:
    """Collect every tag we will match against forbidden_tags."""
    tags: set[str] = set()

    for t in pose.get("anatomical_focus", []) or []:
        tags.add(str(t).lower())

    matching = pose.get("matching_logic") or {}
    for b in matching.get("benefits", []) or []:
        tag = b.get("tag") if isinstance(b, dict) else b
        if tag:
            tags.add(str(tag).lower())
    for c in matching.get("contraindications", []) or []:
        tag = c.get("tag") if isinstance(c, dict) else c
        if tag:
            tags.add(str(tag).lower())

    for k in pose.get("geo_keywords", []) or []:
        tags.add(str(k).lower())

    # also scan the canonical/common name so demo data without rich tags
    # still triggers visibly (e.g. "Downward Dog" -> wrist rule)
    for field in ("canonical_name", "common_name"):
        name = pose.get(field) or ""
        tags.add(name.lower())

    return tags


def is_unsafe(pose: dict, forbidden: set[str]) -> tuple[bool, list[str]]:
    """Return (unsafe, matched_terms)."""
    if not forbidden:
        return False, []
    tags = _pose_tags(pose)
    matched = [
        f for f in forbidden
        if any(f in tag for tag in tags)
    ]
    return bool(matched), matched


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="aeogeo · AEO Safety Filter",
    page_icon="🧘",
    layout="wide",
)

st.title("🧘 aeogeo · AEO Safety Filter")
st.caption(
    "Supporting demo — the headline is the Studio Match Score. "
    "This screen shows the safety guardrail that runs **before** the LLM."
)

with st.sidebar:
    st.header("User Constraints")
    query = st.text_input(
        "Describe your injury or condition",
        value="my wrist hurts",
        help="Free-text. Production uses Typesense / Meilisearch with synonyms + typo tolerance.",
    )
    duration = st.slider("Available time (minutes)", 5, 60, 15, step=5)
    intent = st.text_input("Intent (e.g. pain relief, calm)", "pain relief")

    st.divider()
    st.subheader("AI Engine (production)")
    st.markdown(
        "- **Search/NLU** → Typesense + Kiwi (KO morpheme) → condition tags\n"
        "- **Safety Filter** → this layer (rule engine)\n"
        "- **RAG** → LlamaIndex → Pinecone over instructor manuals\n"
        "- **Orchestration** → LangGraph state machine\n"
        "- **LLM** → Gemini 1.5 Pro / HyperCLOVA X (KO)\n"
        "- **GEO** → Match Score → studio referral (headline)"
    )

poses = load_poses()

matches = resolve_conditions(query)
if matches:
    forbidden: set[str] = set()
    for rid, _, _ in matches:
        forbidden |= INJURY_RULES[rid]["forbidden_tags"]
    primary = INJURY_RULES[matches[0][0]]
    st.success(
        "Resolved conditions: "
        + ", ".join(
            f"**{INJURY_RULES[rid]['label']}** (matched `{syn}`, {sc:.0%})"
            for rid, syn, sc in matches
        )
    )
else:
    forbidden = set()
    primary = None
    if query.strip():
        st.warning("No condition recognized — showing full catalog. Try: wrist, sciatica, 임신, knee.")

# --- summary metrics --------------------------------------------------------
unsafe_flags = [is_unsafe(p, forbidden) for p in poses]
n_total = len(poses)
n_unsafe = sum(1 for u, _ in unsafe_flags if u)
n_safe = n_total - n_unsafe

c1, c2, c3, c4 = st.columns(4)
c1.metric("Poses in catalog", n_total)
c2.metric("✅ Safe", n_safe)
c3.metric("⛔ Filtered out", n_unsafe)
c4.metric("Intent", intent or "—")

if primary and primary["modification"]:
    st.info(f"**Suggested modification:** {primary['modification']}")

st.divider()

# --- pose grid --------------------------------------------------------------
label = primary["label"] if primary else "none"
st.subheader(f"Catalog · injury filter = `{label}`")

show_unsafe = st.toggle(
    "Show unsafe poses (grayed out)", value=True,
    help="Turn off to see only the safe sequence the LLM would generate.",
)

GRID_COLS = 3
cols = st.columns(GRID_COLS)

# limit demo render for speed
MAX_RENDER = 60
rendered = 0

for idx, (pose, (unsafe, matched)) in enumerate(zip(poses, unsafe_flags)):
    if unsafe and not show_unsafe:
        continue
    if rendered >= MAX_RENDER:
        break

    name = pose.get("common_name") or pose.get("canonical_name") or pose.get("pose_id", "?")
    name = name.strip()[:90]
    summary = (
        (pose.get("educational_metadata") or {}).get("aeo_summary") or ""
    ).strip()
    summary = summary[:180] + ("…" if len(summary) > 180 else "")

    col = cols[rendered % GRID_COLS]
    with col:
        if unsafe:
            st.markdown(
                f"<div style='opacity:0.35;border:1px solid #aa3333;"
                f"border-radius:8px;padding:10px;margin-bottom:8px;'>"
                f"<b>⛔ {name}</b><br>"
                f"<small><i>Filtered: {', '.join(matched) or 'rule match'}</i></small><br>"
                f"<small>{summary}</small>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='border:1px solid #2e7d32;border-radius:8px;"
                f"padding:10px;margin-bottom:8px;background:#0d1f10;'>"
                f"<b>✅ {name}</b><br>"
                f"<small>{summary}</small>"
                f"</div>",
                unsafe_allow_html=True,
            )
    rendered += 1

st.divider()
st.caption(
    "Knowledge base = 20 years of certified instructor manuals (RAG fuel). "
    "AI = engine. Safety filter = the moat."
)
