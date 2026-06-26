# aeogeo / YogaQ

> AI-powered yoga recommendation and knowledge platform for **app.yogaman.club**.
> Combines search, chat, studio tooling, matching, structured data, and OCR intake workflows.

---

## Overview

YogaQ is the current product layer of the `aiegoo/aeogeo` repository.

It now runs as a multi-service yoga platform with:

- **FastAPI backend** on `:8000` for chat, search, studio, auth, pipeline, geofence, and Schema.org JSON-LD routes
- **React + Vite frontend** on `:5173` for the main YogaQ interface
- **Spring Boot API** on `:19090` for weighted pose matching backed by PostgreSQL
- **Typesense** on `:8108` indexing **1,813 yoga documents** for semantic and keyword search
- **Ollama** on `:11434` serving `mistral` and `nomic-embed-text` for RAG chat
- **oauth2-proxy** on `:4180` providing GitHub OAuth SSO with approval workflow
- **Caddy** on `:8088` handling reverse proxying behind Cloudflare Tunnel
- **Streamlit match app** on `:8502` for the visual pose-matching demo

Key completed capabilities include GitHub SSO, Typesense-backed search, RAG chat, trust-scored pose matching, LangGraph + CrewAI studio flows, geofencing, crawlable AEO pages, XML sitemap generation, and green GitHub Actions CI.

---

## Architecture

| Layer | Service | Port | Role |
|---|---|---:|---|
| Edge | Cloudflare Tunnel + Caddy | `:8088` | Public entrypoint, TLS termination upstream, reverse proxy |
| Auth | oauth2-proxy | `:4180` | GitHub OAuth SSO, allowlist + access-request approval flow |
| App API | FastAPI | `:8000` | Chat, search, studio, auth, pipeline, geofence, Schema.org JSON-LD |
| Frontend | React + Vite | `:5173` | YogaQ web app: chat, search, pose browser, match, studio, anatomy |
| Matching API | Spring Boot + PostgreSQL | `:19090` | Java matching engine, Flyway migrations `V1-V9` |
| Search | Typesense | `:8108` | 1,813 indexed yoga documents |
| LLM / Embeddings | Ollama | `:11434` | `mistral` chat + `nomic-embed-text` embeddings |
| Demo | Streamlit | `:8502` | Visual pose-matching demo |
| Realtime / Analysis | WebSocket proxy + Jupyter | varies | Real-time connections and notebook-based exploration |

High-level request flow:

1. Cloudflare Tunnel forwards traffic for `app.yogaman.club` and `match.yogaman.club`
2. Caddy routes public schema/AEO routes and protected app routes
3. oauth2-proxy enforces GitHub SSO on protected endpoints
4. FastAPI serves chat, search, studio, auth, geofence, and JSON-LD responses
5. Spring Boot handles weighted yoga matching and PostgreSQL-backed domain data
6. Typesense + Ollama power search, retrieval, and answer generation

---

## Quick start

### 1) Environment

```bash
cp .env.example .env
```

Set local values for at least:

- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `CORS_ORIGINS`
- `KAKAO_REST_KEY` / `GOOGLE_PLACES_KEY` (optional)

### 2) Python API + OCR environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-api.txt
```

### 3) Frontend dependencies

```bash
cd frontend
npm ci
cd ..
```

### 4) Start containerized services

```bash
docker compose up -d
docker compose -f docker-compose.caddy.yml up -d
cd yoga-api && docker compose up -d && cd ..
```

### 5) Start FastAPI locally

```bash
source .venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6) Start frontend locally (optional host-mode dev)

```bash
cd frontend
npm run dev
```

### 7) Ensure local AI/search dependencies are available

```bash
ollama pull mistral
ollama pull nomic-embed-text
```

Useful local URLs:

- `http://localhost:5173` — YogaQ frontend
- `http://localhost:8000/docs` — FastAPI Swagger
- `http://localhost:19090/swagger-ui.html` — Spring Boot Swagger
- `http://localhost:8088/health` — Caddy-routed health check
- `http://localhost:8502` — Streamlit match demo

---

## API endpoints summary

