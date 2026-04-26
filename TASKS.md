# TASKS — aeogeo / yoga matching system
*Generated: 2026-04-22 | Branch: `master` | All confirmed-running services: yoga-api :19090, yoga-search-api :5001, yoga-chat-api :5002, postgres :8879, ollama :11434*

---

## Priority 1 — Critical Bugs

### T-001 Fix match scoring always returns 0.0
**Status:** ✅ Done — commit `cd5e1b0`  
**File:** `yoga-api/src/main/java/club/yogaman/api/matching/MatchService.java`

**Root cause:** `MatchService.score()` compares goal strings from the request
(`"Spinal_Mobility"`, `"Back_Pain"`) against `pose_benefits.tag` values from the DB
(`"flexibility"`, `"mobility"`, `"strength"`, `"back"`, …).
`equalsIgnoreCase` never matches because the goal vocabulary and tag vocabulary are
completely different.

**Two-part fix required:**

**Part A — define canonical goal-to-tag mapping in `MatchService`**
```java
private static final Map<String, List<String>> GOAL_TAG_MAP = Map.of(
    "Spinal_Mobility",  List.of("mobility", "back", "flexibility", "release"),
    "Back_Pain_Relief", List.of("back", "relief", "stress", "posture"),
    "Core_Strength",    List.of("core", "strength", "stability"),
    "Hip_Flexibility",  List.of("hip", "flexibility", "mobility", "release"),
    "Balance",          List.of("balance", "stability"),
    "Stress_Relief",    List.of("stress", "relief", "release"),
    "Shoulder_Opening", List.of("shoulder", "release", "flexibility"),
    "Strength",         List.of("strength", "core", "stability")
);
```
In `score()`, expand each goal into its mapped tags before comparing:
```java
Set<String> expandedTags = goals.stream()
    .flatMap(g -> GOAL_TAG_MAP.getOrDefault(g, List.of(g.toLowerCase())).stream())
    .collect(Collectors.toSet());
if (expandedTags.stream().anyMatch(t -> t.equalsIgnoreCase(b.getTag()))) {
    score += b.getWeight();
}
```

**Part B — update `MatchRequest` goals enum/validation**  
Add JavaDoc or `@Schema` annotation listing supported goal values for the OpenAPI spec.

**Acceptance criteria:**
- `POST /api/v1/match` with `goals: ["Spinal_Mobility"]` returns poses with `score > 0.0`
- Poses with `back`, `mobility` tags score highest
- Blocked poses still return `blocked: true, score: 0.0`

---

### T-002 Ollama healthcheck marked "unhealthy" on every restart
**Status:** 🟡 Low priority (cosmetic — service works)  
**Container:** `yoga-ollama` (managed by Windows Docker Desktop; compose file at `D:\repos\devcourse\yoga\rag_pipeline\docker-compose.yml` — not in this repo)

**Root cause:** Healthcheck uses `curl` which is not in the Ollama Ubuntu 24.04 image.
`docker update --health-cmd` is not supported.

