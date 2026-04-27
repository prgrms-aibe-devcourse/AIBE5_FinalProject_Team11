# Architecture Diagram — Smart Flow / elbee.yogaman.club

> Use as a screen-share slide during Scene 4 of the employer demo video.  
> Source ideation: [aeogeo#3](https://github.com/aiegoo/aeogeo/issues/3) · [yoga#115](https://github.com/aiegoo/yoga/issues/115)

---

## System Overview: Two Layers + Twin Growth Engines (AEO + GEO)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE INTAKE LAYER  (geo repo)                     │
│                                                                           │
│   📖 Expert Instructor Training Manuals (BKS Iyengar, etc.)               │
│          │                                                                │
│          ▼  screenshot → ocr_pipeline.py (OpenCV + pytesseract)           │
│                                                                           │
│   ┌─────────────────────────────────────────────────────────────────┐    │
│   │  adapt_content.py — per-page structured tags:                   │    │
│   │    pose_name · body_region · benefits[]                         │    │
│   │    CONTRAINDICATIONS[]  ←── KEY SAFETY DATA                     │    │
│   │    (disc · hypertension · carpal_tunnel · pregnancy · ...)      │    │
│   └─────────────────────────────────────────────────────────────────┘    │
│          │  → data/json/ : ocr_database.json + keyword_index.json         │
│          │  → content/   : Jekyll Markdown (tracked)                      │
│          │  → integrate.py → yoga-chatbot references/                     │
└──────────────────────────────┬────────────────────────────────────────────┘
                               │  REST sync
                               ▼
┌───────────────────────────────────────────────────────────────────────────┐
│              AGENTIC MATCHING LAYER  (FastAPI + LangGraph)                │
│                                                                           │
│  User speaks/types in natural language  ← AEO INPUT                      │
│  "허리 디스크인데 15분 요가 추천해줘" / "herniated disc, 15 min"            │
│          │                                                                │
│          ▼                                                                │
│  ┌─────────────────────────────────────────────────────────────────┐     │
│  │              LangGraph State Machine (app/agents/graph.py)      │     │
│  │                                                                 │     │
│  │  State 1: parse_input                                           │     │
│  │     └─ extract health_flags, goals, duration, location          │     │
│  │                                                                 │     │
│  │  State 2: parallel_fetch (3 branches)                          │     │
│  │     ├─ a) CONTRAINDICATION FILTER  ←── RED ✗ unsafe poses       │     │
│  │     ├─ b) find_nearby_studios      ←── /api/v1/studios/nearby   │     │
│  │     └─ c) llama_index_retrieve     ←── semantic pose chunks     │     │
│  │                                                                 │     │
│  │  State 3: score_and_rank → POST /api/v1/match                   │     │
│  │                                                                 │     │
│  │  State 4: CrewAI crew (app/agents/crew.py)                      │     │
│  │     ├─ Analyst Agent  → context: location + time + weather      │     │
│  │     ├─ Matcher Agent  → top 3 safe poses + 1 studio             │     │
│  │     └─ Writer Agent   → Korean GEO copy for studio marketing    │     │
│  │                                                                 │     │
│  │  State 5: return_response                                       │     │
│  │     └─ { poses[], studio, copy_ko, copy_en, json_ld }           │     │
│  └─────────────────────────────────────────────────────────────────┘     │
└───────────────────────────┬──────────────────────┬────────────────────────┘
                            │                      │
                            ▼                      ▼
         ┌──────────────────────┐     ┌────────────────────────────┐
         │   AEO CHANNEL (User) │     │   GEO CHANNEL (Studio)     │
         │                      │     │                            │
         │  elbee.yogaman.club  │     │  Studio receives:          │
         │  /yoga/search        │     │  • Pre-qualified lead      │
         │  /yoga/chat          │     │  • User health profile     │
         │                      │     │  • Korean geo-targeted copy│
         │  "Safe. Specific.    │     │  "Rehab yoga → disc patient│
         │   Smart."            │     │   No mass ads. Precision." │
         └──────────────────────┘     └────────────────────────────┘
```

---

## Twin Growth Engine Explanation

| Engine | Stands for | How it works here |
|---|---|---|
| **AEO** | Answer Engine Optimisation | User states need in natural language → AI returns the precise expert answer with source citation. No search fatigue. |
| **GEO** | Generative Engine Optimisation | AI generates Korean geo-targeted copy → routes pre-qualified leads to the right local studio. No paid ads. |

> From yoga#115: *"앱에서 분석된 사용자의 신체 데이터를 바탕으로, 해당 부위에 특화된 전문성을 가진 인근 스튜디오를 연결합니다."*  
> (The app connects users to nearby studios specialised in the exact body area.)

---

## Three Target User Personas (from yoga#115)

| Persona | Problem | Solution |
|---|---|---|
| 🧘 **Injury/rehab practitioner** | Disc, wrist, hypertension — afraid to follow generic videos | Contraindication AI filter removes unsafe poses in real time |
| 🧘 **Nomadic practitioner** | Wastes 10+ min finding the right session across thousands of YouTube videos | AEO engine: say your condition, get the expert sequence instantly |
| 🏢 **Local yoga studio** | Losing members to home workout trend; stuck in price competition | GEO engine: receive pre-qualified leads matched to studio specialty |

---

## Technology Stack Summary

| Layer | Technology |
|---|---|
| OCR + image preprocessing | pytesseract + OpenCV |
| Contraindication tagging | `adapt_content.py` — per-page frontmatter |
| Pipeline orchestration | LangGraph state machine |
| Semantic search (AEO) | LlamaIndex VectorStoreIndex |
| Multi-agent generation (GEO) | CrewAI: Analyst + Matcher + Writer |
| LLM backend | Ollama — mistral:latest (local, no API cost) |
| API | FastAPI |
| Frontend | Jekyll + Vite + Tailwind |
| CI | GitHub Actions |
| Hosting | GitHub Pages + custom domain |

---

## Export to PNG

```bash
# Option 1: grip
pip install grip
grip video/ARCHITECTURE_DIAGRAM.md --export video/architecture.png

# Option 2: VS Code
# Cmd+Shift+P → "Markdown: Open Preview" → right-click → Save as image
```
