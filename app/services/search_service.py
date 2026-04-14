"""
Search service — keyword search with optional GEO-marketing location filters.

Filters applied in order:
  1. Platform filter  (geo_platform in location)
  2. Region filter    (geo_region in location)
  3. Topic filter
  4. Tag filters
  5. Keyword scoring  — remaining pages ranked by query overlap
"""
from __future__ import annotations

import textwrap
from typing import Any, Dict, List, Optional, Set, Tuple

from app.config import get_settings
from app.models.search import (
    LocationFilter, SearchHit, SearchMeta, SearchRequest, SearchResponse,
)
from app.services.loader import GeoDataStore

settings = get_settings()


class SearchService:

    def __init__(self, store: GeoDataStore) -> None:
        self.store = store

    # ── Main search entry point ───────────────────────────────────────────

    def search(self, req: SearchRequest) -> SearchResponse:
        """
        Execute a keyword search with optional location/topic/tag filters.
        Returns a paginated SearchResponse.
        """
        # 1. Build candidate set (all pages = None means unrestricted)
        candidates: Optional[Set[int]] = None

        if req.location:
            candidates = self._apply_location_filter(candidates, req.location)

        if req.topic:
            topic_set = self.store.filter_by_topic(req.topic)
            if topic_set is not None:
                candidates = candidates & topic_set if candidates is not None else topic_set

        for tag in req.tags:
            tag_set = self.store.filter_by_topic(tag)
            if tag_set:
                candidates = candidates & tag_set if candidates is not None else tag_set

        # 2. Score candidates by keyword overlap
        all_scores = self.store.keyword_scores(req.q)

        if candidates is not None:
            scored: List[Tuple[int, float]] = [
                (idx, float(all_scores.get(idx, 0))) for idx in candidates
            ]
        else:
            scored = [(idx, float(score)) for idx, score in all_scores.items()]

        # Sort descending; include zero-score matches only when filtered (user narrowed set)
        if candidates is not None:
            scored.sort(key=lambda x: x[1], reverse=True)
        else:
            scored = [(i, s) for i, s in scored if s > 0]
            scored.sort(key=lambda x: x[1], reverse=True)

        # 3. Paginate
        total = len(scored)
        start = (req.page - 1) * req.per_page
        end = start + req.per_page
        page_slice = scored[start:end]

        # 4. Build hit objects
        hits: List[SearchHit] = []
        for idx, score in page_slice:
            page = self.store.pages[idx]
            excerpt = textwrap.shorten(page["text"].strip(), width=500, placeholder=" …")
            hits.append(SearchHit(
                page=page["page"],
                book=page["book"],
                excerpt=excerpt,
                score=score,
                tags=page.get("tags", []),
                geo_platforms=page.get("geo_platforms", []),
                geo_regions=page.get("geo_regions", []),
            ))

        meta = SearchMeta(
            query=req.q,
            total_hits=total,
            page=req.page,
            per_page=req.per_page,
            total_pages=max(1, -(-total // req.per_page)),   # ceiling division
            mode=req.mode,
            location_filter=req.location,
        )

        return SearchResponse(meta=meta, results=hits)

    # ── Filter helpers ────────────────────────────────────────────────────

    def _apply_location_filter(
        self,
        current: Optional[Set[int]],
        location: LocationFilter,
    ) -> Optional[Set[int]]:
        """
        Intersect the current candidate set with platform + region subsets.
        If a filter returns no results, it is ignored (graceful degradation).
        """
        if location.geo_platform:
            p_set = self.store.filter_by_platform(location.geo_platform)
            if p_set:
                current = current & p_set if current is not None else p_set

        if location.geo_region:
            r_set = self.store.filter_by_region(location.geo_region)
            if r_set:
                current = current & r_set if current is not None else r_set

        return current

    # ── Suggestions ───────────────────────────────────────────────────────

    def suggest(self, prefix: str, limit: int = 8) -> List[str]:
        """Return keyword suggestions starting with `prefix`."""
        p = prefix.lower().strip()
        if len(p) < 2:
            return []
        return sorted(
            k for k in self.store.keyword_index if k.startswith(p)
        )[:limit]
