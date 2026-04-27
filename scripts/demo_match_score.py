"""
aeogeo HEADLINE Demo: Studio / Instructor Match Score
=====================================================

This is the headline visual for the Modoo investor / judge video.

Match Score (per Modoo spec):
    score = 0.40 * physical_need_fit
          + 0.30 * proximity_score
          + 0.30 * specialization_score

Production stack (mapped to issue #4):
    - Geo:           PostGIS (ST_DWithin) + Kakao/Google Maps API
    - Search/NLU:    Typesense + Kiwi (KO morpheme analyzer)
    - RAG:           LlamaIndex over instructor manuals -> Pinecone
    - Orchestration: LangGraph (NLU -> Safety -> Match -> Generate)
    - Multi-agent:   CrewAI (Researcher + Curator + KO-Marketer)
    - LLM:           Gemini 1.5 Pro / HyperCLOVA X (KO copy)

This Streamlit page mocks Verified Studios in Seoul, computes the score
client-side, and renders a map + ranked list with a transparent breakdown
of *why* each studio matched.

Run:
    pip install streamlit pydeck
    streamlit run scripts/demo_match_score.py
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd
import pydeck as pdk
import streamlit as st

# ---------------------------------------------------------------------------
# Mock data (Verified Partner Studios in Seoul)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Studio:
    name: str
    lat: float
    lon: float
    specializations: frozenset[str]
    instructor_certs: frozenset[str]
    rating: float


STUDIOS: list[Studio] = [
    Studio("Gangnam Vinyasa House",  37.4979, 127.0276,
           frozenset({"vinyasa", "alignment"}),
           frozenset({"RYT-500", "Anatomy"}), 4.6),
    Studio("Sinsa Prenatal Studio",  37.5171, 127.0202,
           frozenset({"prenatal", "restorative"}),
           frozenset({"Prenatal Certified", "RYT-200"}), 4.8),
    Studio("Itaewon Therapy Yoga",   37.5347, 126.9947,
           frozenset({"therapy", "back care", "alignment"}),
           frozenset({"Physical Therapy Specialist", "Yoga Therapist"}), 4.9),
    Studio("Hongdae Power Flow",     37.5563, 126.9236,
           frozenset({"power", "vinyasa", "ashtanga"}),
           frozenset({"RYT-500"}), 4.4),
    Studio("Jamsil Senior Yoga",     37.5133, 127.1000,
           frozenset({"senior", "chair", "restorative"}),
           frozenset({"Senior Certified", "RYT-200"}), 4.7),
    Studio("Yongsan Iyengar Center", 37.5326, 126.9905,
           frozenset({"iyengar", "alignment", "back care"}),
           frozenset({"Iyengar Certified", "Anatomy"}), 4.8),
    Studio("Seongsu Hot Yoga",       37.5443, 127.0560,
           frozenset({"hot", "power"}),
           frozenset({"RYT-200"}), 4.2),
    Studio("Mapo Yin & Meditation",  37.5660, 126.9015,
           frozenset({"yin", "meditation", "restorative"}),
           frozenset({"Meditation Teacher", "RYT-200"}), 4.5),
]


# Maps a user-stated need to the studio specialization tags that satisfy it.
NEED_TO_SPECS: dict[str, set[str]] = {
    "Lower back pain":        {"therapy", "back care", "alignment", "iyengar", "restorative"},
    "Prenatal":               {"prenatal", "restorative"},
    "Stress / sleep":         {"yin", "restorative", "meditation"},
    "Build strength":         {"power", "vinyasa", "ashtanga", "hot"},
    "Senior / mobility":      {"senior", "chair", "restorative"},
    "General flexibility":    {"vinyasa", "iyengar", "alignment", "yin"},
}

# Instructor certifications that give a bonus for specific needs.
NEED_TO_CERTS: dict[str, set[str]] = {
    "Lower back pain":   {"Yoga Therapist", "Physical Therapy Specialist", "Iyengar Certified", "Anatomy"},
    "Prenatal":          {"Prenatal Certified"},
    "Stress / sleep":    {"Meditation Teacher"},
    "Build strength":    {"RYT-500"},
    "Senior / mobility": {"Senior Certified"},
    "General flexibility": {"RYT-500", "Anatomy"},
}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def proximity_score(distance_km: float, max_km: float) -> float:
    """1.0 when on top of the user, 0.0 at max_km, linear in between."""
    if distance_km >= max_km:
        return 0.0
    return 1.0 - (distance_km / max_km)


def need_fit_score(need: str, studio: Studio) -> tuple[float, list[str]]:
    wanted = NEED_TO_SPECS.get(need, set())
    if not wanted:
        return 0.0, []
    overlap = wanted & studio.specializations
    score = min(1.0, len(overlap) / 2.0)  # 2+ matching specs -> full marks
    return score, sorted(overlap)


def specialization_score(need: str, studio: Studio) -> tuple[float, list[str]]:
    wanted_certs = NEED_TO_CERTS.get(need, set())
    matched = sorted(wanted_certs & studio.instructor_certs)
    if not wanted_certs:
        cert_score = 0.5
    else:
        cert_score = min(1.0, len(matched) / max(1, min(2, len(wanted_certs))))
    # rating gives a small tiebreaker
    rating_score = (studio.rating - 4.0) / 1.0  # 4.0 -> 0, 5.0 -> 1
    rating_score = max(0.0, min(1.0, rating_score))
    return 0.7 * cert_score + 0.3 * rating_score, matched


def match_score(
    need: str,
    user_lat: float,
    user_lon: float,
    max_km: float,
) -> pd.DataFrame:
    rows = []
    for s in STUDIOS:
        dist = haversine_km(user_lat, user_lon, s.lat, s.lon)
        prox = proximity_score(dist, max_km)
        need_fit, need_overlap = need_fit_score(need, s)
        spec, cert_overlap = specialization_score(need, s)
        total = 0.40 * need_fit + 0.30 * prox + 0.30 * spec
        rows.append({
            "Studio": s.name,
            "Match %": round(total * 100, 1),
            "Need fit (40%)": round(need_fit * 100),
            "Proximity (30%)": round(prox * 100),
            "Specialization (30%)": round(spec * 100),
            "Distance (km)": round(dist, 2),
            "Matching specs": ", ".join(need_overlap) or "—",
            "Matching certs": ", ".join(cert_overlap) or "—",
            "Rating": s.rating,
            "lat": s.lat, "lon": s.lon,
        })
    return pd.DataFrame(rows).sort_values("Match %", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="aeogeo · Studio Match Score",
    page_icon="📍",
    layout="wide",
)

st.title("📍 aeogeo · Studio Match Score")
st.caption(
    "**Headline demo.** AI matches the user to the right *Verified Partner Studio* "
    "using a transparent score: Need 40% · Proximity 30% · Specialization 30%."
)

with st.sidebar:
    st.header("User input")
    need = st.selectbox(
        "Physical need / intent",
        options=list(NEED_TO_SPECS.keys()),
        index=0,
        help="In production this is extracted by NLU (Kiwi + LangGraph).",
    )
    location = st.selectbox(
        "Your location (Seoul)",
        options=["Gangnam Station", "Hongdae", "Itaewon", "Jamsil", "Mapo"],
        index=0,
    )
    LOC_COORDS = {
        "Gangnam Station": (37.4979, 127.0276),
        "Hongdae":         (37.5563, 126.9236),
        "Itaewon":         (37.5347, 126.9947),
        "Jamsil":          (37.5133, 127.1000),
        "Mapo":            (37.5660, 126.9015),
    }
    user_lat, user_lon = LOC_COORDS[location]
    max_km = st.slider("Max travel distance (km)", 1, 20, 8)

    st.divider()
    st.subheader("Production stack")
    st.markdown(
        "- **Geo** PostGIS + Kakao Map API\n"
        "- **NLU** Typesense + Kiwi (KO morpheme)\n"
        "- **RAG** LlamaIndex → Pinecone\n"
        "- **Orchestration** LangGraph state machine\n"
        "- **Agents** CrewAI (Researcher / Curator / KO-Marketer)\n"
        "- **LLM** Gemini 1.5 Pro / HyperCLOVA X"
    )

df = match_score(need, user_lat, user_lon, max_km)

# --- top match callout -------------------------------------------------------
top = df.iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("🥇 Top match", top["Studio"])
c2.metric("Match score", f"{top['Match %']}%")
c3.metric("Distance", f"{top['Distance (km)']} km")
c4.metric("Rating", f"⭐ {top['Rating']}")

st.markdown(
    f"**Why this match:** {top['Matching specs']}  ·  "
    f"instructor certs: *{top['Matching certs']}*"
)

st.divider()

left, right = st.columns([3, 2])

# --- map ---------------------------------------------------------------------
with left:
    st.subheader("Verified Partner Studios")
    map_df = df.copy()
    map_df["radius"] = 60 + map_df["Match %"] * 4
    map_df["color"] = map_df["Match %"].apply(
        lambda p: [int(255 * (1 - p / 100)), int(180 * (p / 100) + 50), 80, 200]
    )
    user_layer = pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame([{"lat": user_lat, "lon": user_lon}]),
        get_position="[lon, lat]",
        get_fill_color=[30, 144, 255, 220],
        get_radius=140,
        pickable=False,
    )
    studio_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lon, lat]",
        get_fill_color="color",
        get_radius="radius",
        pickable=True,
    )
    deck = pdk.Deck(
        layers=[studio_layer, user_layer],
        initial_view_state=pdk.ViewState(
            latitude=user_lat, longitude=user_lon, zoom=11.5,
        ),
        tooltip={"text": "{Studio}\nMatch: {Match %}%\nDist: {Distance (km)} km"},
    )
    st.pydeck_chart(deck)

# --- ranked list -------------------------------------------------------------
with right:
    st.subheader("Ranked matches")
    show = df[[
        "Studio", "Match %",
        "Need fit (40%)", "Proximity (30%)", "Specialization (30%)",
        "Distance (km)",
    ]]
    st.dataframe(show, hide_index=True, use_container_width=True)

st.divider()

# --- transparent breakdown for the top 3 -------------------------------------
st.subheader("Score breakdown (transparent — judges love this)")
for i in range(min(3, len(df))):
    row = df.iloc[i]
    with st.expander(f"#{i+1}  {row['Studio']}  —  {row['Match %']}%", expanded=(i == 0)):
        b1, b2, b3 = st.columns(3)
        b1.metric("Need fit (40%)", f"{row['Need fit (40%)']}%",
                  help=f"Matched specs: {row['Matching specs']}")
        b2.metric("Proximity (30%)", f"{row['Proximity (30%)']}%",
                  help=f"{row['Distance (km)']} km within {max_km} km radius")
        b3.metric("Specialization (30%)", f"{row['Specialization (30%)']}%",
                  help=f"Certs: {row['Matching certs']}  ·  Rating: {row['Rating']}")

st.caption(
    "The match is the moat. RAG + safety filter run as **infra** behind this — "
    "the user only sees the right studio at the right time."
)
