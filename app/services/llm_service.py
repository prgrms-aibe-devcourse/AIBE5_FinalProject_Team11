"""
LLM service — async HTTP client for Ollama.

Supports:
  - chat()        : single round-trip, returns full answer string
  - stream_chat() : async generator yielding token strings via Ollama streaming
"""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    """
    Thin async wrapper around Ollama's /api/chat endpoint.
    Stateless — instantiate once and reuse.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ollama_timeout

    # ── Connectivity ──────────────────────────────────────────────────────

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                return r.status_code == 200
        except Exception:
            return False

    # ── Non-streaming chat ─────────────────────────────────────────────────

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        """
        Sends messages to Ollama and returns the full response text.
        Raises httpx.HTTPError on network / HTTP failures.
        """
        payload = self._build_payload(messages, temperature, max_tokens, stream=False)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            resp.raise_for_status()
            data: Dict[str, Any] = resp.json()

        # Ollama non-stream response: {"message": {"role": "assistant", "content": "..."}}
        return data.get("message", {}).get("content", "").strip()

    # ── Streaming chat ─────────────────────────────────────────────────────

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> AsyncGenerator[str, None]:
        """
        Async generator that yields token strings as Ollama produces them.
        Each yielded value is a text fragment (may be empty for the final done chunk).
        """
        payload = self._build_payload(messages, temperature, max_tokens, stream=True)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk: Dict[str, Any] = json.loads(line)
                    except json.JSONDecodeError:
                        logger.debug("Non-JSON line from Ollama: %r", line)
                        continue

                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token

                    if chunk.get("done"):
                        break

    # ── Helpers ────────────────────────────────────────────────────────────

    def _build_payload(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool,
    ) -> Dict[str, Any]:
        return {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