**Fix:** Edit the Docker Compose file on the Windows host — replace:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:11434/"]
```
with:
```yaml
healthcheck:
  test: ["CMD-SHELL", "ollama list || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
```
Then `docker compose down yoga-ollama && docker compose up -d yoga-ollama`.

**Note:** Until the Windows compose file is updated, the "unhealthy" badge in the
dashboard is purely cosmetic. Both `mistral:latest` (4.4 GB) and
`nomic-embed-text:latest` (274 MB) are confirmed loaded and responding.

---

## Priority 2 — Data / Database

### T-003 Seed sessions table with sample data
**Status:** ✅ Done — V5 migration, commit `b4067c6`  
**Table:** `sessions` (16 rows — seeded by V5__seed_sessions_and_studios.sql)

**Purpose:** `/api/v1/sessions` returns `[]`; the dashboard "Sessions" row shows `Array(0)`;
the matching engine cannot score session history.

**Implementation:** Create `yoga-api/src/main/resources/db/migration/V4__seed_sample_data.sql`
```sql
-- Sample sessions: 5 users × 3 poses each
INSERT INTO sessions (user_id, pose_id, started_at, completed_at) VALUES
  ('user_001', 'mountain_pose',       '2026-04-01 09:00:00+09', '2026-04-01 09:30:00+09'),
  ('user_001', 'downward_facing_dog', '2026-04-02 09:00:00+09', '2026-04-02 09:30:00+09'),
  ('user_001', 'warrior_i',           '2026-04-03 09:00:00+09', '2026-04-03 09:30:00+09'),
  ('user_002', 'triangle_pose',       '2026-04-01 18:00:00+09', '2026-04-01 18:45:00+09'),
  ('user_002', 'seated_forward_fold', '2026-04-02 18:00:00+09', '2026-04-02 18:40:00+09'),
  ('user_003', 'child_pose',          '2026-04-05 08:00:00+09', '2026-04-05 08:20:00+09'),
  ('user_003', 'cobra_pose',          '2026-04-06 08:00:00+09', '2026-04-06 08:25:00+09'),
  ('user_004', 'warrior_ii',          '2026-04-10 07:30:00+09', '2026-04-10 08:00:00+09'),
  ('user_005', 'bridge_pose',         '2026-04-15 19:00:00+09', '2026-04-15 19:30:00+09');
```
> **Note:** Verify that the `pose_id` values above exist in the `poses` table before
> inserting. Run: `docker exec yoga-api-postgres-1 psql -U postgres -d yogadb -c "SELECT pose_id FROM poses WHERE pose_id IN ('mountain_pose','downward_facing_dog','warrior_i') LIMIT 5;"`
> If pose IDs differ, adjust to match actual slugs in the DB.

**Acceptance criteria:**
- `GET /api/v1/sessions` returns at least 9 objects
- Dashboard "Sessions" row shows status 200 with non-empty preview

---

### T-004 Seed studios table with sample data
**Status:** ✅ Done — V5 migration + V6 instructors, commits `b4067c6` / `159764f`  
**Table:** `studios` (10 rows, 5 cities: Seoul·Busan·Daegu·Daejeon·Gwangju); `instructors` (10 Seoul instructors seeded with trust scores via V6)

**Implementation:** Add to the same `V4__seed_sample_data.sql` above:
```sql
INSERT INTO studios (name, city, country, latitude, longitude) VALUES
  ('Seoul Yoga Studio',      'Seoul',  'KR',  37.5665, 126.9780),
  ('Gangnam Yoga Center',    'Seoul',  'KR',  37.4979, 127.0276),
  ('Hongdae Yoga Lab',       'Seoul',  'KR',  37.5563, 126.9235),
  ('Tokyo Flow Studio',      'Tokyo',  'JP',  35.6762, 139.6503),
  ('Busan Beach Yoga',       'Busan',  'KR',  35.1796, 129.0756),
  ('Jeju Island Retreat',    'Jeju',   'KR',  33.4996, 126.5312);
```

**Acceptance criteria:**
- `GET /api/v1/studios` returns 6 objects with name, city, country, lat/lng fields
- Dashboard "Studios" row shows status 200 with non-empty preview

---

### T-005 Add `natural_description` column check + fix for LLM pipeline
**Status:** 🟡 Verify  
**Context:** V2 migration added `natural_description` and `schema_org_jsonld` columns.
`generate_pose_qa.py` populates them. But the FastAPI chat/search services depend on
these for RAG retrieval quality.

**Task:**
1. Verify: `SELECT COUNT(*) FROM poses WHERE natural_description IS NULL;`  
   If count > 0, rerun `python scripts/generate_pose_qa.py` (idempotent).
2. Verify: `SELECT COUNT(*) FROM poses WHERE schema_org_jsonld IS NULL;`
3. If both are 0, mark T-005 complete.

**Acceptance criteria:**
- 0 poses have `NULL` natural_description
- 0 poses have `NULL` schema_org_jsonld

---

## Priority 3 — Git / CI

### T-006 Create PR for `feat/frontend-vite-scaffold`
**Status:** 🔴 Open  
**Branch:** `origin/feat/frontend-vite-scaffold` (pushed, no PR yet)

**What the branch contains:**
- `frontend/` — Vite 5 + React 18 scaffold
  - `ApiDashboard.jsx` — polls 6 endpoints every 5 s, shows status/latency/preview
  - `vite.config.js` — proxy `/api/v1` → :19090, `/chat` → :5002, `/search` → :5001
  - `frontend/.gitignore` — excludes `node_modules/`, `dist/`, `.env*`
- `Dockerfile` + `docker-compose.yml` — root-level for aeogeo FastAPI services
- `app/config.py` — added `http://localhost:5173` to CORS origins
- `yoga-api/src/main/java/club/yogaman/api/config/CorsConfig.java` — Spring Boot CORS for `localhost:*`

**PR description to use:**
```
feat: Vite+React API health dashboard and CORS configuration

## Changes
- frontend/: Vite 5 + React 18 scaffold
  - ApiDashboard component polls 6 endpoints every 5 s
  - Displays HTTP status code (green/orange/red), latency (ms), JSON preview, last-check time
  - Per-row manual re-probe button; pause/resume auto-poll with countdown
  - Proxy config: /api/v1 → :19090, /chat → :5002, /search → :5001
- Dockerfile + docker-compose.yml: containerized FastAPI services
- app/config.py: localhost:5173 added to CORS allowed origins
- yoga-api/CorsConfig.java: Spring Boot WebMvcConfigurer for localhost:* origins

## How to run
cd frontend && npm install && npm run dev
# → http://localhost:5173
```

**Acceptance criteria:**
- PR opened at https://github.com/aiegoo/aeogeo/pull/new/feat/frontend-vite-scaffold
- CI passes (if configured)

---

### T-007 Delete stale remote branches (post-merge cleanup)
**Status:** 🟡 Optional cleanup  
**Branches to delete:**
```bash
git push origin --delete feat/aeo-geo-qa-enrichment
git push origin --delete chore/review-orphan-tracked-files
```
Both are confirmed ancestors of `origin/master` — safe to delete.

---

### T-008 Add GitHub Actions CI workflow
**Status:** 🟡 Medium priority  
**File to create:** `.github/workflows/ci.yml`

**Minimum workflow:**
```yaml
name: CI
on: [push, pull_request]
jobs:
  python-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install ruff
      - run: ruff check scripts/ app/

  java-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: "17", distribution: "temurin" }
      - run: cd yoga-api && mvn -q package -DskipTests

  validate-json-schemas:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install jsonschema
      - run: python -c "import json, jsonschema; schema=json.load(open('schemas/pose_eat_schema.json')); print('Schema valid')"
```

**Acceptance criteria:**
- CI runs on every push/PR
- Python linting and Java Maven build both pass

---

## Priority 4 — Matching System Features

### T-009 Implement experience level filtering in MatchService
**Status:** 🔴 Open  
**File:** `yoga-api/src/main/java/club/yogaman/api/matching/MatchService.java`

**Context:** `MatchRequest` includes `experienceLevel` (`"BEGINNER"`, `"INTERMEDIATE"`, `"ADVANCED"`)
and `availableMinutes`, but `MatchService.score()` ignores both.

**Implementation:**
```java
// In score(), after kill-switch check, before benefit scoring:
int maxDifficulty = switch (request.getExperienceLevel()) {
    case "BEGINNER"     -> 2;
    case "INTERMEDIATE" -> 4;
    case "ADVANCED"     -> 5;
    default             -> 5;
};
if (pose.getDifficultyRank() != null && pose.getDifficultyRank() > maxDifficulty) {
    return new MatchResult(pose.getPoseId(), 0.0, true,
        "Difficulty " + pose.getDifficultyRank() + " exceeds level " + request.getExperienceLevel());
}
```

Also apply an `availableMinutes` time budget: estimate pose duration from difficulty
(`difficulty * 3 minutes` as a simple heuristic) and filter out poses whose sequences
would exceed the budget.

**Acceptance criteria:**
- BEGINNER request returns only poses with `difficulty_rank ≤ 2`
- ADVANCED request receives the full 809-pose pool before benefit scoring
- `topK` still limits final results

---

### T-010 Add `topK` default and max enforcement in MatchRequest
**Status:** 🟡 Minor  
**File:** `yoga-api/src/main/java/club/yogaman/api/matching/MatchRequest.java`

**Issue:** If `topK` is omitted or set to a very large number (e.g., 10000), the endpoint
returns all 809 poses or throws an error.

**Fix:**
```java
@Min(1) @Max(100)
private int topK = 10;
```

---

### T-011 Expose `/api/v1/poses/{id}/jsonld` Schema.org endpoint
**Status:** 🔴 Open  
**Phase:** 3 (AEO/GEO)

**Goal:** Each pose should be reachable at `GET /api/v1/poses/{id}/jsonld` returning the
`schema_org_jsonld` JSONB column as `application/ld+json` — enabling AI search engines
(Perplexity, Gemini) to cite individual poses.

**Implementation steps:**
1. Add `getSchemaOrgJsonld()` to `Pose.java` (map `schema_org_jsonld` JSONB → `String`).
2. Add endpoint to `PoseController.java`:
   ```java
   @GetMapping(value = "/{id}/jsonld", produces = "application/ld+json")
   public ResponseEntity<String> getPoseJsonld(@PathVariable String id) {
       return poseRepository.findById(id)
           .map(p -> ResponseEntity.ok(p.getSchemaOrgJsonld()))
           .orElse(ResponseEntity.notFound().build());
   }
   ```
3. Verify with: `curl http://localhost:19090/api/v1/poses/mountain_pose/jsonld`

**Acceptance criteria:**
- `GET /api/v1/poses/mountain_pose/jsonld` returns 200 with `@context: "https://schema.org"` JSON-LD
- Content-Type header is `application/ld+json`
- 404 for unknown pose IDs

---

### T-012 Add `/api/v1/studios/nearby` location-based search
**Status:** ✅ Done — commit `534d3e5`  
**Phase:** 4 (Studio API)  
**Prerequisite:** T-004 (studios seeded ✅)

**Goal:** `GET /api/v1/studios/nearby?lat=37.5665&lng=126.9780&radiusKm=10` returns studios
within the radius using Haversine distance (no PostGIS extension required).

**Implementation:**
```java
// In StudioService.java:
public List<Studio> findNearby(double lat, double lng, double radiusKm) {
    return studioRepository.findAll().stream()
        .filter(s -> s.getLatitude() != null && s.getLongitude() != null)
        .filter(s -> haversine(lat, lng, s.getLatitude(), s.getLongitude()) <= radiusKm)
        .sorted(Comparator.comparingDouble(s -> haversine(lat, lng, s.getLatitude(), s.getLongitude())))
        .collect(Collectors.toList());
}

private double haversine(double lat1, double lon1, double lat2, double lon2) {
    double R = 6371.0; // km
    double dLat = Math.toRadians(lat2 - lat1);
    double dLon = Math.toRadians(lon2 - lon1);
    double a = Math.sin(dLat/2) * Math.sin(dLat/2)
             + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2))
             * Math.sin(dLon/2) * Math.sin(dLon/2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}
```

**Acceptance criteria:**
- Seoul (37.5665, 126.9780) with 15 km radius returns ≥ 3 seeded studios
- Results sorted by ascending distance
- Studios outside radius not included
- Missing lat/lng studios gracefully excluded

---

### T-013 Write integration tests for `/api/v1/match`
**Status:** 🔴 Open  
**File to create:** `yoga-api/src/test/java/club/yogaman/api/matching/MatchControllerIntegrationTest.java`

**Tests to cover:**
1. `BEGINNER + Spinal_Mobility` → top result has `score > 0.0` (after T-001 fix)
2. `healthFlags: ["herniated_disc"]` → any pose with `kill_switch: true` on that condition returns `blocked: true`
3. Empty goals → all poses return `score: 0.0` but no errors
4. Missing/null `healthFlags` → defaults to empty list, no NPE
5. `topK: 5` → exactly 5 results returned
6. `topK: 0` → 400 Bad Request

**Stack:** Spring Boot `@SpringBootTest` + `MockMvc` + `@Sql` for test data setup.

---

## Priority 5 — Frontend Features

### T-014 Add pose browser to frontend dashboard
**Status:** 🔴 Open  
**File:** `frontend/src/components/PoseBrowser.jsx` (new)

**Goal:** A paginated table of poses from `GET /api/v1/poses` with:
- Columns: pose_id, canonical_name, difficulty_rank, anatomical_focus count
- Filter by difficulty (1–5 slider)
- Click row → shows `natural_description` in a side panel

**Implementation notes:**
- Re-use Vite proxy `/api/v1` → `:19090`
- `/api/v1/poses` returns a list; paginate client-side (50 per page)
- Difficulty filter uses local state, not a server-side parameter

---

### T-015 Add match request form to frontend
**Status:** 🔴 Open  
**File:** `frontend/src/components/MatchForm.jsx` (new)

**Goal:** A form that sends `POST /api/v1/match` and displays results:
- Multi-select goals (checkboxes: `Spinal_Mobility`, `Back_Pain_Relief`, `Core_Strength`, `Hip_Flexibility`, `Balance`, `Stress_Relief`)
- Experience level radio buttons: BEGINNER / INTERMEDIATE / ADVANCED
- Available minutes slider: 15–90 min
- Health flags multi-select (optional): `herniated_disc`, `knee_injury`, `high_blood_pressure`
- Submit → shows top 10 results as cards with score bar, pose name, blocked badge

---

### T-016 Add Ollama chat test panel to frontend
**Status:** 🟡 Medium priority  
**Goal:** A minimal chat input in the dashboard that posts to `POST /chat/ask` with a yoga question
and streams back the `mistral` model's answer — confirming end-to-end Ollama integration.

**Check first:** Verify the FastAPI chat endpoint path:
```bash
curl -s http://localhost:5002/chat/health
# then check actual chat endpoint:
curl -s -X POST http://localhost:5002/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the benefits of downward facing dog?"}'
```

---

## Priority 6 — Content Pipeline (OCR → LLM)

### T-017 Phase 1 book intake — first OCR run
**Status:** 🔴 Open (see ROADMAP.md Phase 1)

**Steps:**
1. Drop book screenshots into `screenshots/`
2. Run: `python ocr_pipeline.py` — review raw output in `ocr/processed/`
3. Tune `preprocess()` in `ocr_pipeline.py` if quality is low (contrast, deskew params)
4. Run: `python scripts/adapt_content.py` — review topic tagging in `content/`
5. Run: `python scripts/integrate.py` — verify pages appear in `/yoga/search`
6. Add book chip to `/yoga/search` filter bar

**Quality bar:**
- OCR confidence ≥ 85% on representative sample of 10 pages
- Topic tagging assigns correct category to ≥ 80% of pages

---

### T-018 Build `data/json/books_manifest.json`
**Status:** 🔴 Open (ROADMAP.md Phase 3)  
**Prerequisite:** T-017

**File:** `data/json/books_manifest.json`  
**Script to create:** `scripts/build_manifest.py`  
**Schema:**
```json
[
  {
    "book_id": "generative-engine-optimization",
    "title": "Generative Engine Optimization",
    "page_count": 83,
    "words_per_page_avg": 320,
    "ocr_quality_score": 0.91,
    "processed_at": "2026-04-22T00:00:00Z",
    "content_path": "content/generative-engine-optimization/"
  }
]
```

---

## Priority 7 — Test Ollama / Chat Integration

### T-019 Verify mistral end-to-end chat response
**Status:** 🟡 Verify  
**Prerequisite:** `mistral:latest` confirmed loaded (✅ done)

**Test:**
```bash
curl -s -X POST http://localhost:5002/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What yoga poses help with lower back pain?"}' | head -40
```

**Expected:** JSON response containing an `answer` field with a yoga-specific answer
generated by the `mistral` model via Ollama at `:11434`.

**If this fails:** Check `app/config.py` for `OLLAMA_BASE_URL` and `OLLAMA_MODEL` settings;
verify `app/services/llm_service.py` sends requests to `http://localhost:11434`.

**Acceptance criteria:**
- Response contains a non-empty `answer` field
- Response time < 30 s (first call may be slow due to model loading)

---

## Priority 8 — Architecture / Brand

### T-020 Register `/api/v1/match` as a GPT Action (OpenAPI spec)
**Status:** 🔴 Planned (Phase 3–5)

**Goal:** Export the Spring Boot OpenAPI spec and register it as a ChatGPT Custom Action,
so `POST /api/v1/match` is callable directly from a GPT conversation.

**Steps:**
1. Verify SpringDoc is generating spec: `http://localhost:19090/v3/api-docs`
2. Download spec: `curl http://localhost:19090/v3/api-docs -o yoga-api-openapi.json`
3. Clean up spec — remove dev-only endpoints, add `servers: [{url: "https://yogaman.club"}]`
4. Upload to ChatGPT Builder → Actions → Import from URL or paste JSON
5. Test: "Find beginner yoga poses for back pain" in a GPT conversation

---

### T-021 Deploy `elbee.yogaman.club` subdomain
**Status:** 🔴 Planned (ROADMAP.md Phase 2)

**Steps:**
1. Add DNS CNAME: `elbee.yogaman.club` → `aiegoo.github.io`
2. Add `CNAME` file to `yoga-chatbot` repo: `elbee.yogaman.club`
3. Add `_data/brand.yml` to `yoga-chatbot`:
   ```yaml
   name: elbee
   domain: elbee.yogaman.club
   tagline: "Yoga Knowledge, Always at Hand"
   color_primary: "#6C63FF"
   ```
4. Apply brand via `_includes/elbee-brand.html`
5. Test chat + search at `https://elbee.yogaman.club`

---

## Quick Reference — Useful Commands

```bash
# DB row counts
docker exec yoga-api-postgres-1 psql -U postgres -d yogadb -c \
  "SELECT 'poses', COUNT(*) FROM poses UNION ALL SELECT 'pose_qa', COUNT(*) FROM pose_qa UNION ALL SELECT 'sessions', COUNT(*) FROM sessions UNION ALL SELECT 'studios', COUNT(*) FROM studios;"

# Check benefit tags in DB
docker exec yoga-api-postgres-1 psql -U postgres -d yogadb -c \
  "SELECT DISTINCT tag FROM pose_benefits ORDER BY tag LIMIT 30;"

# Test match endpoint
curl -s -X POST http://localhost:19090/api/v1/match \
  -H "Content-Type: application/json" \
  -d '{"healthFlags":[],"goals":["Spinal_Mobility"],"experienceLevel":"BEGINNER","availableMinutes":30,"topK":5}' | python3 -m json.tool | head -30

# Test chat
curl -s http://localhost:5002/chat/health

# Ollama models
docker exec yoga-ollama ollama list

# Frontend dev server
cd frontend && npm run dev  # → http://localhost:5173

# Python venv
source .venv/bin/activate
python scripts/db_table.py summary
```

---

## Priority 9 — AEO/GEO Content Gaps ⚠️ Critical for AI Citation

> **Background:** The current `pose_qa` rows are auto-generated template strings (e.g., *"Regular practice of X can benefit: flexibility, mobility."*) stored in a DB table that is never exposed publicly. AI engines (Perplexity, Google SGE, Gemini) cannot cite what they cannot crawl. The `content/generative-engine-optimization/` folder contains a *marketing strategy book about GEO* — not yoga content. Neither the RAG pipeline nor the Spring Boot API expose any of the 7 Schema.org types that drive AI citation.

---

### T-022 Expose `FAQPage` JSON-LD per pose endpoint
**Status:** � Partial — commit `1a15b4f`
- ✅ **Done:** Homepage `FAQPage` + `WebSite` JSON-LD injected via React `<JsonLd>` component (frontend/src/components/JsonLd.jsx + schemas/faqSchema.js); `SchemaOrgService.java` builder methods implemented in Spring Boot
- 🔴 **Still open:** Per-pose `GET /api/v1/poses/{id}/faq` endpoint (PoseQa JPA entity + PoseQaRepository + PoseController handler not yet wired)  
**Gap:** `pose_qa` rows (2,505) exist in PostgreSQL but are never exposed as crawlable structured data. AI answer engines specifically index `FAQPage` markup.  
**File:** `yoga-api/src/main/java/club/yogaman/api/pose/PoseController.java`

**Implementation:**
```java
@GetMapping(value = "/{id}/faq", produces = "application/ld+json")
public ResponseEntity<String> getPoseFaq(@PathVariable String id) {
    List<PoseQa> qaList = poseQaRepository.findByPoseId(id);
    if (qaList.isEmpty()) return ResponseEntity.notFound().build();

    List<Map<String,Object>> entities = qaList.stream().map(qa -> Map.of(
        "@type", "Question",
        "name", qa.getQuestion(),
        "acceptedAnswer", Map.of("@type", "Answer", "text", qa.getAnswer())
    )).collect(Collectors.toList());

    Map<String,Object> faqPage = Map.of(
        "@context", "https://schema.org",
        "@type", "FAQPage",
        "mainEntity", entities
    );
    return ResponseEntity.ok(new ObjectMapper().writeValueAsString(faqPage));
}
```

**Also needed:**
- Create `PoseQa.java` JPA entity mapping `pose_qa` table
- Create `PoseQaRepository.java` with `findByPoseId(String poseId)`

**Acceptance criteria:**
- `GET /api/v1/poses/mountain_pose/faq` returns `application/ld+json` with `@type: "FAQPage"`
- `mainEntity` array contains ≥ 3 Question/Answer pairs
- Google Rich Results Test validates the output: https://search.google.com/test/rich-results

---

### T-023 Upgrade `ExerciseAction` to `HowTo` with numbered steps
**Status:** 🔴 Open  
**Gap:** Current `schema_org_jsonld` stores a basic `ExerciseAction` with a single description paragraph. Google's Featured Snippet and AI engines use `HowTo` with explicit `HowToStep` objects.  
**File:** `scripts/generate_pose_qa.py` — `_build_schema_org()` function

**Upgrade the schema builder to produce:**
```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to do Mountain Pose (Tadasana)",
  "description": "Mountain Pose is a foundational standing pose...",
  "educationalLevel": "Beginner",
  "step": [
    { "@type": "HowToStep", "position": 1, "name": "Starting position",
      "text": "Stand with feet hip-width apart, arms at sides, spine tall." },
    { "@type": "HowToStep", "position": 2, "name": "Align the body",
      "text": "Root through all four corners of both feet. Engage the thighs." },
    { "@type": "HowToStep", "position": 3, "name": "Breathe and hold",
      "text": "Hold for 5–10 breaths. Keep the breath steady and the gaze soft." },
    { "@type": "HowToStep", "position": 4, "name": "Release",
      "text": "Exhale and relax the arms. Step the feet together to close." }
  ],
  "contraindications": "Avoid if you have low blood pressure or dizziness.",
  "bodyLocation": ["Legs", "Core", "Spine"]
}
```

**Step template rules:**
- Step 1: Always "start in [base position inferred from difficulty and canonical name]"
- Step 2: Body alignment cue derived from `anatomical_focus` list
- Step 3: Breathing instruction + hold duration (3 breaths for difficulty 1–2, 5 for 3–4, 8 for 5)
- Step 4: Release instruction

**Acceptance criteria:**
- Re-run `generate_pose_qa.py` with `--limit 5 --dry-run` and inspect output shows `@type: HowTo` with `step` array
- After full run, re-run with `--overwrite-jsonld` flag (add that flag) to update all 735 rows
- `/api/v1/poses/{id}/jsonld` returns the new HowTo format

---

### T-024 Add `DefinedTerm` glossary endpoint for Sanskrit terms
**Status:** 🔴 Open  
**Gap:** No Sanskrit glossary exists. AI engines cite definitions when asked "what is Trikonasana?" — but only if the page has `DefinedTerm` JSON-LD. This is the highest-frequency AEO query type for yoga content.  
**File (new):** `yoga-api/src/main/java/club/yogaman/api/pose/GlossaryController.java`

**Endpoint:** `GET /api/v1/glossary/{pose_id}` returning:
```json
{
  "@context": "https://schema.org",
  "@type": "DefinedTerm",
  "name": "Trikonasana",
  "alternateName": "Triangle Pose",
  "inDefinedTermSet": { "@type": "DefinedTermSet", "name": "Yoga Glossary — yogaman.club" },
  "description": "Triangle Pose is a standing yoga pose known for its positive effects on hip flexibility, spinal mobility, and core strength.",
  "url": "https://yogaman.club/glossary/trikonasana/"
}
```

**Acceptance criteria:**
- `GET /api/v1/glossary/trikonasana` returns `DefinedTerm` JSON-LD
- `name` is the Sanskrit canonical_name from the `poses` table
- `alternateName` is the common_name
- `description` is the `natural_description` column value

---

### T-025 Add `Article` + blog cluster table to PostgreSQL
**Status:** 🔴 Open  
**Gap:** No blog or long-form content exists. AI engines heavily weight long-form editorial articles targeting user-intent queries like "best yoga for lower back pain". These cannot be auto-generated from the current pose data structure — they need editorial intent.

**Step 1 — Create Flyway migration `V5__add_content_tables.sql`:**
```sql
CREATE TABLE IF NOT EXISTS articles (
    id              BIGSERIAL    PRIMARY KEY,
    slug            VARCHAR(255) NOT NULL UNIQUE,
    title           TEXT         NOT NULL,
    summary         TEXT,
    body_markdown   TEXT,
    schema_type     VARCHAR(50)  NOT NULL DEFAULT 'Article',
    author_name     VARCHAR(255),
    author_fyt_cert VARCHAR(100),
    published_at    TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ  DEFAULT NOW(),
    language        VARCHAR(10)  NOT NULL DEFAULT 'en'
);

CREATE TABLE IF NOT EXISTS article_poses (
    article_id  BIGINT       NOT NULL REFERENCES articles(id),
    pose_id     VARCHAR(255) NOT NULL REFERENCES poses(pose_id),
    PRIMARY KEY (article_id, pose_id)
);

CREATE INDEX IF NOT EXISTS idx_articles_slug      ON articles (slug);
CREATE INDEX IF NOT EXISTS idx_articles_schema    ON articles (schema_type);
```

**Step 2 — Seed 5 initial cluster articles** (same migration or V6):
```sql
INSERT INTO articles (slug, title, summary, schema_type, author_name, author_fyt_cert, published_at) VALUES
  ('yoga-for-lower-back-pain',
   'Best Yoga Poses for Lower Back Pain Relief',
   'A certified yoga instructor guide to the 7 most effective poses for chronic lower back pain, with contraindication safety notes.',
   'Article', 'Elbee', 'FYT100', '2026-04-23T00:00:00Z'),
  ('yoga-for-beginners',
   'Yoga for Beginners: 10 Poses to Start Your Practice',
   'A step-by-step beginner guide with breathing cues, alignment tips, and suggested sequence duration.',
   'Article', 'Elbee', 'FYT100', '2026-04-23T00:00:00Z'),
  ('yoga-for-stress-relief',
   'Yoga and Stress Relief: Science-Backed Poses and Sequences',
   'How yoga activates the parasympathetic nervous system, with 5 evidence-supported poses and a 20-minute sequence.',
   'Article', 'Elbee', 'FYT100', '2026-04-23T00:00:00Z'),
  ('yoga-hip-flexibility',
   'Yoga for Hip Flexibility: Top 8 Hip-Opening Poses',
   'Hip tightness is the #1 complaint of desk workers. These 8 poses target hip flexors, rotators, and adductors safely.',
   'Article', 'Elbee', 'FYT100', '2026-04-23T00:00:00Z'),
  ('yoga-core-strength',
   'Build Core Strength with Yoga: 6 Poses That Actually Work',
   'Unlike crunches, yoga core work builds functional stability. Includes Sanskrit names, difficulty ratings, and instructor cues.',
   'Article', 'Elbee', 'FYT100', '2026-04-23T00:00:00Z');
```

**Step 3 — Add `GET /api/v1/articles/{slug}/jsonld` endpoint** returning `Article` JSON-LD:
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Best Yoga Poses for Lower Back Pain Relief",
  "description": "A certified yoga instructor guide...",
  "author": { "@type": "Person", "name": "Elbee", "hasCredential": "FYT100" },
  "publisher": { "@type": "Organization", "name": "yogaman.club" },
  "datePublished": "2026-04-23",
  "dateModified": "2026-04-23"
}
```

**Acceptance criteria:**
- V5 migration applies cleanly with `docker compose restart yoga-api`
- 5 article rows seeded
- `GET /api/v1/articles/yoga-for-lower-back-pain/jsonld` returns `Article` JSON-LD with `author.hasCredential: "FYT100"`

---

### T-026 Add instructor / author `Person` JSON-LD for E-E-A-T signals
**Status:** 🔴 Open  
**Gap:** AI engines weight **author authority** (E-E-A-T "Expertise + Authoritativeness"). The DB has `fyt100_session_ref` and `lineage_source` on poses but no `Person` entity is ever exposed.

**Step 1 — Create `instructors` table (add to V5 migration):**
```sql
CREATE TABLE IF NOT EXISTS instructors (
    id              BIGSERIAL    PRIMARY KEY,
    slug            VARCHAR(255) NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    bio             TEXT,
    certifications  TEXT[],         -- e.g. '{"FYT100","RYT-200"}'
    lineage         VARCHAR(255),   -- e.g. 'Ashtanga / Iyengar'
    website_url     VARCHAR(500),
    social_instagram VARCHAR(255)
);

