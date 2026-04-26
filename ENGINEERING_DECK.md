# YOGA MATCHING CURATOR — Engineering Build Deck
> **Project:** `aiegoo/aeogeo`  ·  **Brand:** `elbee.yogaman.club`  ·  **Last Updated:** 2026-04-26

---

## ▌ 0. What This Project Is

A production-grade AI-native yoga matching platform that:

- Recommends yoga poses and studio sessions using **E-E-A-T trust signals**
- Enforces **Kill-Switch safety rules** for medical contraindications
- Publishes **Schema.org JSON-LD** to be cited by Perplexity, SearchGPT, Gemini
- Serves a **location-based studio search** (Haversine / PostGIS)
- Powers **elbee.yogaman.club** as a white-label employer portfolio demo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     THE FLYWHEEL                                            │
│                                                                             │
│   SUPPLY SIDE             MATCHING ENGINE             DEMAND SIDE           │
│   ──────────              ───────────────             ──────────            │
│   2700+ Poses   ───────►  Kill-Switch Filter  ──────► User Session          │
│   10 Studios    ───────►  Trust Score Rank    ──────► Booking Intent        │
│   10 Instructors ──────►  Haversine Nearby    ──────► Studio Reservation    │
│        │                        │                          │                │
│        ▼                        ▼                          ▼                │
│   Schema.org JSON-LD ──► AI Search Citation ──────► Organic Discovery      │
│   (HowTo / FAQPage)     Perplexity / Gemini          elbee.yogaman.club     │
│                         SearchGPT                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ▌ 1. Infrastructure Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FULL STACK OVERVIEW                                 │
├─────────────────────┬───────────────────────────────────────────────────────┤
│  LAYER              │  TECH                                                 │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  Frontend           │  Vite + React  (port 5173)                            │
│                     │  Proxies:  /search → :8000                            │
│                     │            /chat   → :8000                            │
│                     │            /api/v1 → :19090                           │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  Python API         │  FastAPI   (port 8000)                                │
│                     │  Ollama mistral + nomic-embed-text (127.0.0.1:11434)  │
│                     │  RAG service · chat · search · agent                  │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  Java API           │  Spring Boot 3.2.2, Java 17, Maven                   │
│                     │  Docker → Windows host (port 19090)                   │
│                     │  Flyway auto-migration on startup                     │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  Database           │  PostgreSQL 16  (Docker, Windows host)                │
│                     │  Tables: poses, instructors, studios, sessions,       │
│                     │          benefits, contraindications                  │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  AI / Embeddings    │  Ollama (WSL2 / 127.0.0.1:11434)                      │
│                     │  mistral:latest     — chat completions                │
│                     │  nomic-embed-text   — vector embeddings               │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  Schema / AEO       │  Schema.org JSON-LD  (FAQPage · WebSite · HowTo)      │
│                     │  Static injection in index.html                       │
│                     │  React JsonLd component (runtime)                     │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

### Network Topology

```
  WSL2 Host (Ubuntu)
  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │   :5173  Vite+React ──proxy──► :8000  FastAPI           │
  │                     ──proxy──► :19090 Java API          │
  │                                   │                     │
  │   :11434 Ollama  ◄────────────────┘                     │
  │   (127.0.0.1)                     │                     │
  │                                   ▼                     │
  │                           Windows Host Docker           │
  │                           PostgreSQL :5432 (internal)   │
  └─────────────────────────────────────────────────────────┘

  Git remote: github.com:aiegoo/aeogeo  (SSH, port 22)
```

---

## ▌ 2. Repository Layout

