"""
Singleton data loader.

Reads `ocr_database.json` once at startup and builds:
  - pages[]            — full list of page dicts (id, text, tags …)
  - keyword_index      — word → sorted list of page indexes (into pages[])
  - platform_index     — geo_platform → list of page indexes
  - region_index       — geo_region   → list of page indexes
  - topic_index        — topic tag    → list of page indexes

GEO-platform detection is done by scanning page text for known engine keywords.
GEO-region detection looks for explicit region markers in text/tags.
"""
from __future__ import annotations

import json
import re
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# ── Platform / region keyword maps ──────────────────────────────────────────

PLATFORM_KEYWORDS: Dict[str, List[str]] = {
    "google":      ["google", "search generative experience", "sge", "ai overviews"],
    "bing":        ["bing", "microsoft copilot", "bing chat"],
    "perplexity":  ["perplexity"],
    "chatgpt":     ["chatgpt", "openai", "gpt-4", "gpt4"],
    "gemini":      ["gemini", "bard"],
    "claude":      ["claude", "anthropic"],
    "llm":         ["large language model", "llm", "generative ai", "ai-generated"],
}

REGION_KEYWORDS: Dict[str, List[str]] = {
    "us":     ["united states", " us ", "u.s.", "american", "north america"],
    "eu":     ["europe", "european", " eu ", "gdpr"],
    "apac":   ["asia", "pacific", "apac", "china", "japan", "korea", "india"],
    "latam":  ["latin america", "latam", "brazil", "mexico", "spanish"],
    "global": ["global", "worldwide", "international"],
}


def _detect_platforms(text: str) -> List[str]:
    lower = text.lower()
    return [p for p, kws in PLATFORM_KEYWORDS.items() if any(k in lower for k in kws)]


def _detect_regions(text: str) -> List[str]:
    lower = text.lower()
    return [r for r, kws in REGION_KEYWORDS.items() if any(k in lower for k in kws)]


def _tokenize(text: str) -> List[str]:
    """Lower-case alpha tokens ≥ 3 chars."""
    return re.findall(r"[a-z]{3,}", text.lower())


# ── Main loader ──────────────────────────────────────────────────────────────

class GeoDataStore:
    """
    Loaded once at application startup; injected via FastAPI dependency.
    """

    def __init__(self) -> None:
        self.pages: List[Dict[str, Any]] = []
        self.keyword_index: Dict[str, List[int]] = defaultdict(list)   # word → [page_idx]
        self.platform_index: Dict[str, List[int]] = defaultdict(list)
        self.region_index: Dict[str, List[int]] = defaultdict(list)
        self.topic_index: Dict[str, List[int]] = defaultdict(list)
        self._ready = False

    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def size(self) -> int:
        return len(self.pages)

    # ── Loading ──────────────────────────────────────────────────────────

    def load(self, db_path: Path) -> None:
        if not db_path.exists():
            logger.warning("ocr_database.json not found at %s — search/RAG will be empty", db_path)
            self._ready = False
            return

        raw: Dict[str, Any] = json.loads(db_path.read_text(encoding="utf-8"))
        meta = raw.get("metadata", {})
        book_slug: str = (
            meta.get("book_slug")
            or meta.get("book_title", "unknown")
            .lower().replace(" ", "-")
        )
        # pages can be a list [{page_number, text, ...}, ...] or a dict {key: {...}}
        raw_pages = raw.get("pages", [])
        book_entries = (
            raw_pages.items() if isinstance(raw_pages, dict)
            else enumerate(raw_pages)
        )

        logger.info("Loading %d pages from %s …", len(raw_pages), db_path.name)

        for key, entry in book_entries:
            idx = len(self.pages)
            text: str = entry.get("text", "")
            tags: List[str] = entry.get("tags", [])
            raw_pnum = entry.get("page_number", key if isinstance(key, int) else 0)
            try:
                page_num = int(raw_pnum)
            except (ValueError, TypeError):
                page_num = idx + 1

            platforms = _detect_platforms(text)
            regions = _detect_regions(text)

            page = {
                "idx":          idx,
                "page":         page_num,
                "book":         book_slug,
                "text":         text,
                "tags":         tags,
                "geo_platforms": platforms,
                "geo_regions":  regions,
            }
            self.pages.append(page)

            # ── keyword index ────────────────────────────────────────────
            seen: Set[str] = set()
            for token in _tokenize(text):
                if token not in seen:
                    self.keyword_index[token].append(idx)
                    seen.add(token)

            # ── platform / region indexes ────────────────────────────────
            for p in platforms:
                self.platform_index[p].append(idx)
            for r in regions:
                self.region_index[r].append(idx)

            # ── topic index (from tags) ───────────────────────────────────
            for tag in tags:
                self.topic_index[tag.lower()].append(idx)

        self._ready = True
        logger.info(
            "GeoDataStore ready — %d pages | %d keyword tokens | platforms: %s",
            len(self.pages),
            len(self.keyword_index),
            list(self.platform_index.keys()),
        )

    # ── Query helpers ────────────────────────────────────────────────────

    def keyword_scores(self, query: str) -> Dict[int, int]:
        """Return {page_idx: hit_count} for the query tokens."""
        scores: Dict[int, int] = defaultdict(int)
        for token in _tokenize(query):
            for idx in self.keyword_index.get(token, []):
                scores[idx] += 1
        return scores

    def filter_by_platform(self, platform: str) -> Optional[Set[int]]:
        key = platform.lower().strip()
        # fuzzy: check if any registered key *contains* the requested token
        matching: Set[int] = set()
        for k, idxs in self.platform_index.items():
            if key in k or k in key:
                matching.update(idxs)
        return matching if matching else None

    def filter_by_region(self, region: str) -> Optional[Set[int]]:
        key = region.lower().strip()
        matching: Set[int] = set()
        for k, idxs in self.region_index.items():
            if key in k or k in key:
                matching.update(idxs)
        return matching if matching else None

    def filter_by_topic(self, topic: str) -> Optional[Set[int]]:
        key = topic.lower().strip()
        matching: Set[int] = set()
        for k, idxs in self.topic_index.items():
            if key in k or k in key:
                matching.update(idxs)
        return matching if matching else None


# ── Module-level singleton ───────────────────────────────────────────────────

_store: Optional[GeoDataStore] = None


def get_store() -> GeoDataStore:
    """FastAPI dependency — returns the already-loaded singleton."""
    if _store is None:
        raise RuntimeError("GeoDataStore has not been initialized yet. "
                           "Call init_store() during application startup.")
    return _store


def init_store(db_path: Path) -> GeoDataStore:
    """Called once from app lifespan; returns the populated store."""
    global _store
    _store = GeoDataStore()
    _store.load(db_path)
    return _store
