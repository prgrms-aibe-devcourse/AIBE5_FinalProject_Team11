"""
Search router — /search

Endpoints:
  POST /search           — keyword search with location / topic filters
  GET  /search/suggest   — autocomplete suggestions
  GET  /search/health    — liveness probe
  GET  /search/filters   — available filter values (platforms, regions, topics)
  POST /search/locations — find yoga spots by proximity, amenity, or type
"""
from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, Query

from app.config import get_settings
from app.models.search import (
    LocationSearchRequest, LocationSearchResponse,
    SearchHealthResponse, SearchRequest, SearchResponse,
    YogaLocationResult,
)
from app.services.agent import ElbeeAgent
from app.services.loader import GeoDataStore, get_store
from app.services.location_service import YogaLocationStore, get_location_store
from app.services.maps_service import MapsService
from app.services.search_service import SearchService
from app.services.templates import get_template

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/search", tags=["search"])


# ── Dependency ─────────────────────────────────────────────────────────────────

def get_search(store: GeoDataStore = Depends(get_store)) -> SearchService:
    return SearchService(store)


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=SearchResponse,
    summary="Keyword search with optional GEO-platform / region filtering",
)
async def search(
    body: SearchRequest,
    svc: SearchService = Depends(get_search),
) -> SearchResponse:
    """
    Search the GEO reference book.

    **Location-based filtering** narrows results to pages that mention
    a specific AI search engine (`geo_platform`) or market region (`geo_region`).

    Example location values:
    - `geo_platform`: `google`, `bing`, `perplexity`, `chatgpt`, `gemini`, `sge`
    - `geo_region`:   `us`, `eu`, `apac`, `latam`, `global`
    """
    return svc.search(body)


@router.get(
    "/suggest",
    summary="Autocomplete keyword suggestions",
)
async def suggest(
    q: str = Query(..., min_length=2, description="Prefix to expand"),
    limit: int = Query(8, ge=1, le=20),
    svc: SearchService = Depends(get_search),
) -> dict:
    suggestions: List[str] = svc.suggest(q, limit=limit)
    return {"q": q, "suggestions": suggestions}


@router.get(
    "/health",
    response_model=SearchHealthResponse,
    summary="Health check for the search service",
)
async def health(store: GeoDataStore = Depends(get_store)) -> SearchHealthResponse:
    return SearchHealthResponse(
        status="ok" if store.is_ready else "degraded",
        index_size=store.size,
    )


@router.get(
    "/filters",
    summary="Available filter values (platforms, regions, topics)",
)
async def filters(store: GeoDataStore = Depends(get_store)) -> dict:
    """
    Returns the distinct filter values detected in the loaded book.
    Use this to populate dropdowns / facet UIs.
    """
    return {
        "geo_platforms": sorted(store.platform_index.keys()),
        "geo_regions":   sorted(store.region_index.keys()),
        "topics":        sorted(store.topic_index.keys()),
        "total_pages":   store.size,
        "brand":         settings.brand,
    }


# ── Location search ────────────────────────────────────────────────────────────

@router.post(
    "/locations",
    response_model=LocationSearchResponse,
    summary="Find yoga spots by proximity, amenity, or type (elbee brand)",
)
async def search_locations(
    body: LocationSearchRequest,
    loc_store: YogaLocationStore = Depends(get_location_store),
) -> LocationSearchResponse:
    """
    Returns elbee-brand yoga locations filtered by:
    - **coord** — lat/lng + radius_km for proximity search
    - **source** — `kakao` (default) | `google` | `seed` (local JSON only)
    - **location_type** — `official_elbee_club` | `public_yoga_spot` | `wellness_cafe`
    - **amenities** — must-have list, e.g. `["shower", "mat_rental"]`
    - **weather** — `clear`/`sunny` prefers outdoor; `rain`/`rainy` restricts to indoor
    - **tags** / **district** — optional keyword filters

    Each result includes a `map_redirect_url` that opens the location directly
    in Kakao Maps (mobile app or web) or Google Maps.

    All responses include a Korean contextual message (해요체) and `brand_logo`.
    """
    agent = ElbeeAgent(loc_store.locations)
    district = body.district or ""
    weather = body.weather or "clear"
    source = body.source  # "kakao" | "google" | "seed"

    # ── Live map API path (Kakao or Google) ───────────────────────────────
    if body.coord and source in ("kakao", "google"):
        maps_svc = MapsService(
            kakao_key=settings.kakao_rest_key,
            google_key=settings.google_places_key,
            cache_ttl=settings.maps_cache_ttl,
        )
        # Check API key availability; fall back to seed if unconfigured
        has_key = (source == "kakao" and settings.kakao_rest_key) or \
                  (source == "google" and settings.google_places_key)

        if has_key:
            raw = await maps_svc.search_nearby(
                body.coord.lat,
                body.coord.lng,
                body.coord.radius_km,
                keyword="요가 스튜디오",
                source=source,
            )
            results: List[YogaLocationResult] = []
            for loc in raw:
                invite = agent.generate_proximity_message(
                    body.coord.lat, body.coord.lng,
                    district_name=loc.get("district", "") or district,
                    weather=weather,
                )
                results.append(YogaLocationResult(**loc, invite_message=invite))
            contextual_msg = (
                agent.generate_proximity_message(body.coord.lat, body.coord.lng, district, weather)
                if results else get_template("no_result", location=district)
            )
            return LocationSearchResponse(
                results=results,
                total=len(results),
                message=contextual_msg,
                source=source,
            )
        else:
            logger.warning("/search/locations: no API key for source='%s' — falling back to seed", source)
            source = "seed"

    # ── Seed data path (local yoga_locations.json) ────────────────────────
    if body.coord:
        nearby = loc_store.find_nearby(
            body.coord.lat,
            body.coord.lng,
            body.coord.radius_km,
            location_type=body.location_type,
            amenities=body.amenities or None,
            weather=body.weather,
        )
        results = []
        for loc, dist in nearby:
            invite = agent.generate_proximity_message(
                body.coord.lat, body.coord.lng,
                district_name=loc.get("district", ""),
                weather=weather,
            )
            redirect = MapsService.seed_redirect_url(loc["name"], loc["lat"], loc["lng"])
            results.append(YogaLocationResult(
                **{k: v for k, v in loc.items()},
                distance_km=dist,
                invite_message=invite,
                map_redirect_url=redirect,
            ))
        contextual_msg = (
            agent.generate_proximity_message(body.coord.lat, body.coord.lng, district, weather)
            if results else get_template("no_result", location=district)
        )
    else:
        locs = loc_store.locations
        if body.location_type:
            locs = [l for l in locs if l.get("type") == body.location_type]
        if body.tags:
            tag_set = set(body.tags)
            locs = [l for l in locs if tag_set.intersection(l.get("tags", []))]
        if body.district:
            locs = [l for l in locs if body.district in l.get("district", "")]
        if body.amenities:
            required = set(body.amenities)
            locs = [l for l in locs if required.issubset(set(l.get("amenities", [])))]
        results = [
            YogaLocationResult(
                **l,
                map_redirect_url=MapsService.seed_redirect_url(l["name"], l["lat"], l["lng"]),
            )
            for l in locs
        ]
        contextual_msg = agent.generate_time_message(district or "서울")

    return LocationSearchResponse(
        results=results,
        total=len(results),
        message=contextual_msg,
        source="seed",
    )