| Area | Method | Path | Purpose |
|---|---|---|---|
| Meta | `GET` | `/health` | FastAPI health check |
| Chat | `POST` | `/chat` | RAG chat response |
| Chat | `POST` | `/chat/stream` | SSE chat stream |
| Search | `POST` | `/search/yoga` | Typesense keyword yoga search |
| Search | `POST` | `/search/yoga/semantic` | Hybrid semantic yoga search |
| Studio | `POST` | `/studio/chat` | Studio operator chat |
| Studio | `POST` | `/studio/agent` | LangGraph / CrewAI-style operator agent |
| Auth | `GET` | `/api/v1/me` | Current GitHub user + authorization state |
| Auth | `POST` | `/api/v1/access-request` | Open GitHub Issue + webhook-based approval request |
| Auth | `GET` | `/api/v1/access-status` | Poll approval status |
| Schema | `GET` | `/schema/poses` | Pose JSON-LD index |
| Schema | `GET` | `/schema/poses/{pose_id}` | `HowTo` JSON-LD |
| Schema | `GET` | `/schema/poses/{pose_id}/faq` | `FAQPage` JSON-LD |
| Schema | `GET` | `/schema/glossary` | Glossary index |
| Schema | `GET` | `/schema/glossary/{term}` | `DefinedTerm` JSON-LD |
| Schema | `GET` | `/schema/articles` | Article index |
| Schema | `GET` | `/schema/articles/{slug}` | `Article` JSON-LD |
| Schema | `GET` | `/schema/instructors` | Instructor index |
| Schema | `GET` | `/schema/instructors/{slug}` | `Person` JSON-LD |
| Schema | `GET` | `/schema/poses/{pose_id}/reviews` | `Review` / `AggregateRating` JSON-LD |
| AEO | `GET` | `/aeo/{pose_id}` | Crawlable HTML page with embedded JSON-LD |
| Sitemap | `GET` | `/schema/sitemap.xml` | XML sitemap for AI crawlers |

---

## Deployment

### WSL2 / Docker local

- Primary day-to-day environment is **WSL2 + Docker + host processes**
- Services are split across `docker-compose.yml`, `docker-compose.caddy.yml`, and `yoga-api/docker-compose.yml`
- Cloudflare Tunnel (`elbee-tunnel`) exposes the local stack publicly
- Local domains currently in use: `app.yogaman.club`, `match.yogaman.club`

### EC2

- Verified AWS target: **`i-05b1c2b1d29a78c1b`**
- Deployment label: **`team11_yogaq-app`**
- Hosts the API container and supporting runtime services for parity checks and deployment validation

### Public routing

- **`app.yogaman.club`** — primary YogaQ app
- **`match.yogaman.club`** — matching/demo entrypoint
- Both are active through Cloudflare Tunnel in the current deployment setup

---

## OCR intake pipeline

> OCR intake layer for **elbee.yogaman.club** — extracts, cleans and integrates
> book knowledge into the [yoga-chatbot](https://github.com/aiegoo/yoga-chatbot)
> search (`/yoga/search`) and chat (`/yoga/chat`) interfaces.

---

## Folder layout

```
geo/
├── screenshots/          # drop book page images here  (gitignored)
├── ocr/
│   ├── raw/              # raw tesseract output per book  (gitignored)
│   └── processed/        # cleaned plain-text copies      (tracked)
├── content/              # Jekyll Markdown with frontmatter (tracked)
├── data/json/            # ocr_database.json + indexes     (tracked)
├── scripts/
│   ├── adapt_content.py  # OCR text → Jekyll Markdown
│   ├── integrate.py      # push content into yoga-chatbot
│   └── watch.py          # auto-OCR on file drop (optional)
├── ocr_pipeline.py       # main OCR runner (entry point)
├── ROADMAP.md
└── requirements.txt
```

---

## Quick start

```bash
# 1. Install deps (tesseract already present via homebrew)
pip install -r requirements.txt

# 2. Drop screenshots into screenshots/  (jpg / png / webp)
#    Name them page_001.jpg — page_NNN.jpg (sorted order = book order)

# 3. Run OCR
python3 ocr_pipeline.py --book "Light on Yoga"

# 4. Adapt to Jekyll Markdown
python3 scripts/adapt_content.py --book "Light on Yoga"

# 5. Integrate into yoga-chatbot
python3 scripts/integrate.py --book "Light on Yoga"

# (Optional) Auto-watch folder and process on drop
python3 scripts/watch.py --book "Light on Yoga"
```

## Windows / WSL2 notes

- In WSL2, install Linux Python and Tesseract inside the distro:
  ```bash
  sudo apt update && sudo apt install -y python3.11 python3-pip python3-venv tesseract-ocr
  ```
- If Ollama runs on the Windows host and the API runs in WSL2, override the host URL:
  ```bash
  export OLLAMA_BASE_URL=http://host.docker.internal:11434
  ```
- If using native Windows Python and Tesseract is not on PATH, set:
  ```powershell
  setx TESSERACT_CMD "C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```

## Output schema

Each book produces three JSON files in `data/json/<slug>/`:

| File | Purpose |
|---|---|
| `ocr_database.json` | Full DB matching yoga-chatbot schema (metadata + pages array) |
| `page_index.json` | `{ "42": "cleaned text …" }` quick lookup |
| `keyword_index.json` | Inverted index: `{ "pranayama": [3, 17, 42, …] }` |

---

## Brand

Site: **app.yogaman.club**[0Portfolio / OCR brand: **elbee.yogaman.club**
Repo: `[git@github.com:aiegoo[90/aeogeo](https://github.com/prgrms-aibe-devcourse/AIBE5_FinalProject_Team11)`