INSERT INTO instructors (slug, name, bio, certifications, lineage, website_url) VALUES
  ('elbee',
   'Elbee',
   'Certified yoga instructor with FYT100 qualification and specialisation in therapeutic yoga and E-E-A-T content creation for AI-indexed yoga knowledge bases.',
   ARRAY['FYT100', 'RYT-200'],
   'Ashtanga / Vinyasa',
   'https://elbee.yogaman.club');
```

**Step 2 — Expose `GET /api/v1/instructors/{slug}/jsonld`:**
```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Elbee",
  "description": "Certified yoga instructor...",
  "hasCredential": [
    { "@type": "EducationalOccupationalCredential", "credentialCategory": "FYT100" },
    { "@type": "EducationalOccupationalCredential", "credentialCategory": "RYT-200" }
  ],
  "knowsAbout": ["Yoga", "Ashtanga", "Vinyasa", "Therapeutic Yoga"],
  "url": "https://elbee.yogaman.club"
}
```

**Acceptance criteria:**
- `GET /api/v1/instructors/elbee/jsonld` returns `Person` JSON-LD with `hasCredential` array
- Article JSON-LD (T-025) references this instructor by URL

---

### T-027 Add `Review` / student testimonial table
**Status:** 🟡 Medium priority  
**Gap:** No student testimonials or reviews exist. `Review` Schema.org markup increases trust signals for AI citation and is a distinct GEO ranking factor.

**Migration (add to V5):**
```sql
CREATE TABLE IF NOT EXISTS reviews (
    id              BIGSERIAL    PRIMARY KEY,
    reviewer_name   VARCHAR(255),
    reviewer_level  VARCHAR(50),   -- 'BEGINNER', 'INTERMEDIATE', 'ADVANCED'
    rating          INTEGER CHECK (rating BETWEEN 1 AND 5),
    review_body     TEXT,
    pose_id         VARCHAR(255)   REFERENCES poses(pose_id),
    article_slug    VARCHAR(255)   REFERENCES articles(slug),
    language        VARCHAR(10)    NOT NULL DEFAULT 'en',
    published_at    TIMESTAMPTZ    DEFAULT NOW()
);
```

**Seed 10 reviews** targeting the 5 cluster articles and high-traffic poses.

**Expose `GET /api/v1/poses/{id}/reviews/jsonld`** returning `AggregateRating` + `Review` array:
```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "itemListElement": [
    {
      "@type": "Review",
      "author": { "@type": "Person", "name": "Sarah K." },
      "reviewRating": { "@type": "Rating", "ratingValue": 5 },
      "reviewBody": "This pose completely changed my lower back pain. I do it every morning now."
    }
  ]
}
```

**Acceptance criteria:**
- `reviews` table seeded with ≥ 10 rows
- `GET /api/v1/poses/mountain_pose/reviews/jsonld` returns at least 2 reviews

---

### T-028 Fix `pose_qa` quality — replace generic templates with intent-specific answers
**Status:** 🔴 Open — **root quality issue**  
**Gap:** All 2,505 `pose_qa` rows use the same sentence template. AI engines that evaluate answer quality will deprioritise boilerplate. Examples of the current low-quality content:

| Type | Current answer (generated) | What AI engines prefer |
|---|---|---|
| `benefits` | "Regular practice of X can benefit: flexibility, mobility." | Specific: "Mountain Pose improves posture by strengthening the erector spinae and training neutral spinal alignment — making it particularly effective for desk workers with forward head posture." |
| `how_to` | "To practise X, begin in a comfortable starting position. Move mindfully…" | Step-by-step: "1. Stand with feet hip-width apart. 2. Root through all four corners of the feet. 3. Engage the quadriceps…" |
| `contraindications` | "Do not practise X if you have herniated disc, knee injury." | Clinical: "Those with lumbar disc herniation should avoid forward-folding variants; a neutral spine modification (hands on blocks) is recommended instead." |

**Fix options (in order of quality):**

**Option A (quickest):** Add `aeo_summary` column to `pose_qa` — a 2–3 sentence expansion for each Q&A pair generated by calling the local `mistral` model via `ollama generate`. Run `scripts/expand_qa_with_llm.py` (new script).

**Option B (highest quality):** For the 20 highest-traffic poses (downward dog, warrior I/II, mountain, child's pose, tree pose, triangle, bridge, cobra, cat/cow), hand-write expert answers using the `aeo_summary`, `lineage_source`, and `instructor_cue_priority` columns as source material.

**Implementation for Option A:**
```python
# scripts/expand_qa_with_llm.py
# For each pose_qa row where answer is shorter than 200 chars:
#   POST http://localhost:11434/api/generate with prompt:
#   "You are a certified FYT100 yoga instructor. Expand this yoga FAQ answer into 2-3
#    authoritative sentences suitable for Google Featured Snippets.
#    Question: {question}
#    Short answer: {answer}
#    Expanded answer:"
# Update pose_qa.answer with the expanded text.
```

**Acceptance criteria:**
- Top 20 poses have `how_to` answers with ≥ 3 specific steps
- Top 20 poses have `benefits` answers with at least one anatomical/physiological reason
- Average answer length increases from ~80 chars to ≥ 200 chars

---

### T-029 Expose `pose_qa` as crawlable AEO page via Spring Boot
**Status:** 🔴 Open  
**Gap:** All FAQ content is in PostgreSQL but is never served as HTML or JSON-LD at a stable URL. AI engines cannot index DB content — they index HTTP endpoints.

**Required endpoints for each pose:**
```
GET /api/v1/poses/{id}/faq           → FAQPage JSON-LD   (T-022 above)
GET /api/v1/poses/{id}/jsonld        → HowTo JSON-LD     (T-011 + T-023)
GET /api/v1/poses/{id}/reviews/jsonld → Review JSON-LD   (T-027)
GET /api/v1/glossary/{id}            → DefinedTerm JSON-LD (T-024)
GET /api/v1/articles/{slug}/jsonld   → Article JSON-LD   (T-025)
GET /api/v1/instructors/{slug}/jsonld → Person JSON-LD   (T-026)
```

**Also expose a sitemap** for AI crawlers:
```
GET /api/v1/sitemap.xml  → lists all pose, article, and glossary URLs
```

**Acceptance criteria:**
- All 6 endpoint types return valid JSON-LD validated by https://validator.schema.org/
- Sitemap lists ≥ 735 pose URLs + 5 article URLs + 735 glossary URLs

---

## Task Summary Table

| ID | Priority | Status | Title |
|----|----------|--------|-------|
| T-001 | P1 | ✅ Done (`cd5e1b0`) | Fix match scoring 0.0 (goal↔tag alignment) |
| T-002 | P1 | 🟡 Low | Fix Ollama healthcheck (cosmetic) |
| T-003 | P2 | ✅ Done (`b4067c6`) | Seed sessions table (16 rows, V5) |
| T-004 | P2 | ✅ Done (`b4067c6`/`159764f`) | Seed studios (10) + instructors (10, V5/V6) |
| T-005 | P2 | 🟡 Verify | Check natural_description coverage |
| T-006 | P3 | 🔴 Open | Create PR for feat/frontend-vite-scaffold |
| T-007 | P3 | 🟡 Optional | Delete stale remote branches |
| T-008 | P3 | 🟡 Medium | Add GitHub Actions CI workflow |
| T-009 | P4 | 🔴 Open | Experience level + time budget filtering |
| T-010 | P4 | 🟡 Minor | topK default and max enforcement |
| T-011 | P4 | 🔴 Open | JSON-LD `/poses/{id}/jsonld` endpoint |
| T-012 | P4 | ✅ Done (`534d3e5`) | `/studios/nearby` Haversine search |
| T-013 | P4 | 🔴 Open | Integration tests for /api/v1/match |
| T-014 | P5 | 🔴 Open | Pose browser in frontend |
| T-015 | P5 | 🔴 Open | Match request form in frontend |
| T-016 | P5 | 🟡 Medium | Ollama chat test panel in frontend |
| T-017 | P6 | 🔴 Open | Phase 1 book intake (OCR run) |
| T-018 | P6 | 🔴 Open | Build books_manifest.json |
| T-019 | P7 | 🟡 Verify | Test mistral end-to-end chat response |
| T-020 | P8 | 🔴 Planned | Register /api/v1/match as GPT Action |
| T-021 | P8 | 🔴 Planned | Deploy elbee.yogaman.club subdomain |
| T-022 | P9 | 🟡 Partial (`1a15b4f`) | FAQPage+WebSite JSON-LD on homepage ✅; per-pose /faq endpoint 🔴 |
| T-023 | P9 | 🔴 Open | Upgrade ExerciseAction → HowTo with steps |
| T-024 | P9 | 🔴 Open | DefinedTerm glossary endpoint (Sanskrit) |
| T-025 | P9 | 🔴 Open | Article table + blog cluster seed data |
| T-026 | P9 | 🔴 Open | Instructor Person JSON-LD (E-E-A-T author) |
| T-027 | P9 | 🟡 Medium | Review / testimonial table + JSON-LD |
| T-028 | P9 | 🔴 Open | Fix pose_qa quality (expand with LLM) |
| T-029 | P9 | 🔴 Open | Sitemap + crawlable AEO URL inventory |
| T-030 | P2 | 🔴 Open | Instructor trust score daily batch recalc (Python cron) |
| T-031 | P10 | 🔴 Open | LangGraph state machine scaffold (`app/agents/graph.py`) |
| T-032 | P10 | 🔴 Open | LlamaIndex pose index — replaces keyword `rag_service.py` |
| T-033 | P10 | 🔴 Open | CrewAI crew: Analyst + Matcher + Writer agents |
| T-034 | P10 | 🔴 Open | Geofencing trigger: real-time Korean GEO copy on proximity |
| T-035 | P10 | 🔴 Open | GitHub Actions CI: full pipeline lint + smoke test |

---

## Priority 2 — Data (continued)

### T-030 Instructor trust score daily batch recalc
**Status:** 🔴 Open  
**Purpose:** V6 seeds pre-computed trust scores at a fixed point in time. As `avg_rating`, `ig_followers`, and `lineage_depth` change, the `instructor_trust_score` column goes stale. A daily cron job recalculates and updates all rows.

**Formula:**
```
trust_score =
    cert_weight                             # E-RYT-500=1.0, E-RYT-200=0.8, RYT-500=0.6, RYT-200=0.4, YACEP=0.2
  + (avg_rating / 5.0) * 0.3
  + min(lineage_depth, 4) * 0.05
  + min(log10(ig_followers) / 7.0, 0.1)
  [capped at 1.000]
