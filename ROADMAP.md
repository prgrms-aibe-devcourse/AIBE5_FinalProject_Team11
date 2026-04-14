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

## Key metrics to track

| Metric | Baseline | Target |
|---|---|---|
| Pages processed | 0 | 500+ |
| OCR accuracy (manual sample) | — | ≥ 90% |
| Search latency | — | < 200ms |
| Books integrated | 0 | 3+ |
| Chat answers sourced from geo | 0% | > 30% |