```
aeogeo/
├── yoga-api/                      ← Java Spring Boot API
│   ├── src/main/java/
│   │   └── club/yogaman/api/
│   │       ├── matching/          ← MatchController, MatchService, MatchResult
│   │       ├── pose/              ← Pose entity, PoseController
│   │       ├── instructor/        ← Instructor entity, InstructorController
│   │       ├── studio/            ← Studio entity, StudioController, StudioDistance
│   │       └── session/           ← Session entity, SessionController
│   ├── src/main/resources/
│   │   └── db/migration/          ← Flyway V1 … V6 SQL scripts
│   └── src/test/java/
│       └── club/yogaman/api/
│           ├── matching/          ← MatchControllerIT
│           └── studio/            ← StudioControllerIT  [NEW]
│
├── app/                           ← FastAPI Python service
│   ├── services/                  ← rag_service, llm_service, search_service
│   └── api/                       ← chat.py, search.py endpoints
│
├── frontend/                      ← Vite+React SPA
│   ├── index.html                 ← Static JSON-LD blocks (FAQPage + WebSite)
│   └── src/
│       ├── schemas/faqSchema.js   ← Canonical FAQ data + schema builders
│       └── components/JsonLd.jsx  ← Runtime <script type="application/ld+json">
│
├── scripts/                       ← Python data pipeline tools
│   ├── enrich_poses.py
│   ├── scrape_instructors.py
│   └── generate_pose_insert_sql.py
│
└── data/                          ← Seed data and JSON exports
    ├── yoga_locations.json
    └── poses/
```

---

## ▌ 3. Milestones — Completed

---

### MILESTONE 1 — Phase 0: Project Scaffold
> **Date:** 2026-04-15  ·  **Status:** ✅ SHIPPED

```
WHAT WAS BUILT
──────────────
  screenshots/          image drop zone (gitignored)
  ocr/                  pytesseract + OpenCV pipeline output
  content/              topic-tagged Jekyll Markdown (tracked)
  data/json/            structured JSON exports
  scripts/
    ocr_pipeline.py     → pytesseract + OpenCV → JSON
    adapt_content.py    → OCR text → tagged Markdown
    integrate.py        → syncs to yoga-chatbot references/
    watch.py            → file-watcher: image drop → auto-process
  requirements.txt
  README.md

OUTCOME
───────
  Zero-to-repo in one day.
  Drop a book screenshot → auto-OCR → auto-Markdown → indexed in /yoga/search.
```

---

### MILESTONE 2 — Phase 1: E-E-A-T Data Schema
> **Status:** ✅ SHIPPED  ·  **Commit:** exists in history

```
WHAT WAS BUILT
──────────────
  schemas/pose_eat_schema.json          E-E-A-T pose schema definition
  data/poses/poses_eat_schema.json      Enriched pose export (2700+ base)
  scripts/enrich_poses.py               Enrichment pipeline

SCHEMA STRUCTURE
────────────────

  Pose (E-E-A-T Extended)
  ┌──────────────────────────────────────────────────────┐
  │ pose_id           "trikonasana_001"                  │
  │ canonical_name    "Trikonasana"                      │
  │ common_name       "Triangle Pose"                    │
  │ difficulty_rank   1 – 5                              │
  │ anatomical_focus  ["hip", "hamstring", "spine"]      │
  │ benefits[]        { tag, weight }                    │
  │ contraindications[]  { condition, severity,          │
  │                        kill_switch, instruction }    │
  │ geo_keywords      ["yoga for back pain Seoul"]       │
  │ aeo_summary       "AI-facing 1-paragraph summary"    │
  │ schema_org        { HowTo JSON-LD object }           │
  └──────────────────────────────────────────────────────┘

  kill_switch = true  →  pose BLOCKED for that condition, always
  severity    CRITICAL | MEDICAL_CLEARANCE | CAUTION
```

---

### MILESTONE 3 — Spring Boot API Scaffold (yoga-api/)
> **Status:** ✅ SHIPPED

```
WHAT WAS BUILT
──────────────
  yoga-api/              Spring Boot 3.2.2 project
  ├── Pose.java          JPA entity (+ natural_description via V2 migration)
  ├── Benefit.java
  ├── Contraindication.java
  ├── EducationalMetadata.java
  ├── MatchService.java
  ├── MatchController.java
  ├── MatchResult.java
  └── SchemaOrgService.java   → HowTo JSON-LD builder

  Flyway migrations:
  V1__create_pose_tables.sql
  V2__add_natural_description.sql

  Dockerfile + docker-compose.yml  (run without local Java)

ENDPOINTS LIVE
──────────────
  POST /api/v1/match          → MatchResult[]
  GET  /api/v1/poses          → Pose[]
  GET  /api/v1/poses/{id}     → Pose
  GET  /api/v1/poses/{id}.jsonld  → HowTo JSON-LD
```

