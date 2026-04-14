"""
Yoga Location Service — loads yoga_locations.json and provides
proximity, amenity, type, and weather-aware filtering.

The module-level singleton starts as an empty store (no crash if JSON
is missing). `init_location_store()` is called during app lifespan startup.
"""
from __future__ import annotations

import json
import math
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.services.templates import get_template, get_time_trigger

logger = logging.getLogger(__name__)


# ── Haversine distance ────────────────────────────────────────────────────────

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two (lat, lon) points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── Store class ───────────────────────────────────────────────────────────────

class YogaLocationStore:
    """In-memory store of yoga/wellness locations loaded from yoga_locations.json."""

    def __init__(self) -> None:
        self.locations: List[Dict[str, Any]] = []
        self._ready = False

    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def size(self) -> int:
        return len(self.locations)

    # ── Loading ───────────────────────────────────────────────────────────

    def load(self, path: Path) -> None:
        if not path.exists():
            logger.warning("yoga_locations.json not found at %s — /search/locations will be empty", path)
            return
        data: Dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        self.locations = data.get("locations", [])
        self._ready = bool(self.locations)
        logger.info(
            "YogaLocationStore ready — %d locations loaded (%d official, %d outdoor)",
            len(self.locations),
            sum(1 for l in self.locations if l.get("type") == "official_elbee_club"),
            sum(1 for l in self.locations if not l.get("weather_indoor", True)),
        )

    # ── Query helpers ─────────────────────────────────────────────────────

    def find_nearby(
        self,
        lat: float,
        lng: float,
        radius_km: float = 1.0,
        location_type: Optional[str] = None,
        amenities: Optional[List[str]] = None,
        weather: Optional[str] = None,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Return [(location_dict, distance_km), …] within radius, sorted by distance.

        Filters applied:
          - location_type: exact match on loc["type"] if provided
          - amenities: all requested amenities must be present
          - weather: if "rain"/"rainy"/비, exclude outdoor spots
        """
        results: List[Tuple[Dict[str, Any], float]] = []
        for loc in self.locations:
            if location_type and loc.get("type") != location_type:
                continue
            if amenities:
                loc_ams = set(loc.get("amenities", []))
                if not all(a in loc_ams for a in amenities):
                    continue
            if weather and weather.lower() in ("rain", "rainy", "비", "흐림"):
                if not loc.get("weather_indoor", False):
                    continue
            dist = haversine_km(lat, lng, loc["lat"], loc["lng"])
            if dist <= radius_km:
                results.append((loc, round(dist, 3)))
        return sorted(results, key=lambda x: x[1])

    def search_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Return locations that share at least one tag with `tags`."""
        tag_set = set(t.lower() for t in tags)
        return [
            loc for loc in self.locations
            if tag_set & set(t.lower() for t in loc.get("tags", []))
        ]

    def filter_by_type(self, location_type: str) -> List[Dict[str, Any]]:
        return [l for l in self.locations if l.get("type") == location_type]

    def get_by_district(self, district: str) -> List[Dict[str, Any]]:
        return [l for l in self.locations if district in l.get("district", "")]

    def generate_message(
        self,
        lat: float,
        lng: float,
        district: str = "",
        weather: str = "clear",
    ) -> str:
        """
        Generate a contextual Korean marketing message based on proximity and weather.
        """
        nearby = self.find_nearby(lat, lng, radius_km=1.0, weather=weather)

        if not nearby:
            return get_template("no_result", location=district or "현재 위치")

        closest, _ = nearby[0]
        loc_type = closest.get("type", "")
        loc_name = closest.get("name", "근처 스튜디오")
        district_str = district or closest.get("district", "현재 위치")

        # Sunny weather + outdoor available → promote outdoor
        if weather.lower() in ("sunny", "clear", "맑음") and not closest.get("weather_indoor", True):
            return get_template("outdoor_sunny", location=district_str)

        # Rainy → indoor only (already filtered)
        if weather.lower() in ("rain", "rainy", "비"):
            return get_template("rainy_day", location=district_str)

        # Official partner club within 1 km → Club Invite
        if loc_type == "official_elbee_club":
            return get_template(
                "club_invite",
                location=district_str,
                studio_name=loc_name,
            )

        # Public / park spot
        return get_template("proximity_public", location=district_str)


# ── Module-level singleton (empty until init_location_store is called) ────────

_loc_store: YogaLocationStore = YogaLocationStore()


def get_location_store() -> YogaLocationStore:
    """FastAPI dependency — returns the module-level store (always safe to call)."""
    return _loc_store


def init_location_store(path: Path) -> YogaLocationStore:
    """Called once from app lifespan. Loads data into the singleton."""
    _loc_store.load(path)
    return _loc_store