```

**File to create:** `scripts/recalc_trust_scores.py`

```python
import math, psycopg2, os
from datetime import datetime, timezone

CERT_WEIGHT = {
    "E-RYT-500": 1.0, "E-RYT-200": 0.8,
    "RYT-500":   0.6, "RYT-200":   0.4,
    "YACEP":     0.2,
}

def calc_trust(cert, avg_rating, lineage_depth, ig_followers):
    score = CERT_WEIGHT.get(cert, 0.2)
    score += (avg_rating / 5.0) * 0.3
    score += min(lineage_depth, 4) * 0.05
    score += min(math.log10(max(ig_followers, 1)) / 7.0, 0.1)
    return min(round(score, 3), 1.000)

conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("SELECT instructor_id, certification, avg_rating, lineage_depth, ig_followers FROM instructors")
rows = cur.fetchall()
now = datetime.now(timezone.utc)
for row in rows:
    iid, cert, rating, depth, followers = row
    score = calc_trust(cert, float(rating or 0), int(depth or 0), int(followers or 0))
    cur.execute(
        "UPDATE instructors SET instructor_trust_score=%s, updated_at=%s WHERE instructor_id=%s",
        (score, now, iid)
    )
conn.commit()
cur.close(); conn.close()
print(f"Updated {len(rows)} instructors")
```

**Acceptance criteria:**
- Script runs without error: `DATABASE_URL=... python scripts/recalc_trust_scores.py`
- All rows in `instructors` have `updated_at = NOW()` after the run
- `instructor_trust_score` values are in range `[0.0, 1.000]`
- Script is idempotent — safe to run multiple times

---

## Priority 10 — Agentic Automation Pipeline (Issue #4)

> **Source:** [Issue #4](https://github.com/aiegoo/aeogeo/issues/4) — LangGraph + LlamaIndex + CrewAI + AutoGen  
> **Context:** Replace the current stateless keyword RAG + simple Ollama loop with a production-grade multi-agent orchestration pipeline.

### T-031 LangGraph state machine scaffold
**Status:** 🔴 Open  
**File to create:** `app/agents/graph.py`

**Purpose:** Define the full pipeline as a typed state graph. Each node is a discrete, testable function. Cycles are explicit (e.g., if kill-switch fires, short-circuit to `return_blocked`).

**State schema:**
```python
from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    # Input
    lat: float
    lng: float
    goals: List[str]
    health_flags: List[str]
    experience_level: str
    available_minutes: int
    # Intermediate
    expanded_goals: List[str]
    nearby_studios: List[dict]
    blocked_poses: List[str]
    retrieved_chunks: List[dict]
    match_results: List[dict]
    # Output
    crew_copy_ko: str
    crew_copy_en: str
    top_poses: List[dict]
    top_studio: Optional[dict]