---

### MILESTONE 4 — T-001: Fix Match Scoring (Always 0.0)
> **Date:** 2026-04-25  ·  **Commit:** `cd5e1b0`  ·  **Status:** ✅ SHIPPED

```
ROOT CAUSE
──────────
  UI sends goal strings like "Spinal_Mobility"
  DB benefit tags are lowercase words like "mobility", "back", "flexibility"
  equalsIgnoreCase("Spinal_Mobility", "mobility") → FALSE → score = 0.0

FIX: GOAL_TAG_MAP in MatchService.java
───────────────────────────────────────
  private static final Map<String, List<String>> GOAL_TAG_MAP = Map.of(
      "Spinal_Mobility",  List.of("mobility","back","flexibility","release","posture"),
      "Back_Pain_Relief", List.of("back","relief","stress","posture","release"),
      "Core_Strength",    List.of("core","strength","stability"),
      "Hip_Flexibility",  List.of("hip","flexibility","mobility","release"),
      "Balance",          List.of("balance","stability"),
      "Stress_Relief",    List.of("stress","relief","release"),
      "Shoulder_Opening", List.of("shoulder","release","flexibility"),
      "Strength",         List.of("strength","core","stability")
  );

FLOW AFTER FIX
──────────────
  goal: "Spinal_Mobility"
        │
        ▼  expand via GOAL_TAG_MAP
  expandedTags: { mobility, back, flexibility, release, posture }
        │
        ▼  for each pose benefit tag
  tag "mobility"  →  matched  →  adds benefit.weight to score
  tag "back"      →  matched  →  adds benefit.weight to score
        │
        ▼
  MatchResult.scored(pose, 0.74)   ← non-zero!

TEST ADDED
──────────
  MatchControllerIT.goalTagMapExpandsSpinalMobilityToNonZeroScore()
  Asserts: at least one result has score > 0.0
```

---

### MILESTONE 5 — T-003/T-004: V5 Studio + Session Seeds
> **Date:** 2026-04-25  ·  **Commit:** `b4067c6`  ·  **Status:** ✅ SHIPPED

```
WHAT WAS BUILT
──────────────
  V5__seed_sessions_and_studios.sql  (Flyway auto-applied on startup)

STUDIOS SEEDED (10)
───────────────────
  City          Count   Studios
  ──────────    ─────   ────────────────────────────────────────
  Seoul, KR       3     Inner Peace Yoga, Seoul Flow Studio,
                        Hannam Yoga Collective
  Tokyo, JP       2     Shibuya Yoga Lab, Nakameguro Yoga House
  Singapore, SG   2     Marina Bay Yoga, Tiong Bahru Studio
  New York, US    2     Brooklyn Yoga Loft, Manhattan Slow Flow
  London, UK      1     Shoreditch Yoga Works

SESSIONS SEEDED (16)
─────────────────────
  user_001 → 5 sessions  (mix: online/offline, completed/ongoing)
  user_002 → 4 sessions
  user_003 → 6 sessions (including 1 with NULL completed_at)

ENTITY SCHEMA
─────────────
  sessions
  ┌───────────────────────────────────────┐
  │ session_id    UUID                    │
  │ user_id       VARCHAR                 │
  │ studio_id     FK → studios            │
  │ pose_id       FK → poses (nullable)   │
  │ started_at    TIMESTAMPTZ             │
  │ completed_at  TIMESTAMPTZ (nullable)  │
  │ session_type  online | offline        │
  └───────────────────────────────────────┘
```

---

### MILESTONE 6 — T-022: AEO/GEO JSON-LD (FAQPage + WebSite)
> **Date:** 2026-04-25  ·  **Commit:** `1a15b4f`  ·  **Status:** ✅ SHIPPED

