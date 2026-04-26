# ROADMAP — geo × elbee.yogaman.club

> Mini-project for employer portfolio  
> Brand: **elbee.yogaman.club**  
> Targets: `aiegoo.github.io/yoga/chat` · `/yoga/search`  
> Repo: `aiegoo/aeogeo` (private)  
> Started: 2026-04-15

---

## Phase 0 — Scaffold ✅ (2026-04-15)

- [x] `geo/` linked to `aeogeo.git` private remote
- [x] Folder structure: `screenshots/`, `ocr/`, `content/`, `data/json/`, `scripts/`
- [x] `ocr_pipeline.py` — pytesseract + OpenCV preprocessing → JSON
- [x] `scripts/adapt_content.py` — OCR text → topic-tagged Jekyll Markdown
- [x] `scripts/integrate.py` — syncs to yoga-chatbot references/
- [x] `scripts/watch.py` — file-watcher for auto-processing on image drop
- [x] `.gitignore` — screenshots + raw OCR gitignored; processed content tracked
- [x] `requirements.txt`, `README.md`

---

## Phase 1 — First Book Intake (target: 2026-04-22)

- [ ] Drop first book screenshots into `screenshots/`
- [ ] Run `ocr_pipeline.py` and review raw output quality
- [ ] Tune `preprocess()` if page quality is low (contrast, deskew params)
- [ ] Run `adapt_content.py` and review topic tagging
- [ ] Run `integrate.py` and verify pages appear in `/yoga/search`
- [ ] Add book chip to `/yoga/search` filter bar
- [ ] Confirm book is selectable in `/yoga/chat` book library sidebar
- [ ] First commit + push to `aeogeo.git`

---

## Phase 2 — Brand Layer (target: 2026-04-30)

- [ ] Create `elbee.yogaman.club` DNS CNAME → `aiegoo.github.io`
- [ ] Add `_data/brand.yml` to yoga-chatbot with elbee identity
  ```yaml
  name: elbee
  domain: elbee.yogaman.club
  tagline: "Yoga Knowledge, Always at Hand"
  logo: /assets/images/elbee-logo.svg
  color_primary: "#6C63FF"
  ```
- [ ] Apply brand to `/chat` and `/search` layouts via `_includes/elbee-brand.html`
- [ ] Add CNAME file to yoga-chatbot repo for custom domain
- [ ] Test chat + search under `elbee.yogaman.club`

---

## Phase 3 — Multi-Book Expansion (target: 2026-05-15)

- [ ] Process 2nd and 3rd books with `ocr_pipeline.py`
- [ ] Build a `data/json/books_manifest.json` aggregating all book metadata
- [ ] Update `integrate.py` to auto-update the manifest
- [ ] Add per-book quality score (words/page ratio) to manifest
- [ ] Add `scripts/audit.py` to report OCR confidence per page

---

## Phase 4 — Quality & CI (target: 2026-05-30)

- [ ] Add GitHub Actions workflow `.github/workflows/ocr-ci.yml`
  - Lint Python scripts on push
  - Validate JSON schema of `ocr_database.json`
  - Report page count diff vs previous run
- [ ] Add `scripts/review.py` — interactive terminal viewer for OCR output
- [ ] Add manual correction support: `ocr/corrections/<slug>/page_NNNN.txt` overrides

---

## Phase 5 — Employer Demo Package (target: 2026-06-01)

- [ ] Write `DEMO.md` — 5-minute walkthrough for employer
- [ ] Record demo screencast: screenshot drop → chat answer
- [ ] Deploy live demo at `elbee.yogaman.club`
- [ ] Prepare architecture diagram (OCR → JSON → search → chat flow)
- [ ] Portfolio write-up: pipeline design decisions, accuracy measurements

---

---

## Phase 6 — Agentic Automation Pipeline (target: 2026-05-20)

> **Source:** [Issue #4 tech stack discussion](https://github.com/aiegoo/aeogeo/issues/4)  
> **Goal:** Replace the current stateless FastAPI/Ollama loop with a production-grade multi-agent orchestration layer using LangGraph + LlamaIndex + CrewAI.

### Architecture

```
User request (lat/lng + goals + health flags)
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│          LangGraph State Machine (app/agents/)          │
│                                                         │
│  State 1: parse_input                                   │
│     └─ validate goals, expand via GOAL_TAG_MAP          │
│                                                         │
│  State 2: parallel_fetch (3 branches)                   │
│     ├─ a) find_nearby_studios → GET /api/v1/studios/nearby │
│     ├─ b) kill_switch_check  → contraindication filter  │
│     └─ c) llama_index_retrieve → semantic pose chunks   │
│                                                         │
│  State 3: score_and_rank                                │
│     └─ POST /api/v1/match → ranked MatchResult[]        │
│                                                         │
│  State 4: crew_generate (CrewAI)                        │
│     ├─ Analyst agent  → reads location + time + weather │
│     ├─ Matcher agent  → selects top 3 poses + 1 studio  │
│     └─ Writer agent   → generates Korean GEO copy       │
│                                                         │
│  State 5: return_response                               │
│     └─ { poses, studio, copy_ko, copy_en, json_ld }     │
└─────────────────────────────────────────────────────────┘
```

### Framework roles

| Framework | Role in this project |
|-----------|---------------------|
| **LangGraph** | Orchestrates the full pipeline as a typed state machine; handles retries and cycles |
| **LlamaIndex** | Indexes pose `natural_description` + `schema_org_jsonld` for semantic retrieval; replaces keyword `rag_service.py` |
| **CrewAI** | Three-agent crew: Analyst (context) → Matcher (poses) → Writer (Korean copy) |
| **AutoGen** | (Optional) Code-executing agent for trust score recalc validation + schema tests |
| **Ollama** | Local LLM backend (`mistral:latest`) — shared by LangGraph + CrewAI |

### Phase 6 checklist

- [ ] T-031 — LangGraph state machine scaffold (`app/agents/graph.py`)
- [ ] T-032 — LlamaIndex pose index (`app/agents/pose_index.py`) — replaces `rag_service.py`
- [ ] T-033 — CrewAI crew: Analyst + Matcher + Writer agents (`app/agents/crew.py`)
- [ ] T-034 — Geofencing trigger: real-time Korean copy on proximity event
- [ ] T-035 — GitHub Actions CI: lint + build + agent smoke test on every push

---

## Key metrics to track

| Metric | Baseline | Target |
|---|---|---|
| Pages processed | 0 | 500+ |
| OCR accuracy (manual sample) | — | ≥ 90% |
| Search latency | — | < 200ms |
| Books integrated | 0 | 3+ |
| Chat answers sourced from geo | 0% | > 30% |
| Agent pipeline e2e latency | — | < 5s |
| Korean copy naturalness (human eval) | — | ≥ 4/5 |
