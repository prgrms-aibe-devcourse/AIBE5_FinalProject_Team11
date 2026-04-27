"""
aeogeo FastAPI application — entry point.

Architecture:
  /chat         → RAG over GEO book chunks + Ollama LLM
  /chat/stream  → SSE streaming variant
  /search       → Keyword search with GEO-platform / region filters
  /docs         → Swagger UI (auto-generated)
  /redoc        → ReDoc UI
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import chat_router, search_router, studio_router
from app.config import get_settings
from app.services.loader import init_store
from app.services.location_service import init_location_store

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Application lifespan ──────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Startup: load & index the OCR data store once.
    Shutdown: nothing to clean up (in-memory store).
    """
    logger.info("🚀 Starting %s v%s …", settings.app_name, settings.app_version)
    store = init_store(settings.ocr_db_path)
    if store.is_ready:
        logger.info("✅ Data store loaded: %d pages indexed", store.size)
    else:
        logger.warning(
            "⚠️  Data store is EMPTY — run the OCR pipeline first.\n"
            "    Expected path: %s", settings.ocr_db_path
        )

    loc_path = settings.base_dir / "data" / "yoga_locations.json"
    loc_store = init_location_store(loc_path)
    if loc_store.is_ready:
        logger.info("📍 Location store loaded: %d yoga spots indexed", loc_store.size)
    else:
        logger.warning("⚠️  yoga_locations.json not found — /search/locations will return empty results")

    yield
    logger.info("🛑 Shutting down %s", settings.app_name)


# ── App factory ────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="aeogeo API",
        description=(
            "**GEO Marketing Automation API** — powered by *Generative Engine Optimization* "
            "reference data.\n\n"
            f"Brand: **{settings.brand}** · "
            "Targets: `aiegoo.github.io/yoga/chat` · `aiegoo.github.io/yoga/search`"
        ),
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    )

    # ── Routers ───────────────────────────────────────────────────────────
    app.include_router(chat_router)
    app.include_router(search_router)
    app.include_router(studio_router)

    # ── Root ──────────────────────────────────────────────────────────────
    @app.get("/", tags=["meta"])
    async def root() -> dict:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "brand": settings.brand,
            "docs": "/docs",
            "endpoints": {
                "chat": "POST /chat",
                "chat_stream": "POST /chat/stream",
                "studio_chat": "POST /studio/chat",
                "studio_chat_stream": "POST /studio/chat/stream",
                "search": "POST /search",
                "search_suggest": "GET /search/suggest?q=",
                "search_filters": "GET /search/filters",
            },
        }

    @app.get("/health", tags=["meta"])
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok", "brand": settings.brand})

    return app


app = create_app()