```

**Graph edges:**
```
parse_input → parallel_fetch → score_and_rank → crew_generate → return_response
                   │
                   ├─ find_nearby_studios (calls /api/v1/studios/nearby)
                   ├─ run_kill_switch_check
                   └─ llama_index_retrieve
```

**Install:** `pip install langgraph langchain-core`

**Acceptance criteria:**
- `python -c "from app.agents.graph import build_graph; g = build_graph(); print(g)"` runs without error
- Graph can be drawn: `g.get_graph().draw_mermaid()` outputs a valid Mermaid diagram
- Smoke test input `{"lat": 37.5665, "lng": 126.9780, "goals": ["Spinal_Mobility"], "health_flags": [], "experience_level": "BEGINNER", "available_minutes": 30}` completes in < 10 s

---

### T-032 LlamaIndex pose index
**Status:** 🔴 Open  
**File to create:** `app/agents/pose_index.py`  
**Replaces:** `app/services/rag_service.py` (keyword BM25 → semantic vector retrieval)

**Purpose:** Index all `natural_description` + `schema_org_jsonld` text from the `poses` table using `nomic-embed-text` embeddings. At query time, retrieve the top-K most semantically relevant pose chunks.

**Implementation:**
```python
from llama_index.core import VectorStoreIndex, Document
from llama_index.embeddings.ollama import OllamaEmbedding

