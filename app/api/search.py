"""
Search router — /search

Endpoints:
  POST /search          — keyword search with location / topic filters
  GET  /search/suggest  — autocomplete suggestions
  GET  /search/health   — liveness probe
  GET  /search/filters  — available filter values (platforms, regions, topics)
"""
from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, Query

from app.config import get_settings
from app.models.search import SearchHealthResponse, SearchRequest, SearchResponse
from app.services.loader import GeoDataStore, get_store
from app.services.search_service import SearchService

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
