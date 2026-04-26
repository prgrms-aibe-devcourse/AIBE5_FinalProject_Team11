"""
Geofencing trigger for proximity-based Korean GEO marketing copy (T-034).

Zone types:
    partner  — user is within PARTNER_RADIUS_KM of a partner studio
    club     — user is within CLUB_RADIUS_KM (broader invite zone)

Usage::

    from app.agents.geofence import check_geofence, GeoTrigger

    studios = [{"studio_id": 1, "name": "강남 요가 센터", "latitude": 37.4979, "longitude": 127.0276}]
    trigger = check_geofence(37.4982, 127.0280, studios)
    if trigger:
        print(f"{trigger.zone_type}: {trigger.studio['name']} — {trigger.distance_m}m")

The trigger is passed to the CrewAI crew (crew.py) as GEO context so the
Writer agent can adjust copy tone (urgent proximity vs. soft club invite).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PARTNER_RADIUS_KM: float = 0.5   # 500 m — "지금 가까이 있어요!" copy
CLUB_RADIUS_KM: float = 1.0      # 1 km — "근처 지나가시면 들러봐요" copy


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class GeoTrigger:
    zone_type: str                  # "partner" | "club"
    studio: Dict[str, Any]
    distance_m: int


# ---------------------------------------------------------------------------
# Haversine helper (re-uses the same formula as agent.py)
# ---------------------------------------------------------------------------

def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlng / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_geofence(
    user_lat: float,
    user_lng: float,
    studios: List[Dict[str, Any]],
    partner_radius_km: float = PARTNER_RADIUS_KM,
    club_radius_km: float = CLUB_RADIUS_KM,
) -> Optional[GeoTrigger]:
    """Return the closest geofence trigger, or None if outside all zones.

    Args:
        user_lat, user_lng: Current user coordinates (WGS84 decimal degrees).
        studios: List of studio dicts with 'latitude' and 'longitude' keys.
        partner_radius_km: Radius for "partner" zone (default 0.5 km).
        club_radius_km: Radius for "club invite" zone (default 1.0 km).

    Returns:
        GeoTrigger with zone_type="partner" or "club", or None.
    """
    best: Optional[GeoTrigger] = None

    for studio in studios:
        lat = studio.get("latitude") or studio.get("lat")
        lng = studio.get("longitude") or studio.get("lng")
        if lat is None or lng is None:
            continue

        dist_km = _haversine_km(user_lat, user_lng, float(lat), float(lng))
        dist_m = int(dist_km * 1000)

        if dist_km <= partner_radius_km:
            if best is None or dist_m < best.distance_m:
                best = GeoTrigger(zone_type="partner", studio=studio, distance_m=dist_m)
        elif dist_km <= club_radius_km:
            if best is None or dist_m < best.distance_m:
                best = GeoTrigger(zone_type="club", studio=studio, distance_m=dist_m)

    return best


def geofence_copy_hint(trigger: GeoTrigger) -> str:
    """Return a short Korean copy prefix string based on trigger type.
    
    This is passed as additional context to the CrewAI Writer agent.
    """
    if trigger.zone_type == "partner":
        return (
            f"지금 {trigger.studio.get('name', '스튜디오')}에서 {trigger.distance_m}m 앞이에요! "
            "지금 바로 들어오세요 🏃"
        )
    else:
        return (
            f"근처에 {trigger.studio.get('name', '요가 스튜디오')}가 있어요 ({trigger.distance_m}m). "
            "잠깐 들러보실래요? 🧘"
        )
