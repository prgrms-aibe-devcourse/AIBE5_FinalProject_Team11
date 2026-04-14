"""
MapsService — live yoga studio search via Kakao Local API or Google Places API.

Falls back gracefully to the seed YogaLocationStore when no API key is configured
or the external call fails.

Redirect links:
  Kakao result  → place_url from API  (e.g. https://place.map.kakao.com/12345678)
  Google result → https://www.google.com/maps/search/?api=1&query={name}&query_place_id={place_id}
  Seed result   → https://map.kakao.com/link/map/{name},{lat},{lng}    (universal deeplink)

Both Kakao Maps app and web handle the kakao deeplink; Google Maps handles the Google URL.
"""
from __future__ import annotations

import logging
import urllib.parse
from typing import Any, Dict, List, Optional

import httpx

from app.services.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

# ── Kakao Local API ────────────────────────────────────────────────────────────
_KAKAO_BASE = "https://dapi.kakao.com/v2/local/search/keyword.json"
# category_group_code PT8 = 체육시설 (sports/exercise facilities)
_KAKAO_CATEGORY = "PT8"

# ── Google Places Nearby Search ────────────────────────────────────────────────
_GOOGLE_BASE = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"


class MapsService:
    """
    Async map API client.  Instantiate once; re-use across requests (httpx.AsyncClient
    is created per-call to stay stateless — suitable for FastAPI dependency injection).

    Usage:
        svc = MapsService(kakao_key="...", google_key="...", cache_ttl=300)
        results = await svc.search_nearby(37.5443, 127.0556, 1.5, keyword="요가 스튜디오", source="kakao")
    """

    def __init__(
        self,
        kakao_key: str = "",
        google_key: str = "",
        cache_ttl: int = 300,
    ) -> None:
        self.kakao_key = kakao_key
        self.google_key = google_key
        self.cache_ttl = cache_ttl

    # ── Public entry point ─────────────────────────────────────────────────

    async def search_nearby(
        self,
        lat: float,
        lng: float,
        radius_km: float = 1.5,
        keyword: str = "요가 스튜디오",
        source: str = "kakao",
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of normalized YogaLocationResult-compatible dicts.
        Checks TTL cache first; falls back to empty list on network error.
        """
        cached = cache_get(lat, lng, radius_km, keyword, source)
        if cached is not None:
            return cached

        try:
            if source == "kakao":
                results = await self._kakao_nearby(lat, lng, radius_km, keyword)
            elif source == "google":
                results = await self._google_nearby(lat, lng, radius_km, keyword)
            else:
                return []
        except Exception as exc:
            logger.warning("MapsService [%s] error: %s — returning empty", source, exc)
            return []

        cache_set(lat, lng, radius_km, keyword, source, results, self.cache_ttl)
        return results

    # ── Kakao ──────────────────────────────────────────────────────────────

    async def _kakao_nearby(
        self, lat: float, lng: float, radius_km: float, keyword: str
    ) -> List[Dict[str, Any]]:
        radius_m = min(int(radius_km * 1000), 20_000)
        params = {
            "query": keyword,
            "x": str(lng),
            "y": str(lat),
            "radius": str(radius_m),
            "category_group_code": _KAKAO_CATEGORY,
            "size": "15",
        }
        headers = {"Authorization": f"KakaoAK {self.kakao_key}"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(_KAKAO_BASE, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        docs = data.get("documents", [])
        logger.info("Kakao Local: %d results for '%s' @ (%.4f, %.4f) r=%dm",
                    len(docs), keyword, lat, lng, radius_m)
        return [self._normalize_kakao(d) for d in docs]

    def _normalize_kakao(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        name = doc.get("place_name", "")
        loc_lat = float(doc.get("y", 0))
        loc_lng = float(doc.get("x", 0))
        place_url = doc.get("place_url", "")
        address_parts = doc.get("address_name", "").split()

        # Kakao deeplink: opens in Kakao Maps app on mobile, web on desktop
        kakao_deeplink = (
            f"https://map.kakao.com/link/map/"
            f"{urllib.parse.quote(name)},{loc_lat},{loc_lng}"
        )

        return {
            "id":             f"kakao-{doc.get('id', '')}",
            "name":           name,
            "type":           "live_result",
            "district":       address_parts[1] if len(address_parts) > 1 else "",
            "address":        doc.get("road_address_name") or doc.get("address_name", ""),
            "lat":            loc_lat,
            "lng":            loc_lng,
            "amenities":      [],
            "tags":           [t.strip() for t in doc.get("category_name", "").split(">") if t.strip()],
            "weather_indoor": True,
            "rating":         0.0,
            "description":    doc.get("category_name", ""),
            "distance_km":    round(float(doc.get("distance", 0)) / 1000, 2),
            "phone":          doc.get("phone", ""),
            "place_url":      place_url or kakao_deeplink,
            "map_redirect_url": place_url or kakao_deeplink,
        }

    # ── Google ─────────────────────────────────────────────────────────────

    async def _google_nearby(
        self, lat: float, lng: float, radius_km: float, keyword: str
    ) -> List[Dict[str, Any]]:
        radius_m = min(int(radius_km * 1000), 50_000)
        params = {
            "location": f"{lat},{lng}",
            "radius": str(radius_m),
            "keyword": keyword,
            "language": "ko",
            "key": self.google_key,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(_GOOGLE_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()

        places = data.get("results", [])
        logger.info("Google Places: %d results for '%s' @ (%.4f, %.4f) r=%dm",
                    len(places), keyword, lat, lng, radius_m)
        return [self._normalize_google(p) for p in places]

    def _normalize_google(self, place: Dict[str, Any]) -> Dict[str, Any]:
        name = place.get("name", "")
        geo = place.get("geometry", {}).get("location", {})
        loc_lat = geo.get("lat", 0.0)
        loc_lng = geo.get("lng", 0.0)
        place_id = place.get("place_id", "")

        google_url = (
            f"https://www.google.com/maps/search/?api=1"
            f"&query={urllib.parse.quote(name)}"
            f"&query_place_id={place_id}"
        )

        return {
            "id":             f"google-{place_id}",
            "name":           name,
            "type":           "live_result",
            "district":       "",
            "address":        place.get("vicinity", ""),
            "lat":            loc_lat,
            "lng":            loc_lng,
            "amenities":      [],
            "tags":           place.get("types", [])[:5],
            "weather_indoor": True,
            "rating":         float(place.get("rating", 0.0)),
            "description":    ", ".join(place.get("types", [])[:3]),
            "distance_km":    None,
            "phone":          "",
            "place_url":      google_url,
            "map_redirect_url": google_url,
        }

    # ── Seed data redirect helper ─────────────────────────────────────────

    @staticmethod
    def seed_redirect_url(name: str, lat: float, lng: float) -> str:
        """
        Generate a Kakao Maps deeplink for a seed-data location (no API key required).
        Opens in Kakao Maps app on mobile; falls back to Kakao Maps web.

        Example: https://map.kakao.com/link/map/성수elbee요가스튜디오,37.5443,127.0556
        """
        return (
            f"https://map.kakao.com/link/map/"
            f"{urllib.parse.quote(name)},{lat},{lng}"
        )
