"""
CrewAI role-based crew for GEO marketing copy generation (T-033).

Crew composition:
    Analyst  — reads location context (time of day, nearby landmarks, weather proxy)
    Matcher  — selects top 3 poses + 1 studio from match results
    Writer   — generates natural 해요체 Korean + English GEO marketing copy

Usage::

    from app.agents.crew import run_crew

    state = {
        "lat": 37.4979, "lng": 127.0276,
        "top_poses": [{"poseId": "cat_cow", ...}],
        "top_studio": {"name": "강남 요가 센터", ...},
        "goals": ["Spinal_Mobility"],
    }
    copy_ko, copy_en = run_crew(state)
    print(copy_ko)

Dependencies:
    pip install crewai crewai-tools
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, Tuple


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _time_context() -> str:
    h = datetime.now().hour
    if 6 <= h < 10:
        return "이른 아침"
    elif 10 <= h < 12:
        return "오전"
    elif 12 <= h < 14:
        return "점심시간"
    elif 14 <= h < 18:
        return "오후"
    elif 18 <= h < 21:
        return "저녁"
    else:
        return "밤"


def _district_hint(lat: float, lng: float) -> str:
    """Cheap lookup — matches approximate Seoul district bounding boxes."""
    districts = [
        (37.4979, 127.0276, "강남역"),
        (37.5563, 126.9235, "홍대"),
        (37.5700, 126.9822, "종로"),
        (37.5173, 127.0473, "잠실"),
    ]
    closest = min(districts, key=lambda d: math.hypot(d[0] - lat, d[1] - lng))
    dist = math.hypot(closest[0] - lat, closest[1] - lng)
    return closest[2] if dist < 0.03 else f"({lat:.3f}, {lng:.3f})"


# ---------------------------------------------------------------------------
# Template fallback (used when crewai is not installed)
# ---------------------------------------------------------------------------

def _template_copy(state: Dict[str, Any]) -> Tuple[str, str]:
    time_ctx = _time_context()
    district = _district_hint(state.get("lat", 0), state.get("lng", 0))
    poses = [p.get("poseId", "") for p in state.get("top_poses", [])]
    studio = state.get("top_studio")

    ko_lines = [f"{time_ctx} {district} — 오늘의 요가 추천드릴게요 🧘"]
    if poses:
        ko_lines.append(f"추천 포즈: {' · '.join(poses)}")
    if studio:
        ko_lines.append(f"가까운 스튜디오: {studio.get('name', '')} ({studio.get('city', '')})")

    en_lines = [f"{time_ctx} at {district} — Today's yoga recommendation"]
    if poses:
        en_lines.append(f"Recommended: {', '.join(poses)}")
    if studio:
        en_lines.append(f"Nearby: {studio.get('name', '')}")

    return "\n".join(ko_lines), "\n".join(en_lines)


# ---------------------------------------------------------------------------
# CrewAI crew
# ---------------------------------------------------------------------------

def build_crew(ollama_base_url: str = "http://localhost:11434", model: str = "mistral"):
    """Build and return the CrewAI Crew instance.
    
    Requires: pip install crewai
    """
    try:
        from crewai import Agent, Crew, Task
        from langchain_community.llms import Ollama
    except ImportError as e:
        raise ImportError(
            "crewai and langchain-community are required: "
            "pip install crewai langchain-community"
        ) from e

    llm = Ollama(model=model, base_url=ollama_base_url)

    analyst = Agent(
        role="GEO Context Analyst",
        goal=(
            "사용자의 위경도, 현재 시간, 지역 상권 정보를 분석하여 "
            "마케팅 문구 작성에 필요한 컨텍스트 요약문을 작성한다."
        ),
        backstory=(
            "당신은 한국 도시 상권 전문가입니다. 위경도와 시간대를 보고 "
            "그 장소가 강남 직장인 밀집 지역인지, 홍대 젊은층 지역인지, "
            "주택가인지 파악하여 마케팅 전략의 기반 컨텍스트를 제공합니다."
        ),
        llm=llm,
        verbose=False,
    )

    matcher = Agent(
        role="Yoga Pose Matcher",
        goal=(
            "매칭 점수와 금기사항 데이터를 보고 사용자에게 "
            "가장 적합한 포즈 3개와 인근 스튜디오 1곳을 선정한다."
        ),
        backstory=(
            "당신은 FYT100 자격증을 보유한 요가 전문가입니다. "
            "포즈의 난이도, 효능 태그, 금기사항을 종합적으로 검토하여 "
            "사용자에게 안전하고 효과적인 포즈를 추천합니다."
        ),
        llm=llm,
        verbose=False,
    )

    writer = Agent(
        role="Korean GEO Copywriter",
        goal=(
            "Analyst와 Matcher의 결과를 바탕으로 "
            "자연스러운 한국어(해요체) GEO 마케팅 문구를 생성한다. "
            "이모지를 적절히 사용하고 150자 이내로 작성한다."
        ),
        backstory=(
            "당신은 한국어 마케팅 카피라이터입니다. "
            "고객의 현재 위치, 시간대, 요가 목표를 반영한 "
            "즉각적인 행동 유도(CTA)가 포함된 문구를 작성합니다. "
            "예: '비 오는 강남역 점심, 뻐근한 어깨를 풀어드릴게요 🧘'"
        ),
        llm=llm,
        verbose=False,
    )

    return analyst, matcher, writer, Crew


def run_crew(state: Dict[str, Any]) -> Tuple[str, str]:
    """Run the crew and return (copy_ko, copy_en).
    
    Falls back to template copy if crewai is unavailable.
    """
    try:
        from crewai import Crew, Task

        analyst, matcher, writer, CrewClass = build_crew()
        time_ctx = _time_context()
        district = _district_hint(state.get("lat", 0.0), state.get("lng", 0.0))
        poses = [p.get("poseId", "") for p in state.get("top_poses", [])]
        studio = state.get("top_studio", {})

        analyze_task = Task(
            description=(
                f"현재 위치: {district}, 시간대: {time_ctx}. "
                f"이 컨텍스트에서 요가 마케팅에 활용할 수 있는 "
                f"상황 요약문을 2문장으로 작성하세요."
            ),
            agent=analyst,
        )

        match_task = Task(
            description=(
                f"추천 포즈 목록: {poses}. "
                f"인근 스튜디오: {studio.get('name', '없음')}. "
                f"이 중 마케팅 문구에 포함할 포즈 2개와 스튜디오를 선정하고 "
                f"이유를 한 줄로 설명하세요."
            ),
            agent=matcher,
        )

        write_task = Task(
            description=(
                "위 분석 결과를 바탕으로 한국어(해요체) 마케팅 문구를 작성하세요. "
                "150자 이내, 이모지 1개 포함, 즉각적인 행동 유도 포함. "
                "영어 번역도 함께 제공하세요. "
                "형식: KO: <한국어 문구>\\nEN: <English copy>"
            ),
            agent=writer,
        )

        crew = CrewClass(
            agents=[analyst, matcher, writer],
            tasks=[analyze_task, match_task, write_task],
            verbose=False,
        )
        result = str(crew.kickoff())

        copy_ko, copy_en = _template_copy(state)
        for line in result.splitlines():
            if line.startswith("KO:"):
                copy_ko = line[3:].strip()
            elif line.startswith("EN:"):
                copy_en = line[3:].strip()

        return copy_ko, copy_en

    except Exception:
        return _template_copy(state)
