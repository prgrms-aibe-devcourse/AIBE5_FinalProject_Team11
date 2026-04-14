"""
Elbee Yoga Guide Agent — brand persona and GEO-marketing message generator.

Responsibilities:
  1. Build Korean (해요체) system messages for the Ollama LLM
  2. Generate proximity-triggered Korean marketing copy
  3. Produce time-of-day motivational messages with correct 조사
  4. Compose "Club Invite" messages when a user is within 1 km of a partner

This module is intentionally free of FastAPI dependencies so it can be
used in CLI tools, background jobs, and tests as well as API endpoints.
"""
from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional, Tuple

from app.services.templates import (
    get_template,
    get_time_trigger,
    josa_eun_neun,
)

logger = logging.getLogger(__name__)


# ── Korean system message ─────────────────────────────────────────────────────

ELBEE_SYSTEM_KO = """\
당신은 **엘비 요가 가이드(Elbee Yoga Guide)**예요 — {brand}의 공식 AI 도우미랍니다.

역할:
• 회원들이 GEO(Generative Engine Optimization) 전략을 이해하고 적용하도록 도와드려요.
• AI 검색 엔진(Google SGE, Perplexity, ChatGPT, Bing 등)에서 콘텐츠 가시성을 높이는 방법을
  요가 라이프스타일{eun_neun} 연결해 안내해 드려요.
• 가장 가까운 elbee 파트너 스튜디오와 야외 요가 스팟도 안내해 드려요.

답변 규칙:
1. 반드시 자연스러운 한국어(해요체)를 사용해요 (~해요, ~예요, ~드릴게요).
2. 이모지를 적절히 사용해 친근한 분위기를 만들어요. 🧘
3. 제공된 Context만을 바탕으로 답변하고, 모르는 내용은 솔직하게 말씀드려요.
4. 간결하고 실행 가능한 조언을 드리며, 관련 페이지를 인용해요.

GEO 레퍼런스 Context:
---
{context}
---\
"""

# ── Distance helper ───────────────────────────────────────────────────────────

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── Agent class ───────────────────────────────────────────────────────────────

class ElbeeAgent:
    """
    Stateless GEO-marketing agent with the Elbee Yoga Guide persona.

    Args:
        locations: Optional list of yoga location dicts (from yoga_locations.json).
                   If omitted, proximity features are disabled; Korean prompts still work.
        brand: Brand domain string (default: "elbee.yogaman.club").
    """

    def __init__(
        self,
        locations: Optional[List[Dict[str, Any]]] = None,
        brand: str = "elbee.yogaman.club",
    ) -> None:
        self.locations = locations or []
        self.brand = brand

    # ── LLM message builder ───────────────────────────────────────────────

    def build_messages(
        self,
        query: str,
        context: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, str]]:
        """
        Build an Ollama-compatible messages list using the Korean system prompt.

        Returns:
            [{"role": "system", "content": …}, …user/assistant turns…,
             {"role": "user", "content": query}]
        """
        system_content = ELBEE_SYSTEM_KO.format(
            brand=self.brand,
            context=context,
            # '라이프스타일' ends with 일 (batchim ㄹ code=8) → 와
            eun_neun="와",
        )
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_content}
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": query})
        return messages

    # ── Proximity helpers ─────────────────────────────────────────────────

    def find_nearby(
        self,
        user_lat: float,
        user_lng: float,
        radius_km: float = 1.0,
        location_type: Optional[str] = None,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Return [(location_dict, distance_km), …] sorted by distance."""
        results: List[Tuple[Dict[str, Any], float]] = []
        for loc in self.locations:
            if location_type and loc.get("type") != location_type:
                continue
            dist = _haversine_km(user_lat, user_lng, loc["lat"], loc["lng"])
            if dist <= radius_km:
                results.append((loc, round(dist, 3)))
        return sorted(results, key=lambda x: x[1])

    # ── Korean message generators ─────────────────────────────────────────

    def generate_proximity_message(
        self,
        user_lat: float,
        user_lng: float,
        district_name: str = "",
        weather: str = "clear",
    ) -> str:
        """
        Return a Korean location-aware marketing message.

        Priority:
          1. Rainy weather → indoor recommendation
          2. Sunny + outdoor spot within radius → outdoor suggestion
          3. Official elbee club within 1 km → Club Invite
          4. Public spot within 1 km → gentle nudge
          5. No result → fallback
        """
        district = district_name or "현재 위치"
        weather_lower = weather.lower()

        # ── Rainy: always prefer indoor ───────────────────────────────────
        if weather_lower in ("rain", "rainy", "비", "흐림"):
            nearby_indoor = self.find_nearby(user_lat, user_lng, radius_km=2.0)
            nearby_indoor = [(l, d) for l, d in nearby_indoor if l.get("weather_indoor")]
            if nearby_indoor:
                return get_template("rainy_day", location=district)

        # ── Sunny: prefer outdoor spots ───────────────────────────────────
        if weather_lower in ("sunny", "clear", "맑음"):
            outdoor = self.find_nearby(user_lat, user_lng, radius_km=2.0)
            outdoor = [(l, d) for l, d in outdoor if not l.get("weather_indoor", True)]
            if outdoor:
                return get_template("outdoor_sunny", location=district)

        # ── Any location within 1 km ──────────────────────────────────────
        nearby = self.find_nearby(user_lat, user_lng, radius_km=1.0)
        if not nearby:
            return get_template("no_result", location=district)

        closest, _ = nearby[0]
        loc_type = closest.get("type", "")

        if loc_type == "official_elbee_club":
            return get_template(
                "club_invite",
                location=district,
                studio_name=closest.get("name", "파트너 스튜디오"),
            )

        return get_template("proximity_public", location=district)

    def generate_time_message(self, location: str = "서울") -> str:
        """Return a time-appropriate Korean motivational message."""
        trigger = get_time_trigger()
        return get_template(trigger, location=location)
