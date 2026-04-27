"""
aeogeo JSON-LD AEO emitter
==========================

Emits schema.org JSON-LD for:
  - SportsActivityLocation (the matched studio)
  - FAQPage              (the user's pain query + concierge answer)
  - HowTo                (the curated session sequence, when present)

This is the "AEO proof point" that makes the platform readable by
generative answer engines (Google AI Overviews, Perplexity, Naver Cue).

Pure stdlib. No network. Deterministic ordering for diff-friendly output.

CLI:
    python scripts/jsonld_aeo.py --query "허리가 아픈데 강남에서 추천해줘"

Or import:
    from jsonld_aeo import build_jsonld
    snippet = build_jsonld(orchestrator_state)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _studio_node(top: dict[str, Any], user_lat: float | None, user_lon: float | None) -> dict[str, Any]:
    node: dict[str, Any] = {
        "@type": "SportsActivityLocation",
        "@id": f"#studio-{top.get('studio', 'unknown').replace(' ', '-').lower()}",
        "name": top.get("studio"),
        "sport": "Yoga",
        "amenityFeature": [
            {"@type": "LocationFeatureSpecification", "name": s, "value": True}
            for s in top.get("matched_specs", [])
        ],
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "instructorCertification", "value": c}
            for c in top.get("matched_certs", [])
        ],
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": top.get("rating", 4.5),
            "bestRating": 5,
        },
    }
    if "lat" in top and "lon" in top:
        node["geo"] = {"@type": "GeoCoordinates", "latitude": top["lat"], "longitude": top["lon"]}
    if user_lat is not None and user_lon is not None:
        node["potentialAction"] = {
            "@type": "ReserveAction",
            "name": "Book a class",
            "target": "https://aeogeo.app/book",
            "actionStatus": "PotentialActionStatus",
        }
    return node


def _faq_node(query: str, answer: str, lang: str) -> dict[str, Any]:
    return {
        "@type": "FAQPage",
        "inLanguage": lang or "ko",
        "mainEntity": [
            {
                "@type": "Question",
                "name": query,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer,
                },
            }
        ],
    }


def _howto_node(crew: dict[str, Any], need: str | None) -> dict[str, Any] | None:
    seq = (crew or {}).get("sequence") or []
    if not seq:
        return None
    return {
        "@type": "HowTo",
        "name": f"Adapted yoga session for {need or 'general practice'}",
        "step": [
            {
                "@type": "HowToStep",
                "position": i + 1,
                "name": s.get("phase"),
                "text": s.get("detail"),
            }
            for i, s in enumerate(seq)
        ],
    }


def build_jsonld(state: dict[str, Any]) -> dict[str, Any]:
    """Return a single schema.org JSON-LD document (@graph) from state."""
    top = state.get("top_studio") or {}
    answer = state.get("answer") or ""
    lang = state.get("lang") or "ko"
    crew = state.get("crew") or {}

    graph: list[dict[str, Any]] = [
        _studio_node(top, state.get("user_lat"), state.get("user_lon")),
        _faq_node(state.get("query", ""), answer, lang),
    ]
    howto = _howto_node(crew, state.get("need"))
    if howto:
        graph.append(howto)

    return {"@context": "https://schema.org", "@graph": graph}


def to_script_tag(doc: dict[str, Any]) -> str:
    """Wrap the JSON-LD doc in a <script> tag ready for the Flutter web shell."""
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(doc, ensure_ascii=False, indent=2)
        + "\n</script>"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Emit schema.org JSON-LD from orchestrator state")
    p.add_argument("--query", default="허리가 아픈데 강남에서 추천해줘")
    p.add_argument("--lat", type=float, default=37.4979)
    p.add_argument("--lon", type=float, default=127.0276)
    p.add_argument("--script-tag", action="store_true",
                   help="Wrap output in <script type=application/ld+json>")
    args = p.parse_args(argv)

    from orchestrator import State, run_graph  # type: ignore
    state: State = {
        "query": args.query,
        "user_lat": args.lat,
        "user_lon": args.lon,
        "max_km": 8.0,
        "llm": "none",
        "use_crew": True,
    }
    final = run_graph(state)
    doc = build_jsonld(final)
    print(to_script_tag(doc) if args.script_tag else json.dumps(doc, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
