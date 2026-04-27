# aeogeo Investor Pitch — Video Script (Korean)

**Audience:** Modoo investors + crowdfunding manager  
**Cuts:** 90s teaser + 5min deep-dive (teaser = beats 0, 3, 5, 9 trimmed)  
**Language:** Korean voiceover primary · English subtitles · all on-screen JSON in source form  
**Tone:** Founder-led, calm, specific. Numbers over adjectives.  
**Edit tool:** DaVinci Resolve · 23.976fps · KO burned captions + EN soft-sub  

> See also: [VIDEO_DEMO_GUIDE.md](../VIDEO_DEMO_GUIDE.md) · [video/SCRIPT.md](SCRIPT.md) (English employer demo)  
> Demo assets: `scripts/demo_match_score.py` · `scripts/demo_safety_filter.py` · `scripts/orchestrator.py` · `scripts/jsonld_aeo.py`
**Working title:** *"한국 요가 매칭은 왜 어려운가 — 그리고 우리가 푸는 방법"*

---

## Beat 0 · Cold open (0:00–0:08) — 8s

**Visual:** Black screen → single line of Korean text fades in:
> *"허리가 아픈데 강남에서 추천해줘"*

**VO (KO):**
> 한 줄. 이게 우리 사용자가 묻는 방식입니다.

**Subtitle (EN):** *"One line. This is how our users ask."*

---

## Beat 1 · The problem (0:08–0:38) — 30s

**Visual:** Split screen.
- Left: Naver/Google search results for "강남 요가 추천" — generic listicles, sponsored posts.
- Right: A user holding their lower back, scrolling endlessly.

**VO (KO):**
> 통증, 임신, 부상 — 한국 요가 회원의 실제 고민은 검색 엔진이 답하지 못합니다.
> 스튜디오는 광고로 노출되고, 강사 자격은 어디에도 없습니다.
> **20년간 요가 강사로 활동한 창업자가 본 진짜 문제**는 이겁니다 —
> *수련자와 스튜디오를 연결하는 신뢰 가능한 데이터 레이어가 없다는 것.*

**Lower-third:** "Founder · 20 years yoga instructor"

---

## Beat 2 · The thesis (0:38–0:58) — 20s

**Visual:** Whiteboard-style animation. Two boxes.
- Box 1: **강사 지식 = 연료 (Fuel)**
- Box 2: **AI = 엔진 (Engine)**
- Arrow connects them → output: **"Right studio, right pose, right time."**

**VO (KO):**
> 강사의 20년 지식이 연료, AI는 엔진입니다.
> 우리는 둘을 연결합니다.

---

## Beat 3 · HEADLINE DEMO — Studio Match (0:58–1:58) — 60s

**Visual:** Screen recording of `scripts/demo_match_score.py` (Streamlit).

| Sec | Action |
|---|---|
| 0:58 | Free-text box: type *"허리가 아픈데 강남에서 추천해줘"* slowly |
| 1:08 | Map of Seoul renders with 8 verified studios as pins |
| 1:14 | Ranked table animates in. **Itaewon Therapy Yoga · 80.3%** highlighted |
| 1:22 | Expander opens: **40% Need fit · 30% Proximity · 30% Specialization** breakdown |
| 1:35 | Cursor hovers proximity bar (37%) and specialization bar (97%) — show trade-off |
| 1:45 | Caption: *"가까운 곳보다, 맞는 곳."* (Not the closest. The right one.) |

**VO (KO):**
> 우리의 매칭 점수는 세 가지를 봅니다 — 필요 적합도, 거리, 전문성.
> 사용자가 가장 가까운 강남 스튜디오 대신 5km 떨어진 이태원 치료 요가를 추천받는 이유는,
> 거기에 *물리치료 자격* 강사가 있기 때문입니다.
> **Modoo 명세 그대로, 4-3-3 가중치.**

---

## Beat 4 · Why this match — RAG cite (1:58–2:33) — 35s

**Visual:** Terminal recording of `scripts/orchestrator.py --query ... --crew`. Pretty-print the JSON output.
Highlight in sequence:
1. `"need": "Lower back pain"` (NLU node)
2. `"safety": ["Herniated disc / Lower back: Substitute supported bridge..."]` (Safety node)
3. `"crew.evidence": [{"page": ..., "snippet": ...}]` (Researcher role pulling from RAG)
4. `"trace"` array animates — 5 nodes light up: NLU → Safety → RAG → Match → Generate

**VO (KO):**
> 추천에는 *근거*가 따라옵니다.
> RAG가 강사 매뉴얼에서 인용을 가져오고, CrewAI의 Researcher 에이전트가 가장 강한 증거 3개를 골라냅니다.
> **답이 아니라, 인용된 답입니다.**

---

## Beat 5 · Safety guardrail (2:33–3:03) — 30s

**Visual:** Screen recording of `scripts/demo_safety_filter.py`.
- Type *"무릎이 좋지 않아요"* in the search box
- Pose grid: 1,471 poses, ~40 grayed out (forbidden)
- Toggle "Hide unsafe" — grid filters live
- Caption: *"강사의 20년 룰북, 코드로."*

**VO (KO):**
> 안전은 옵션이 아닙니다. 7가지 부상·임신 조건에 대해, 자유 입력으로도 동의어와 오타까지 잡아냅니다.
> 1,471개 포즈 중 위험한 동작은 자동으로 흐려집니다.

---

