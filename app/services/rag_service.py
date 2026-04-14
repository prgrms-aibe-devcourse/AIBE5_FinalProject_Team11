"""
RAG service — retrieves the most relevant GEO-book pages for a query
and assembles a context string suitable for prompting the LLM.

Retrieval strategy (no vector DB required):
  1. Score every page by keyword overlap (TF-proxy: unique hit count).
  2. Optionally re-rank by exact phrase bonus.
  3. Return top-K pages as context chunks.
"""
from __future__ import annotations

import re
import textwrap
from typing import Any, Dict, List, Optional, Tuple

from app.config import get_settings
from app.models.chat import ContextSource
from app.services.loader import GeoDataStore

settings = get_settings()


# ── Prompt templates ─────────────────────────────────────────────────────────

# Korean 해요체 system prompt — Elbee Yoga Guide persona
SYSTEM_PROMPT = """\
당신은 **엘비 요가 가이드(Elbee Yoga Guide)**예요 — {brand}의 공식 AI 도우미랍니다. 🧘

GEO(Generative Engine Optimization) 전문가로서, AI 검색 엔진(Google SGE, Perplexity, ChatGPT, Bing 등)에서
콘텐츠 가시성을 높이는 방법을 요가 라이프스타일과 연결해 안내해 드려요.

답변 규칙:
• 반드시 자연스러운 한국어(해요체)로 답변해요 (~해요, ~예요, ~드릴게요).
• 제공된 Context만을 바탕으로 답변하고, 확인되지 않은 내용은 솔직하게 말씀드려요.
• 간결하고 실행 가능한 조언을 드리며, 관련 페이지를 인용해요 (예: [페이지 12]).
• 이모지를 적절히 사용해 친근한 분위기를 만들어요.

GEO 레퍼런스 Context:
---
{context}
---"""

HISTORY_ITEM_TEMPLATE = "{role}: {content}"


# ── Core class ────────────────────────────────────────────────────────────────

class RagService:
    """
    Wraps the GeoDataStore to provide retrieve() and build_prompt() helpers.
    Instantiated once and injected via FastAPI dependency.
    """

    def __init__(self, store: GeoDataStore) -> None:
        self.store = store

    # ── Retrieval ─────────────────────────────────────────────────────────

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: int = 1,
    ) -> List[Tuple[Dict[str, Any], int]]:
        """
        Returns [(page_dict, score), …] sorted by score descending.
        `score` = number of unique query tokens that appear in the page.
        """
        k = top_k or settings.rag_top_k
        scores = self.store.keyword_scores(query)

        # Phrase bonus: +3 if the query appears verbatim
        phrase = query.lower()
        for idx, page in enumerate(self.store.pages):
            if phrase in page["text"].lower():
                scores[idx] = scores.get(idx, 0) + 3

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        result = []
        for idx, score in ranked[:k]:
            if score >= min_score:
                result.append((self.store.pages[idx], score))
        return result

    # ── Context assembly ──────────────────────────────────────────────────

    def build_context(
        self,
        hits: List[Tuple[Dict[str, Any], int]],
        max_chars: Optional[int] = None,
    ) -> Tuple[str, List[ContextSource]]:
        """
        Assembles a single context string from the top-k pages.
        Returns (context_text, list_of_ContextSource).
        Truncates to max_chars to stay within LLM context windows.
        """
        limit = max_chars or settings.rag_max_context_chars
        parts: List[str] = []
        sources: List[ContextSource] = []
        used = 0

        for page, score in hits:
            header = f"[Page {page['page']}]"
            body = page["text"].strip()
            chunk = f"{header}\n{body}"

            if used + len(chunk) > limit:
                # Partial inclusion
                remaining = limit - used
                if remaining > 200:
                    chunk = chunk[:remaining] + " …"
                    parts.append(chunk)
                break

            parts.append(chunk)
            used += len(chunk)

            # Build ContextSource (excerpt = first 300 chars)
            excerpt = textwrap.shorten(body, width=300, placeholder=" …")
            sources.append(ContextSource(
                page=page["page"],
                book=page["book"],
                excerpt=excerpt,
                score=score,
            ))

        return "\n\n".join(parts), sources

    # ── Prompt builder ────────────────────────────────────────────────────

    def build_prompt(
        self,
        query: str,
        context: str,
        history: Optional[List[Dict[str, str]]] = None,
        brand: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Returns the messages list suitable for Ollama /api/chat.
        Format: [{"role": "system", ...}, {"role": "user"/"assistant", ...}, …]
        """
        b = brand or settings.brand
        system_content = SYSTEM_PROMPT.format(brand=b, context=context)

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_content}
        ]

        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": query})
        return messages