```
WHY THIS MATTERS
────────────────
  Perplexity, SearchGPT, Gemini cite pages that have structured data.
  FAQPage schema → AI reads Q&As directly → cites yogaman.club as source.
  WebSite schema → enables Google Sitelinks search box.

DUAL INJECTION STRATEGY
────────────────────────

  ① Static (index.html — instant, no JS required)
  ─────────────────────────────────────────────────
  <head>
    <script type="application/ld+json">
      { "@type": "FAQPage", ... 7 Q&As ... }
    </script>
    <script type="application/ld+json">
      { "@type": "WebSite", "potentialAction": { SearchAction } }
    </script>
  </head>

  ② React Runtime (JsonLd.jsx — SPA hydration)
  ──────────────────────────────────────────────
  App.jsx
  └── <JsonLd schema={FAQ_SCHEMA}     id="schema-faqpage" />
  └── <JsonLd schema={WEBSITE_SCHEMA} id="schema-website" />

  JsonLd.jsx  →  useEffect: creates/removes <script id="..."> dynamically
              →  deduplication by id prevents double injection

FAQ CONTENT (10 Q&As)
──────────────────────
  Q: What yoga poses help with back pain?
  Q: How do I find yoga studios near me in Seoul?
  Q: What is a kill-switch in yoga pose matching?
  Q: How is instructor trust score calculated?
  Q: What is E-E-A-T in yoga content?
  … (10 total in faqSchema.js)

FILES
──────
  frontend/index.html                   ← static <script> blocks
  frontend/src/schemas/faqSchema.js     ← FAQ_ITEMS, buildFaqPageSchema()
  frontend/src/components/JsonLd.jsx    ← React runtime injection
  frontend/src/App.jsx                  ← mounts both schemas
```

---

### MILESTONE 7 — V6: 10 Seoul Instructor Seeds + Trust Scores
> **Date:** 2026-04-25  ·  **Commit:** `159764f`  ·  **Status:** ✅ SHIPPED

```
TRUST SCORE FORMULA
────────────────────
  trust_score =
      cert_weight                              [0.0 – 1.0]
    + (avg_rating / 5.0) × 0.3                [0.0 – 0.3]
    + min(lineage_depth, 4) × 0.05            [0.0 – 0.2]
    + min(log10(ig_followers) / 7.0, 0.1)     [0.0 – 0.1]
    ──────────────────────────────────────────
    capped at 1.000

  cert_weight:
    E-RYT-500  = 1.0
    E-RYT-200  = 0.8
    RYT-500    = 0.6
    RYT-200    = 0.4
    YACEP      = 0.2

10 SEEDED INSTRUCTORS (Seoul, KR)
──────────────────────────────────
  instructor_id       cert          trust_score
  ─────────────────   ──────────    ───────────
  lee-ji-woo          E-RYT-500     1.000
  park-sun-young      E-RYT-200     1.000  ← high rating compensates
  kim-min-jun         RYT-500       1.000  ← high rating + lineage
  lim-soo-ah          RYT-500       1.000
  yoon-tae-yang       E-RYT-500     1.000
  kwon-ji-hoon        RYT-500       1.000
  choi-yeon-seo       RYT-200       0.820
  han-mi-rae          RYT-200       0.808
  jung-ha-eun         RYT-200       0.752
  oh-se-jin           YACEP         0.540

INSTRUCTOR ENTITY
─────────────────
  instructors
  ┌──────────────────────────────────────────────────┐
  │ instructor_id          VARCHAR (slug, PK)         │
  │ full_name              VARCHAR                    │
  │ certification_level    ENUM                       │
  │ lineage_school         VARCHAR                    │
  │ lineage_depth          INT                        │
  │ instagram_handle       VARCHAR                    │
  │ instagram_followers    INT                        │
  │ avg_rating             DECIMAL(3,2)               │
  │ review_count           INT                        │
  │ instructor_trust_score DECIMAL(5,3)               │
  │ specialties            TEXT[]                     │
  │ city / country         VARCHAR                    │
  │ data_source            VARCHAR   ('manual')       │
  └──────────────────────────────────────────────────┘

ENDPOINTS
─────────
  GET  /api/v1/instructors?city=Seoul&specialty=vinyasa
  GET  /api/v1/instructors/{id}
  POST /api/v1/instructors
```