## Beat 6 · The architecture (3:03–3:43) — 40s

**Visual:** Animated architecture diagram. Boxes light up as VO mentions each.

```
        ┌────────────────┐
        │  Flutter App   │  ← user
        └────────┬───────┘
                 │ HTTPS
        ┌────────▼───────┐
        │  FastAPI       │
        └────────┬───────┘
                 │
   ┌─────────────┼──────────────┐
   ▼             ▼              ▼
LangGraph    LlamaIndex      CrewAI
 (state)      (RAG)        (3 roles)
   │             │              │
   ▼             ▼              ▼
Postgres     Pinecone     Gemini 1.5 Pro
+PostGIS    (BAAI/bge-m3)  HyperCLOVA X
```

**VO (KO):**
> Flutter, FastAPI, **LangGraph가 상태를, LlamaIndex가 데이터를, CrewAI가 역할을** 맡습니다.
> 벡터는 Pinecone, 지리는 PostGIS, 한국어는 HyperCLOVA X, 추론은 Gemini.
> *왜 LangChain이 아니라 LangGraph인가* — 실제 흐름은 직선이 아니라 조건부 루프입니다. (issue #4)

**Lower-third:** "LangGraph · LlamaIndex · CrewAI · Pinecone · PostGIS · HyperCLOVA X"

---

## Beat 7 · AEO proof — JSON-LD on screen (3:43–4:13) — 30s

**Visual:** Side-by-side.
- Left: Mobile mockup of the studio card (the user-facing answer).
- Right: Browser DevTools showing the `<script type="application/ld+json">` block emitted by `scripts/jsonld_aeo.py`.
- Highlight `@type: SportsActivityLocation`, `FAQPage`, `HowTo` nodes one by one.
- Bottom caption: *"Google AI Overviews · Perplexity · Naver Cue가 읽을 수 있는 형식."*

**VO (KO):**
> AEO — Answer Engine Optimization.
> 모든 추천은 schema.org JSON-LD로도 발행됩니다.
> 사용자에게 보여주는 답이 곧 검색 엔진이 *인용*할 수 있는 답이 됩니다.
> **이게 다음 세대의 SEO입니다.**

---

## Beat 8 · The moat (4:13–4:33) — 20s

**Visual:** Three stacked cards animate in.
1. **20년간의 강사 데이터** — 1,471 포즈, 7가지 부상 룰, 검증된 스튜디오 시드
2. **AI 오케스트레이션** — LangGraph + RAG + CrewAI = 답이 아니라 *추론 과정*을 소유
3. **AEO 우위** — JSON-LD를 처음부터 발행하는 한국 첫 요가 플랫폼

**VO (KO):**
> 우리 해자(moat)는 세 가지입니다 — *데이터, 오케스트레이션, AEO*.

---

## Beat 9 · Roadmap & ask (4:33–5:00) — 27s

**Visual:** Three-column timeline.

| Round 1 (now) | Round 2 (6mo) | Round 3 (12mo) |
|---|---|---|
| Prototype + 50 verified studios | Flutter MVP + payment | Studio dashboard (B2B SaaS) |

**VO (KO):**
> 1라운드는 프로토타입과 50개 검증 스튜디오.
> 2라운드는 Flutter MVP와 결제.
> 3라운드는 스튜디오 대시보드 — B2B SaaS로 확장합니다.
>
> *"수련자와 강사를 다시 연결하는 가장 빠른 길은, 우리가 이미 걸어본 길입니다."*

**End card:** Logo · `aeogeo.app` · contact

---

## Production checklist

- [ ] OBS Studio: 1920×1080 @ 30fps, capture each demo separately
  - [ ] `streamlit run scripts/demo_match_score.py` (Beat 3)
  - [ ] `python3 scripts/orchestrator.py --query "..." --crew | jq` in iTerm2 with large font (Beat 4)
  - [ ] `streamlit run scripts/demo_safety_filter.py` (Beat 5)
  - [ ] `python3 scripts/jsonld_aeo.py --query "..." --script-tag` + browser DevTools view (Beat 7)
- [ ] Architecture diagram: build in Excalidraw or draw.io, export as MP4 with sequential reveal
- [ ] Voiceover: KO primary, record in single take per beat for consistent pacing
- [ ] DaVinci Resolve project: 23.976fps timeline, captions burned in for KO, soft-sub track for EN
- [ ] Lower-thirds: `LangGraph` `LlamaIndex` `CrewAI` `RAG` `AEO` `GEO` `PostGIS` `HyperCLOVA X`
- [ ] Master export: 1080p H.264 (investor Vimeo)
- [ ] Vertical cut: 9:16 1080×1920, beats 0+3+7+9 only, ~60s (LinkedIn, Naver Blog)

## Beat-to-asset map

| Beat | Asset | Source |
|---|---|---|
| 3 | Match Score recording | [scripts/demo_match_score.py](aiegoo/aeogeo/scripts/demo_match_score.py) |
| 4 | Orchestrator JSON | [scripts/orchestrator.py](aiegoo/aeogeo/scripts/orchestrator.py) `--crew` |
| 5 | Safety filter recording | [scripts/demo_safety_filter.py](aiegoo/aeogeo/scripts/demo_safety_filter.py) |
| 6 | Architecture animation | new — Excalidraw |
| 7 | JSON-LD DevTools | [scripts/jsonld_aeo.py](aiegoo/aeogeo/scripts/jsonld_aeo.py) `--script-tag` |
