"""
RAG Ingestion Pipeline (infra)
==============================

Automates the path from OCR'd instructor manual pages -> chunked
"Pose -> Mod -> Action" units -> embeddings -> Pinecone vector store.

This module is **infrastructure**, not a UI demo. It is the "fuel
refinery" that converts the founder's 20 years of instructor knowledge
into a queryable RAG knowledge base for the LangGraph orchestrator.

Pipeline stages (per Modoo spec + issue #4):
    1. Discover    : walk ocr/processed/<book>/page_*.txt
    2. Pre-tokenize: Kiwi morpheme analyzer for KO; passthrough for EN
                     (mixed-script paragraphs are normalized so chunks
                      respect Korean word boundaries)
    3. Chunk       : LlamaIndex SentenceSplitter -> "Action-Precaution"
                     pairs with rich metadata (book, page, lang, type)
    4. Embed       : embedding model (default: BAAI/bge-m3 multilingual,
                     swap to Gemini text-embedding-004 in prod)
    5. Upsert      : Pinecone (prod) or local JSON sidecar (dev/CI)

Run:
    # Dev (no Pinecone, no GPU): writes data/rag/index_<book>.jsonl
    python scripts/rag_ingest.py --book generative-engine-optimization --dry-run

    # Prod: requires PINECONE_API_KEY
    python scripts/rag_ingest.py --book generative-engine-optimization \\
        --index aeogeo-rag --backend pinecone

Design notes
------------
- Imports for heavy deps (llama_index, pinecone, kiwipiepy,
  sentence_transformers) are deferred so `--dry-run` works in CI without
  installing them.
- All chunk metadata follows the schema.org JSON-LD shape used in
  data/poses/poses_eat_schema.json so downstream AEO surfaces can cite
  the same `pose_id` / page anchor.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

REPO_ROOT = Path(__file__).resolve().parent.parent
OCR_ROOT = REPO_ROOT / "ocr" / "processed"
RAG_OUT = REPO_ROOT / "data" / "rag"

log = logging.getLogger("rag_ingest")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    chunk_id: str
    book: str
    page: int
    lang: str                # "ko" | "en" | "mixed"
    chunk_type: str          # "pose" | "modification" | "precaution" | "general"
    text: str
    metadata: dict = field(default_factory=dict)

    def to_record(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Stage 1 — discover
# ---------------------------------------------------------------------------

def iter_pages(book: str) -> Iterator[tuple[int, Path]]:
    book_dir = OCR_ROOT / book
    if not book_dir.is_dir():
        raise FileNotFoundError(f"No OCR directory: {book_dir}")
    pages = sorted(book_dir.glob("page_*.txt"))
    for p in pages:
        m = re.search(r"page_(\d+)\.txt$", p.name)
        if not m:
            continue
        yield int(m.group(1)), p


# ---------------------------------------------------------------------------
# Stage 2 — language detect + Kiwi pre-tokenization (KO)
# ---------------------------------------------------------------------------

_HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def detect_lang(text: str) -> str:
    has_ko = bool(_HANGUL_RE.search(text))
    has_en = bool(_LATIN_RE.search(text))
    if has_ko and has_en:
        return "mixed"
    if has_ko:
        return "ko"
    return "en"


_kiwi = None


def _get_kiwi():
    """Lazy-load Kiwi to keep --dry-run dependency-free."""
    global _kiwi
    if _kiwi is None:
        try:
            from kiwipiepy import Kiwi  # type: ignore

            _kiwi = Kiwi()
        except ImportError:
            log.warning("kiwipiepy not installed; falling back to whitespace split for KO")
            _kiwi = False
    return _kiwi


def normalize_ko(text: str) -> str:
    """
    Re-join Korean morphemes with explicit spaces so the downstream
    sentence splitter never breaks inside a word like '학교에서는'.
    EN tokens are passed through unchanged.
    """
    kiwi = _get_kiwi()
    if not kiwi:
        return text
    out: list[str] = []
    for sent in kiwi.split_into_sents(text):
        toks = [t.form for t in kiwi.tokenize(sent.text)]
        out.append(" ".join(toks))
    return "\n".join(out)


def normalize(text: str, lang: str) -> str:
    text = re.sub(r"[ \t]+", " ", text).strip()
    if lang in ("ko", "mixed"):
        return normalize_ko(text)
    return text


# ---------------------------------------------------------------------------
# Stage 3 — chunking ("Action / Modification / Precaution")
# ---------------------------------------------------------------------------

# Heuristic markers for instructor-manual structure.  In a richer manual
# these would be section headings; here we tag at the sentence level so
# a single page produces multiple typed chunks.
_POSE_HINTS = (
    "asana", "pose", "자세", "downward", "warrior", "sun salutation",
)
_MOD_HINTS = (
    "modification", "modify", "alternative", "easier", "변형", "쉬운",
)
_PRECAUTION_HINTS = (
    "avoid", "caution", "do not", "contraindication", "injury",
    "주의", "금지", "부상",
)


def classify(sentence: str) -> str:
    s = sentence.lower()
    if any(h in s for h in _PRECAUTION_HINTS):
        return "precaution"
    if any(h in s for h in _MOD_HINTS):
        return "modification"
    if any(h in s for h in _POSE_HINTS):
        return "pose"
    return "general"


def split_sentences(text: str) -> list[str]:
    """
    Try LlamaIndex SentenceSplitter for richer behaviour; fall back to a
    regex splitter so --dry-run works without the dep.
    """
    try:
        from llama_index.core.node_parser import SentenceSplitter  # type: ignore

        splitter = SentenceSplitter(chunk_size=400, chunk_overlap=40)
        return [c for c in splitter.split_text(text) if c.strip()]
    except ImportError:
        # Fallback: split on sentence terminators (EN + KO)
        parts = re.split(r"(?<=[.!?。！？])\s+|\n{2,}", text)
        return [p.strip() for p in parts if p.strip()]


def chunk_page(book: str, page: int, raw: str) -> list[Chunk]:
    lang = detect_lang(raw)
    text = normalize(raw, lang)
    if not text:
        return []
    sentences = split_sentences(text)
    chunks: list[Chunk] = []
    for i, sent in enumerate(sentences):
        if len(sent) < 20:  # skip OCR noise
            continue
        ctype = classify(sent)
        cid = f"{book}__p{page:04d}__c{i:03d}"
        chunks.append(Chunk(
            chunk_id=cid,
            book=book,
            page=page,
            lang=lang,
            chunk_type=ctype,
            text=sent,
            metadata={
                "source_path": f"ocr/processed/{book}/page_{page:04d}.txt",
                "schema_org_type": "HowTo" if ctype == "pose" else "MedicalGuideline",
            },
        ))
    return chunks


# ---------------------------------------------------------------------------
# Stage 4 — embeddings (lazy)
# ---------------------------------------------------------------------------

def embed(texts: list[str], model: str) -> list[list[float]]:
    from sentence_transformers import SentenceTransformer  # type: ignore

    enc = SentenceTransformer(model)
    return enc.encode(texts, normalize_embeddings=True, show_progress_bar=True).tolist()


# ---------------------------------------------------------------------------
# Stage 5 — upsert backends
# ---------------------------------------------------------------------------

def upsert_jsonl(chunks: Iterable[Chunk], book: str) -> Path:
    RAG_OUT.mkdir(parents=True, exist_ok=True)
    out = RAG_OUT / f"index_{book}.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for c in chunks:
            fh.write(json.dumps(c.to_record(), ensure_ascii=False) + "\n")
    return out


def upsert_pinecone(
    chunks: list[Chunk],
    *,
    index_name: str,
    embed_model: str,
    namespace: str,
) -> int:
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        raise RuntimeError("PINECONE_API_KEY not set")
    from pinecone import Pinecone, ServerlessSpec  # type: ignore

    pc = Pinecone(api_key=api_key)
    if index_name not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=index_name,
            dimension=1024,  # bge-m3
            metric="cosine",
            spec=ServerlessSpec(
                cloud=os.environ.get("PINECONE_CLOUD", "aws"),
                region=os.environ.get("PINECONE_REGION", "us-east-1"),
            ),
        )
    index = pc.Index(index_name)

    vectors = embed([c.text for c in chunks], embed_model)
    payload = [
        {
            "id": c.chunk_id,
            "values": v,
            "metadata": {
                "book": c.book, "page": c.page, "lang": c.lang,
                "chunk_type": c.chunk_type, "text": c.text[:1000],
                **c.metadata,
            },
        }
        for c, v in zip(chunks, vectors)
    ]
    # Pinecone batches of 100
    for i in range(0, len(payload), 100):
        index.upsert(vectors=payload[i:i + 100], namespace=namespace)
    return len(payload)


# ---------------------------------------------------------------------------
# Pipeline driver
# ---------------------------------------------------------------------------

def run(book: str, *, backend: str, index: str, embed_model: str,
        dry_run: bool, limit: int | None) -> dict:
    log.info("Discovering pages for book=%s", book)
    pairs = list(iter_pages(book))
    if limit:
        pairs = pairs[:limit]
    log.info("Pages found: %d", len(pairs))

    all_chunks: list[Chunk] = []
    by_type: dict[str, int] = {}
    by_lang: dict[str, int] = {}

    for page, path in pairs:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        for c in chunk_page(book, page, raw):
            all_chunks.append(c)
            by_type[c.chunk_type] = by_type.get(c.chunk_type, 0) + 1
            by_lang[c.lang] = by_lang.get(c.lang, 0) + 1

    summary = {
        "book": book,
        "pages": len(pairs),
        "chunks": len(all_chunks),
        "by_type": by_type,
        "by_lang": by_lang,
        "backend": backend if not dry_run else "jsonl(dry-run)",
    }

    if dry_run or backend == "jsonl":
        out = upsert_jsonl(all_chunks, book)
        summary["output"] = str(out.relative_to(REPO_ROOT))
    elif backend == "pinecone":
        n = upsert_pinecone(
            all_chunks, index_name=index,
            embed_model=embed_model, namespace=book,
        )
        summary["upserted"] = n
    else:
        raise SystemExit(f"unknown backend: {backend}")

    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="aeogeo RAG ingestion pipeline")
    p.add_argument("--book", required=True,
                   help="folder name under ocr/processed/")
    p.add_argument("--backend", choices=["jsonl", "pinecone"], default="jsonl")
    p.add_argument("--index", default="aeogeo-rag")
    p.add_argument("--embed-model", default="BAAI/bge-m3",
                   help="sentence-transformers model id")
    p.add_argument("--dry-run", action="store_true",
                   help="skip embeddings/Pinecone; write JSONL only")
    p.add_argument("--limit", type=int, default=None,
                   help="process only the first N pages (smoke test)")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s | %(message)s",
    )

    summary = run(
        args.book,
        backend=args.backend,
        index=args.index,
        embed_model=args.embed_model,
        dry_run=args.dry_run,
        limit=args.limit,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