---

### MILESTONE 8 — Phase 4: /studios/nearby  (Haversine Distance Search)
> **Date:** 2026-04-26  ·  **Commit:** `534d3e5`  ·  **Status:** ✅ SHIPPED

```
WHAT WAS BUILT
──────────────
  StudioDistance.java        DTO: Studio + distanceKm (2 decimal places)
  StudioService.java         findNearby(lat, lng, radiusKm)
  StudioController.java      GET /api/v1/studios/nearby
  StudioControllerIT.java    4 integration tests
  studio-seed.sql            Test data: 2 Seoul studios + 1 Busan outlier

HAVERSINE ALGORITHM
────────────────────
  Input:  user lat/lng  +  radius (km, default 10)

  For each studio with coordinates:
  ┌──────────────────────────────────────────────────────┐
  │  dLat = toRadians(studio.lat - user.lat)             │
  │  dLng = toRadians(studio.lng - user.lng)             │
  │                                                      │
  │  a = sin²(dLat/2)                                    │
  │    + cos(user.lat) × cos(studio.lat) × sin²(dLng/2) │
  │                                                      │
  │  distance = 6371 × 2 × atan2(√a, √(1−a))  [km]      │
  └──────────────────────────────────────────────────────┘

  Filter:  distance <= radius
  Sort:    ascending by distance

API USAGE
──────────
  GET /api/v1/studios/nearby?lat=37.5665&lng=126.9780&radius=5

  Response:
  [
    {
      "studio": { "name": "Inner Peace Yoga", "city": "Seoul", ... },
      "distanceKm": 0.47
    },
    {
      "studio": { "name": "Seoul Flow Studio", "city": "Seoul", ... },
      "distanceKm": 1.23
    }
  ]

TESTS (all green)
──────────────────
  ✓ nearbyReturnsOnlyStudiosWithinRadius     (radius=5, expects 2 Seoul only)
  ✓ nearbyResultsSortedByAscendingDistance   (order check)
  ✓ nearbyDefaultRadiusIs10km               (no radius param → default 10)
  ✓ nearbyEmptyWhenRadiusTooSmall           (radius=0.1 → [])
```

---

## ▌ 4. Flyway Migration Timeline

```
  V1__create_pose_tables.sql
  │   poses, benefits, contraindications, educational_metadata
  │
  V2__add_natural_description.sql
  │   ALTER TABLE poses ADD COLUMN natural_description TEXT
  │
  V3__create_instructors.sql
  │   instructors (trust_score, cert_level, lineage, instagram, specialties[])
  │
  V4__create_studios_sessions.sql
  │   studios (name, city, country, lat, lng, ...)
  │   sessions (user_id, studio_id, started_at, completed_at, session_type)
  │
  V5__seed_sessions_and_studios.sql
  │   10 studios across 5 cities + 16 sessions across 3 demo users
  │
  V6__seed_instructors.sql
      10 Seoul instructors with pre-computed trust scores

  Applied automatically by Flyway on Spring Boot startup.
  No manual DB management required.
```

---

## ▌ 5. API Surface — What Works Now

