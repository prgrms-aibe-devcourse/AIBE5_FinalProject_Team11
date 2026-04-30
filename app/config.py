"""
Application configuration — reads from environment variables or .env file.
All defaults are safe for local development.
"""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App identity ──────────────────────────────────────────────────────
    app_name: str = "aeogeo"
    brand: str = "elbee.yogaman.club"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── Server ────────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── CORS ──────────────────────────────────────────────────────────────
    # Comma-separated list in .env:  CORS_ORIGINS=https://a.com,https://b.com
    cors_origins: str = (
        "http://localhost:5173,"
        "http://localhost:4000,"
        "http://localhost:3000,"
        "https://aiegoo.github.io,"
        "https://elbee.yogaman.club,"
        "https://fyt200.yogaman.club"
    )

    @property
    def allowed_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
    @staticmethod
    def _is_wsl() -> bool:
        if sys.platform != "linux":
            return False
        proc = Path("/proc/version")
        return proc.exists() and "microsoft" in proc.read_text("utf-8").lower()

    @property
    def resolved_ollama_base_url(self) -> str:
        url = self.ollama_base_url.rstrip("/")
        if url == "http://localhost:11434" and self._is_wsl():
            return "http://host.docker.internal:11434"
        return url
    # ── Data paths ────────────────────────────────────────────────────────
    # Absolute path resolved at import time relative to this file
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data" / "json"
    default_book: str = "generative-engine-optimization"

    @property
    def ocr_db_path(self) -> Path:
        return self.data_dir / self.default_book / "ocr_database.json"

    @property
    def page_index_path(self) -> Path:
        return self.data_dir / self.default_book / "page_index.json"

    @property
    def keyword_index_path(self) -> Path:
        return self.data_dir / self.default_book / "keyword_index.json"

    # ── Ollama (LLM backend) ───────────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"          # change to llama3, gemma2, etc.
    ollama_timeout: int = 120              # seconds

    # ── OpenAI (fallback when Ollama is slow / unavailable) ───────────────
    openai_api_key: str = ""                       # OPENAI_API_KEY in .env
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    openai_timeout: int = 60
    # Switch "auto" = try Ollama first, fall back to OpenAI on error/timeout.
    # "ollama" = local only.  "openai" = OpenAI only.
    llm_provider: str = "auto"
    # Soft deadline (s) — if Ollama doesn't emit any token within this window
    # the request is cancelled and OpenAI is used instead (auto mode only).
    ollama_soft_deadline: int = 25

    # ── RAG tuning ────────────────────────────────────────────────────────
    rag_top_k: int = 5                     # pages returned as context
    rag_max_context_chars: int = 6000      # trim long context windows
    rag_min_keyword_score: int = 1         # pages with ≥ N keyword hits

    # ── Search defaults ───────────────────────────────────────────────────
    search_per_page: int = 10
    search_max_per_page: int = 50

    # ── Maps API ──────────────────────────────────────────────────────────
    kakao_rest_key: str = ""           # KAKAO_REST_KEY in .env
    google_places_key: str = ""        # GOOGLE_PLACES_KEY in .env
    maps_source: str = "kakao"         # MAPS_SOURCE = kakao | google | seed
    maps_cache_ttl: int = 300          # seconds to cache map API responses


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
