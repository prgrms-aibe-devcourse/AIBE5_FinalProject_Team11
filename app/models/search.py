"""
Pydantic models for the /search endpoint.

Location-based filtering in the GEO-marketing context means filtering by:
  - geo_platform  : Google, Bing, Perplexity, ChatGPT, SGE, etc.
  - geo_region    : market region identifier (us, eu, apac, global …)
  - topic         : content topic / chapter tag from the GEO book
  - tags          : free-form content tags (list)
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
    page: int = Field(1, ge=1, description="Result page number (1-indexed)")
    per_page: int = Field(10, ge=1, le=50, description="Results per page")
    mode: Literal["keyword", "semantic", "hybrid"] = Field(
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


class SearchHealthResponse(BaseModel):
    status: Literal["ok", "degraded", "error"] = "ok"
    service: str = "search"
    index_size: int = 0
    brand: str = "elbee.yogaman.club"