```
  BASE URL: http://localhost:19090

  ┌─────────────────────────────────────────────────────────────────┐
  │  ENDPOINT                           WHAT IT DOES               │
  ├─────────────────────────────────────────────────────────────────┤
  │  POST /api/v1/match                 Kill-Switch + scored match  │
  │                                     GOAL_TAG_MAP expansion       │
  │                                     Returns MatchResult[]        │
  │                                                                  │
  │  GET  /api/v1/poses                 All poses                   │
  │  GET  /api/v1/poses/{id}            Single pose                 │
  │  GET  /api/v1/poses/{id}.jsonld     HowTo JSON-LD               │
  │                                                                  │
  │  GET  /api/v1/instructors           All instructors (filterable) │
  │  GET  /api/v1/instructors/{id}      Single instructor            │
  │  POST /api/v1/instructors           Create instructor            │
  │                                                                  │
  │  GET  /api/v1/studios               All studios (city filter)   │
  │  GET  /api/v1/studios/{id}          Single studio               │
  │  GET  /api/v1/studios/nearby        ← NEW: Haversine search     │
  │       ?lat=&lng=&radius=            returns StudioDistance[]     │
  │  POST /api/v1/studios               Create studio               │
  │                                                                  │
  │  GET  /api/v1/sessions              All sessions                │
  │  POST /api/v1/sessions              Create session              │
  └─────────────────────────────────────────────────────────────────┘
```

---

## ▌ 6. Data Flow — End to End

```
  USER INPUT
  ──────────
  { goals: ["Spinal_Mobility", "Back_Pain_Relief"],
    conditions: ["herniated_disc"],
    difficulty_max: 3,
    lat: 37.5665, lng: 126.9780, radius: 5 }
        │
        ▼
  POST /api/v1/match
        │
        ├─► GOAL_TAG_MAP expansion
        │     "Spinal_Mobility" → {mobility, back, flexibility, release, posture}
        │     "Back_Pain_Relief" → {back, relief, stress, posture, release}
        │     union → expandedTags
        │
        ├─► Kill-Switch filter
        │     pose.contraindications[].condition == "herniated_disc"
        │     && kill_switch == true
        │     → MatchResult.blocked(pose, "herniated_disc: avoid backbends")
        │
        ├─► Score calculation (surviving poses)
        │     for each benefit tag in expandedTags:
        │       if pose.benefits[].tag matches → score += benefit.weight
        │     → MatchResult.scored(pose, 0.74)
        │
        └─► Return sorted by score DESC

  PARALLEL:  GET /api/v1/studios/nearby?lat=37.5665&lng=126.9780&radius=5
        │
        ├─► Load all studios with coordinates
        ├─► Haversine distance for each
        ├─► Filter ≤ 5 km
        └─► Sort ascending → StudioDistance[]
```

---

## ▌ 7. AEO / GEO Content Pipeline

```
  HOW AI SEARCH ENGINES FIND US
  ──────────────────────────────

  ┌──────────────────────────────────────────────────────────────────┐
  │  index.html (static, pre-hydration)                              │
  │  ┌────────────────────────────────────────────┐                  │
  │  │  <script type="application/ld+json">       │                  │
  │  │    {                                       │                  │
  │  │      "@type": "FAQPage",                   │◄── crawled by    │
  │  │      "mainEntity": [                       │    Perplexity    │
  │  │        { "Q": "What poses for back pain?"  │    SearchGPT     │
  │  │          "A": "Mountain, Cat-Cow, Child's  │    Gemini        │
  │  │                Pose are recommended ..." } │                  │
  │  │      ]                                     │                  │
  │  │    }                                       │                  │
  │  │  </script>                                 │                  │
  │  └────────────────────────────────────────────┘                  │
  │                                                                  │
  │  App.jsx (React runtime, SPA hydration)                          │
  │  <JsonLd schema={FAQ_SCHEMA}     id="schema-faqpage" />          │
  │  <JsonLd schema={WEBSITE_SCHEMA} id="schema-website" />          │
  └──────────────────────────────────────────────────────────────────┘

  WHY DUAL INJECTION?
  ───────────────────
  Static  → Googlebot, Perplexity see it even without JS execution
  Runtime → Keeps schema in sync with React app state / future dynamic data
```

---

## ▌ 8. Git History — Session Commits

