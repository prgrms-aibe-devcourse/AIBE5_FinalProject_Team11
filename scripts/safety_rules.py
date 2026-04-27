"""
Pure safety-rule logic shared by the Streamlit demo and the LangGraph
orchestrator.  No UI / framework imports — safe for CLI + CI use.
"""

from __future__ import annotations

import difflib
import re

INJURY_RULES: dict[str, dict] = {
    "wrist": {
        "label": "Wrist injury / Carpal Tunnel",
        "synonyms": ["wrist", "손목", "carpal", "터널", "손", "hand pain"],
        "forbidden_tags": {"wrist", "arm balance", "plank", "chaturanga",
                           "downward dog", "handstand"},
        "modification": "Use blocks under hands, or make fists to keep wrists neutral.",
    },
    "lower_back": {
        "label": "Herniated disc / Lower back",
        "synonyms": ["herniated", "disc", "lower back", "허리", "디스크",
                     "sciatica", "좌골신경", "back pain", "lumbar"],
        "forbidden_tags": {"forward fold", "deep twist", "spine",
                           "back", "seated forward bend", "plow"},
        "modification": "Substitute supported bridge, gentle cat-cow, supine knee hugs.",
    },
    "knee": {
        "label": "Knee injury",
        "synonyms": ["knee", "무릎", "meniscus", "acl", "patella"],
        "forbidden_tags": {"knee", "lotus", "hero", "deep lunge", "pigeon"},
        "modification": "Keep knee tracking over second toe; use blocks/blankets.",
    },
    "pregnancy": {
        "label": "Pregnancy (2nd / 3rd trimester)",
        "synonyms": ["pregnant", "pregnancy", "임신", "prenatal", "출산",
                     "trimester"],
        "forbidden_tags": {"twist", "prone", "belly", "inversion",
                           "deep backbend", "core"},
        "modification": "Open twists only; avoid lying prone after week 20.",
    },
    "hypertension": {
        "label": "High blood pressure",
        "synonyms": ["hypertension", "high blood pressure", "고혈압", "bp"],
        "forbidden_tags": {"inversion", "headstand", "shoulder stand",
                           "handstand"},
        "modification": "Substitute legs-up-the-wall (Viparita Karani).",
    },
    "shoulder": {
        "label": "Shoulder injury",
        "synonyms": ["shoulder", "어깨", "rotator cuff", "frozen shoulder",
                     "오십견"],
        "forbidden_tags": {"shoulder", "chaturanga", "plank", "arm balance",
                           "downward dog"},
        "modification": "Lower knees in plank; skip chaturanga transitions.",
    },
    "neck": {
        "label": "Neck injury",
        "synonyms": ["neck", "목", "cervical", "거북목"],
        "forbidden_tags": {"neck", "headstand", "shoulder stand", "plow"},
        "modification": "Keep gaze neutral; skip cervical-loading inversions.",
    },
}


def _normalize(text: str) -> list[str]:
    return [t for t in re.split(r"[\s,./;:!?\-]+", text.lower()) if t]


def resolve_conditions(query: str, *, cutoff: float = 0.78) -> list[tuple[str, str, float]]:
    """Return [(rule_id, matched_synonym, score), ...] for a free-text query.

    Production swaps this for Typesense / Meilisearch with synonyms +
    typo tolerance + Kiwi morpheme analyzer.  This in-memory fuzzy match
    keeps demos and CI dependency-free.
    """
    if not query.strip():
        return []
    tokens = _normalize(query)
    hits: dict[str, tuple[str, float]] = {}
    for rule_id, rule in INJURY_RULES.items():
        for syn in rule["synonyms"]:
            syn_l = syn.lower()
            if syn_l in query.lower():
                score = 1.0
            else:
                best = 0.0
                for tok in tokens:
                    r = difflib.SequenceMatcher(None, tok, syn_l).ratio()
                    if r > best:
                        best = r
                score = best
            if score >= cutoff and score > hits.get(rule_id, ("", 0.0))[1]:
                hits[rule_id] = (syn, score)
    return sorted(
        [(rid, syn, sc) for rid, (syn, sc) in hits.items()],
        key=lambda x: -x[2],
    )