def build_pose_index(poses: list[dict]) -> VectorStoreIndex:
    embed_model = OllamaEmbedding(
        model_name="nomic-embed-text",
        base_url="http://localhost:11434",
    )
    docs = [
        Document(
            text=p["natural_description"] or p["canonical_name"],
            metadata={"pose_id": p["pose_id"], "difficulty": p["difficulty_rank"]},
        )
        for p in poses
    ]
    return VectorStoreIndex.from_documents(docs, embed_model=embed_model)
```

**Index persistence:** Save to `data/pose_index/` using `index.storage_context.persist()`. Rebuild only when pose count changes (check row count vs saved manifest).

**Install:** `pip install llama-index llama-index-embeddings-ollama`

**Acceptance criteria:**
- `python -c "from app.agents.pose_index import build_pose_index"` imports without error
- Index builds from 944 poses in < 60 s
- Query `"best poses for lower back pain"` returns ≥ 3 relevant poses with cosine similarity > 0.6

---

### T-033 CrewAI role-based crew
**Status:** 🔴 Open  
**File to create:** `app/agents/crew.py`

**Purpose:** Three specialised agents that collaborate to produce a personalised GEO marketing message. Each agent has a distinct role, goal, and backstory — mirroring the issue #4 description.

**Crew composition:**

| Agent | Role | Goal | Backstory |
|-------|------|------|-----------|
| `analyst` | GEO Context Analyst | Read user location + time of day + season + nearby landmark type | "당신은 도시 상권 전문가입니다. 위경도와 시간대를 보고 그 장소가 어떤 컨텍스트인지 파악합니다." |
| `matcher` | Yoga Pose Matcher | Select the top 3 poses and 1 nearby studio from the match results | "당신은 FYT100 자격증을 가진 요가 전문가입니다. 매칭 점수와 금기사항을 보고 최적 포즈를 선택합니다." |
| `writer` | Korean Copy Writer | Generate natural 해요체 Korean marketing copy for the selected poses and studio | "당신은 한국어 마케팅 전문가입니다. GEO 컨텍스트에 맞는 자연스러운 한국어 문구를 작성합니다." |

**Sample output** (비 오는 강남역 점심시간):
```
비 오는 강남역 점심, 뻐근한 어깨를 풀어드릴게요 🧘
오늘 추천 포즈: 고양이-소 자세 · 어깨 개방 자세 · 다운독
도보 3분: 강남 요가 센터 — 오늘 12:30 수업 잔여석 3
```

**Install:** `pip install crewai crewai-tools`

**Acceptance criteria:**
- `python -c "from app.agents.crew import build_crew; c = build_crew()"` runs without error
- Crew produces Korean copy string of ≥ 50 characters for a sample GEO context
- Copy passes a basic 해요체 check (ends sentences in `~요`, `~어요`, `~드릴게요`)

---

### T-034 Geofencing trigger: proximity-based Korean copy
**Status:** 🔴 Open  
**File to create:** `app/agents/geofence.py`

**Purpose:** Implement the Geofencing + Geo-conquesting logic from issue #4. When a user enters a defined zone (e.g., within 500 m of a partner studio, or within 1 km of a competitor), the agent pipeline fires and generates a push-notification-ready Korean message.

**Zone types:**

| Zone | Trigger | Copy template |
|------|---------|---------------|
| Partner studio (< 500 m) | User enters radius | "지금 {distance}m 앞! {studio} 오늘 {time} 수업 시작해요 🧘 지금 예약하면 {discount}% 할인" |
| Competitor vicinity (< 1 km) | User near competitor | "{competitor} 근처시군요? {our_studio}는 여기서 {distance}m — 더 저렴하고 쾌적해요 💜" |
| High-traffic zone (lunch) | Time 11:30–13:30 + CBD | "점심시간 {location} — 10분 스트레칭으로 오후를 준비하세요. 추천 포즈: {pose}" |

**Implementation:**
```python
from app.services.agent import _haversine_km

