"""
LlamaIndex semantic pose index (T-032).

Replaces the keyword BM25 rag_service.py with vector retrieval using
nomic-embed-text embeddings via Ollama.

Usage::

    from app.agents.pose_index import build_pose_index, get_query_engine

    # Build once (takes ~60 s for 944 poses, then persists to data/pose_index/)
    index = build_pose_index(poses)

    # Query
    qe = get_query_engine()
    response = qe.query("best poses for lower back pain")
    print(response)

Dependencies:
    pip install llama-index llama-index-embeddings-ollama
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

INDEX_PERSIST_DIR = Path(__file__).resolve().parents[2] / "data" / "pose_index"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")


def _get_embed_model():
    try:
        from llama_index.embeddings.ollama import OllamaEmbedding
    except ImportError as e:
        raise ImportError(
            "llama-index-embeddings-ollama is required: "
            "pip install llama-index llama-index-embeddings-ollama"
        ) from e
    return OllamaEmbedding(model_name=EMBED_MODEL, base_url=OLLAMA_BASE_URL)


def build_pose_index(poses: List[Dict[str, Any]]):
    """
    Build a VectorStoreIndex from a list of pose dicts.

    Args:
        poses: List of dicts with at least 'pose_id', 'canonical_name',
               and optionally 'natural_description', 'difficulty_rank'.

    Returns:
        A persisted VectorStoreIndex instance.
    """
    from llama_index.core import VectorStoreIndex, Document, StorageContext

    embed_model = _get_embed_model()
    docs = []
    for p in poses:
        text = p.get("natural_description") or p.get("canonical_name", "")
        if not text:
            continue
        docs.append(
            Document(
                text=text,
                metadata={
                    "pose_id": p.get("pose_id", ""),
                    "difficulty": p.get("difficulty_rank", 0),
                },
                doc_id=p.get("pose_id", ""),
            )
        )

    INDEX_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)
    index.storage_context.persist(persist_dir=str(INDEX_PERSIST_DIR))
    print(f"Index built: {len(docs)} documents → {INDEX_PERSIST_DIR}")
    return index


def load_pose_index():
    """Load a previously persisted index from disk."""
    from llama_index.core import StorageContext, load_index_from_storage

    if not INDEX_PERSIST_DIR.exists():
        raise FileNotFoundError(
            f"No index at {INDEX_PERSIST_DIR}. Run build_pose_index() first."
        )
    embed_model = _get_embed_model()
    storage_context = StorageContext.from_defaults(persist_dir=str(INDEX_PERSIST_DIR))
    return load_index_from_storage(storage_context, embed_model=embed_model)


def get_query_engine(similarity_top_k: int = 5):
    """Return a ready-to-use query engine (loads or builds index as needed)."""
    index = load_pose_index()
    return index.as_query_engine(similarity_top_k=similarity_top_k)
