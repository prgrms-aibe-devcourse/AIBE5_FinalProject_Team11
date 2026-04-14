"""
Pydantic models for the /search endpoint.

Two distinct search modes:
  1. Content search (mode: keyword/semantic/hybrid)
     Filters: LocationFilter (geo_platform, geo_region), topic, tags
     Returns: SearchHit (book page excerpts)

  2. Location search (mode: location  OR  POST /search/locations)
     Filters: GeoCoordinate (lat/lng/radius), location_type, amenities, weather
     Returns: YogaLocationResult (studio/park/cafe with amenities)
"""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class LocationFilter(BaseModel):
    """
    GEO-marketing location filter.

    `geo_platform` selects the search engine / AI platform context.
    `geo_region`   narrows results to a market region.
    Both are optional; omitting them returns results from all contexts.
    """
    geo_platform: Optional[str] = Field(
        None,
        description="Filter by platform context: google, bing, perplexity, chatgpt, sge, gemini …",
        examples=["google", "perplexity", "sge"],
    )
    geo_region: Optional[str] = Field(
        None,
        description="Market region: us, eu, apac, latam, global …",
        examples=["us", "global"],
    )


class GeoCoordinate(BaseModel):
    """
    Physical location for proximity-based yoga spot search.
    Distinct from LocationFilter (which targets search-engine platforms/regions).
    """
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    radius_km: float = Field(1.0, ge=0.1, le=50.0, description="Search radius in km")


class SearchRequest(BaseModel):
    q: str = Field(..., min_length=1, max_length=512, description="Search query")
    location: Optional[LocationFilter] = Field(
        None,
        description="Optional GEO-platform / region filter",
    )
    topic: Optional[str] = Field(
        None,
        description="Filter by chapter topic (e.g. 'seo', 'llm', 'citations')",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Additional content tags to filter by",
    )
    geo_coord: Optional[GeoCoordinate] = Field(
        None,
        description="Physical coordinates for proximity-based location search",
    )
    weather: Optional[str] = Field(
        None,
        description="Current weather context: sunny, clear, rain, rainy — used to route indoor/outdoor",
        examples=["sunny", "rain"],
    )
    page: int = Field(1, ge=1, description="Result page number (1-indexed)")
    per_page: int = Field(10, ge=1, le=50, description="Results per page")
    mode: Literal["keyword", "semantic", "hybrid", "location"] = Field(
        "keyword",
        description="Search mode — 'semantic' requires an embedding model",
    )

    model_config = {"json_schema_extra": {
        "examples": [{
            "q": "citation optimization for generative search",
            "location": {"geo_platform": "perplexity", "geo_region": "us"},
            "topic": "citations",
            "page": 1,
            "per_page": 10,
            "mode": "keyword",
        }]
    }}


class SearchHit(BaseModel):
    page: int
    book: str
    excerpt: str = Field(..., max_length=600)
    score: float = Field(description="Relevance score (keyword hit count or cosine sim)")
    tags: List[str] = Field(default_factory=list)
    geo_platforms: List[str] = Field(
        default_factory=list,
        description="Platform contexts detected in this chunk",
    )
    geo_regions: List[str] = Field(
        default_factory=list,
        description="Market regions detected in this chunk",
    )
    amenities: List[str] = Field(
        default_factory=list,
        description="Available amenities if this hit is linked to a physical location",
    )
    location_type: Optional[str] = Field(
        None,
        description="official_elbee_club | public_yoga_spot | wellness_cafe | park",
    )
    distance_km: Optional[float] = Field(
        None,
        description="Distance from user coordinates if geo_coord was provided",
    )


class SearchMeta(BaseModel):
    query: str
    total_hits: int
    page: int
    per_page: int
    total_pages: int
    mode: str
    location_filter: Optional[LocationFilter] = None


class SearchResponse(BaseModel):
    meta: SearchMeta
    results: List[SearchHit]
    brand: str = "elbee.yogaman.club"
    brand_logo: str = "https://elbee.yogaman.club/assets/logo.png"
    contextual_message: Optional[str] = Field(
        None,
        description="Time/location-triggered Korean marketing message",
    )


class SearchHealthResponse(BaseModel):
    status: Literal["ok", "degraded", "error"] = "ok"
    service: str = "search"
    index_size: int = 0
    brand: str = "elbee.yogaman.club"
    brand_logo: str = "https://elbee.yogaman.club/assets/logo.png"


# ── Yoga location models (for POST /search/locations) ─────────────────────────

class YogaLocationResult(BaseModel):
    """A single yoga studio, outdoor spot, or wellness cafe."""
    id: str
    name: str
    type: str = Field(description="official_elbee_club | public_yoga_spot | wellness_cafe | park")
    district: str
    address: str
    lat: float
    lng: float
    amenities: List[str] = Field(
        default_factory=list,
        description="shower | mat_rental | locker | parking | cafe | sauna | restroom …",
    )
    tags: List[str] = Field(default_factory=list)
    weather_indoor: bool = True
    rating: float = Field(0.0, ge=0.0, le=5.0)
    description: str = ""
    distance_km: Optional[float] = Field(None, description="Distance from user if coords provided")
    invite_message: Optional[str] = Field(None, description="Korean contextual marketing message")
    # Map links
    place_url: Optional[str] = Field(None, description="Kakao Maps place page URL")
    phone: Optional[str] = Field(None, description="Phone number from map API")
    map_redirect_url: Optional[str] = Field(
        None,
        description="Deeplink to open this location in Kakao Maps or Google Maps",
        examples=["https://map.kakao.com/link/map/성수elbee요가스튜디오,37.5443,127.0556"],
    )


class LocationSearchRequest(BaseModel):
    """Request body for POST /search/locations."""
    coord: Optional[GeoCoordinate] = Field(
        None, description="User coordinates for proximity search"
    )
    location_type: Optional[str] = Field(
        None,
        description="Filter by type: official_elbee_club | public_yoga_spot | wellness_cafe | park",
        examples=["official_elbee_club"],
    )
    amenities: List[str] = Field(
        default_factory=list,
        description="Required amenities (all must be present): shower, mat_rental, parking …",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Content tags to match: morning_flow, hot_yoga, meditation …",
    )
    weather: Optional[str] = Field(
        None,
        description="Weather context for indoor/outdoor routing: sunny | rain | clear",
    )
    district: Optional[str] = Field(
        None, description="District name for 조사-aware Korean messages (e.g. 성수동, 강남)"
    )
    source: Literal["kakao", "google", "seed"] = Field(
        "kakao",
        description="Map data source: kakao (default) | google | seed (local JSON only)",
    )

    model_config = {"json_schema_extra": {
        "examples": [{
            "coord": {"lat": 37.5443, "lng": 127.0556, "radius_km": 1.5},
            "amenities": ["shower", "mat_rental"],
            "weather": "sunny",
            "district": "성수동",
        }]
    }}


class LocationSearchResponse(BaseModel):
    results: List[YogaLocationResult]
    total: int
    message: Optional[str] = Field(None, description="Korean contextual marketing message")
    brand: str = "elbee.yogaman.club"
    brand_logo: str = "https://elbee.yogaman.club/assets/logo.png"
    source: str = Field("seed", description="Data source used: kakao | google | seed")
