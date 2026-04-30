"""
LLM service — async HTTP client for Ollama.

Supports:
  - chat()        : single round-trip, returns full answer string
  - stream_chat() : async generator yielding token strings via Ollama streaming
"""
from __future__ import annotations

import asyncio
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
        self.base_url = (base_url or settings.resolved_ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ollama_timeout

        # OpenAI fallback config
        self.provider = (settings.llm_provider or "auto").lower()
        self.openai_api_key = settings.openai_api_key
        self.openai_base_url = settings.openai_base_url.rstrip("/")
        self.openai_model = settings.openai_model
        self.openai_timeout = settings.openai_timeout
        self.ollama_soft_deadline = settings.ollama_soft_deadline

    @property
    def openai_enabled(self) -> bool:
        return bool(self.openai_api_key) and self.provider in ("auto", "openai")

    @property
    def ollama_enabled(self) -> bool:
        return self.provider in ("auto", "ollama")

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

    # ── OpenAI fallback (chat + streaming) ───────────────────────────────

    async def openai_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        if not self.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.openai_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=self.openai_timeout) as client:
            r = await client.post(
                f"{self.openai_base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            r.raise_for_status()
            data = r.json()
        return data["choices"][0]["message"]["content"].strip()

    async def openai_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> AsyncGenerator[str, None]:
        if not self.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.openai_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=self.openai_timeout) as client:
            async with client.stream(
                "POST",
                f"{self.openai_base_url}/chat/completions",
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    body = line[6:].strip()
                    if body == "[DONE]":
                        break
                    try:
                        chunk = json.loads(body)
                    except json.JSONDecodeError:
                        continue
                    delta = (
                        chunk.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content", "")
                    )
                    if delta:
                        yield delta

    # ── Auto chat / stream (Ollama → OpenAI fallback) ────────────────────

    async def chat_auto(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        if self.provider == "openai":
            return await self.openai_chat(messages, temperature, max_tokens)
        if self.ollama_enabled:
            try:
                return await self.chat(messages, temperature, max_tokens)
            except Exception as exc:
                logger.warning("Ollama chat failed (%s) — falling back to OpenAI", exc)
                if not self.openai_enabled:
                    raise
        return await self.openai_chat(messages, temperature, max_tokens)

    async def stream_auto(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> AsyncGenerator[str, None]:
        """Yield tokens from Ollama; if no token within `ollama_soft_deadline`s
        or any error occurs, transparently switch to OpenAI streaming."""
        if self.provider == "openai":
            async for tok in self.openai_stream(messages, temperature, max_tokens):
                yield tok
            return

        if not self.ollama_enabled:
            async for tok in self.openai_stream(messages, temperature, max_tokens):
                yield tok
            return

        agen = self.stream_chat(messages, temperature, max_tokens)
        first_token: Optional[str] = None
        try:
            first_token = await asyncio.wait_for(
                agen.__anext__(), timeout=self.ollama_soft_deadline
            )
        except (asyncio.TimeoutError, StopAsyncIteration, Exception) as exc:
            logger.warning("Ollama stream stalled/failed (%r) — OpenAI fallback", exc)
            try:
                await agen.aclose()
            except Exception:
                pass
            if not self.openai_enabled:
                raise
            async for tok in self.openai_stream(messages, temperature, max_tokens):
                yield tok
            return

        if first_token:
            yield first_token
        try:
            async for tok in agen:
                yield tok
        except Exception as exc:
            logger.warning("Ollama stream broke mid-flight (%r)", exc)
            return
