"""
Simple in-process TTL cache for map API responses.

Key is a tuple derived from (lat, lng, radius_km, keyword, source),
with lat/lng rounded to 3 decimal places (~111 m grid).
"""
from __future__ import annotations

import time
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# {cache_key: (expires_at, payload)}
_cache: Dict[tuple, Tuple[float, List[Any]]] = {}


def _round_key(lat: float, lng: float, radius_km: float, keyword: str, source: str) -> tuple:
    return (round(lat, 3), round(lng, 3), round(radius_km, 1), keyword.lower(), source)


def cache_get(lat: float, lng: float, radius_km: float, keyword: str, source: str) -> Optional[List[Any]]:
    key = _round_key(lat, lng, radius_km, keyword, source)
    entry = _cache.get(key)
    if entry is None:
        return None
    expires_at, payload = entry
    if time.monotonic() > expires_at:
        del _cache[key]
        logger.debug("Cache expired for key %s", key)
        return None
    logger.debug("Cache hit for key %s", key)
    return payload


def cache_set(lat: float, lng: float, radius_km: float, keyword: str, source: str,
              payload: List[Any], ttl: int = 300) -> None:
    key = _round_key(lat, lng, radius_km, keyword, source)
    _cache[key] = (time.monotonic() + ttl, payload)
    logger.debug("Cache set for key %s (ttl=%ds)", key, ttl)


def cache_clear() -> None:
    """Flush the entire cache (useful in tests)."""
    _cache.clear()