```
  534d3e5  feat(studios): add GET /api/v1/studios/nearby with Haversine
           └── StudioDistance.java  StudioService.java  StudioController.java
               StudioControllerIT.java  studio-seed.sql

  159764f  feat: V6 seed 10 Seoul instructors with pre-computed trust scores
           └── V6__seed_instructors.sql

  1a15b4f  feat(T-022): FAQPage + WebSite JSON-LD for AEO/GEO
           └── index.html  faqSchema.js  JsonLd.jsx  App.jsx

  b4067c6  feat(T-003/T-004): V5 seed 10 studios + 16 sessions
           └── V5__seed_sessions_and_studios.sql

  cd5e1b0  fix(T-001): GOAL_TAG_MAP expansion fixes match scoring 0.0
           └── MatchService.java  MatchResult.java  MatchControllerIT.java
```

---

## ▌ 9. Test Coverage

```
  INTEGRATION TESTS (Spring Boot, H2 in-memory, TestRestTemplate)
  ──────────────────────────────────────────────────────────────────
  MatchControllerIT
  ├── matchReturnsResultsForValidRequest
  ├── matchBlocksPoseWhenKillSwitchActive
  ├── matchFiltersOnMaxDifficultyRank
  └── goalTagMapExpandsSpinalMobilityToNonZeroScore  ← T-001 regression

  StudioControllerIT                                 ← NEW (Milestone 8)
  ├── nearbyReturnsOnlyStudiosWithinRadius
  ├── nearbyResultsSortedByAscendingDistance
  ├── nearbyDefaultRadiusIs10km
  └── nearbyEmptyWhenRadiusTooSmall
```

---

## ▌ 10. What's Next (Roadmap)

```
  STATUS LEGEND:  ✅ done  🔄 in progress  ⬜ not started  🔴 deferred

  PHASE 2 — Java API completion
  ──────────────────────────────
  ✅  MatchService GOAL_TAG_MAP scoring
  ✅  V5 studio + session seeds
  ✅  V6 instructor seeds + trust scores
  ✅  /studios/nearby Haversine endpoint
  ⬜  Instructor trust score BATCH RECALC (Python daily job)
  ⬜  SchemaOrgService.buildHowTo() wired to real pose DB rows
  ⬜  HowTo, Course, DefinedTerm JSON-LD (only FAQPage done)

  PHASE 3 — AEO/GEO
  ──────────────────
  ✅  FAQPage + WebSite JSON-LD (static + React)
  ⬜  /glossary/:pose/ Jekyll landing pages + per-pose JSON-LD
  ⬜  AI citation tracking (Google Search Console API)
  ⬜  A/B test: HowTo vs DefinedTerm schema effectiveness

  PHASE 4 — Studio API integration
  ──────────────────────────────────
  ✅  Haversine nearby search
  ⬜  MindbodyAdapter (live booking slots)
  ⬜  OneClubAdapter
  ⬜  PostGIS upgrade (replace in-memory Haversine for scale)

  PHASE 5 — Monetisation
  ────────────────────────
  ⬜  Pilot proposal for 3 Seoul studios
  ⬜  Conversion rate dashboard
  ⬜  White-label API packaging

  DEFERRED
  ─────────
  🔴  Playwright-based Yoga Alliance scraper
      (BeautifulSoup cannot parse JS-rendered YA directory)
      → replace httpx+BS4 with Playwright headless browser
```

---

## ▌ 11. Key Design Decisions

| Decision | Choice | Why |
|----------|---------|-----|
| Kill-Switch enforcement | Hard block, score = 0, reason returned | Safety first — medical risk must never be silently ignored |
| GOAL_TAG_MAP | Static Map in Java | UI goals are a closed enum; no DB lookup overhead needed |
| Haversine vs PostGIS | Haversine in Java | No PostGIS extension yet; Java Haversine is accurate to < 1 km for city-scale searches |
| Instructor data | Manual seed (V6) | YA directory is JS-rendered; BeautifulSoup fails; Playwright scraper deferred |
| JSON-LD injection | Dual (static + React) | Static serves crawlers; React keeps SPA in sync |
| Trust score | Pre-computed on seed | Avoids expensive join at query time; recalc job will refresh nightly |
| Flyway | Auto-applied on startup | Zero-config DB state management; no manual migration steps |

---

*End of Engineering Deck — `aiegoo/aeogeo` · 2026-04-26*