def check_geofence(user_lat: float, user_lng: float, studios: list[dict]) -> dict | None:
    """Returns the closest zone trigger within threshold, or None."""
    for studio in studios:
        dist = _haversine_km(user_lat, user_lng, studio["latitude"], studio["longitude"])
        if dist <= 0.5:
            return {"type": "partner", "studio": studio, "distance_m": int(dist * 1000)}
    return None
```

**Acceptance criteria:**
- `check_geofence(37.4979, 127.0276, studios)` returns `{"type": "partner", ...}` for Gangnam Yoga Center
- Triggered zones are passed to the CrewAI `writer` agent (T-033) to generate copy
- Returns `None` for coordinates outside all zone radii

---

### T-035 GitHub Actions CI — full pipeline
**Status:** 🔴 Open  
**File to create:** `.github/workflows/ci.yml`

**Purpose:** Automated testing on every push and PR. Covers Python linting, Java build, JSON schema validation, and a smoke test of the agent pipeline.

```yaml
name: CI

on:
  push:
    branches: [master]
  pull_request:

jobs:
  python-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install ruff
      - run: ruff check scripts/ app/

  java-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: "17", distribution: "temurin" }
      - run: cd yoga-api && ./mvnw -q package -DskipTests

  validate-schemas:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install jsonschema
      - run: |
          python -c "
          import json, jsonschema
          schema = json.load(open('schemas/pose_eat_schema.json'))
          print('Schema valid:', schema.get('@type', schema.get('title', 'OK')))
          "

  agent-smoke-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt langgraph llama-index crewai
      - run: |
          python -c "
          from app.agents.graph import build_graph
          g = build_graph()
          print('Graph nodes:', list(g.get_graph().nodes.keys()))
          "
```

**Acceptance criteria:**
- All 4 jobs pass on `master` push
- `python-lint` catches any ruff violations
- `agent-smoke-test` confirms `build_graph()` is importable without a live DB or Ollama connection (use mocks/stubs)
