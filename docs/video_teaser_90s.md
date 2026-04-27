# aeogeo Teaser — 90 Seconds

**Cut from:** [docs/video_script.md](aiegoo/aeogeo/docs/video_script.md) (5-min master)
**Aspect ratios:** 16:9 1920×1080 (investor email, Vimeo) · 9:16 1080×1920 (LinkedIn, Naver Blog, KakaoStory)
**Total runtime:** 0:00–1:30 (90s)
**Beats reused:** 0 (cold open) · 3 (HEADLINE match demo) · 7 (AEO JSON-LD) · 9 (ask)
**Cuts dropped from master:** 1 (problem) · 2 (thesis) · 4 (RAG cite detail) · 5 (safety) · 6 (architecture) · 8 (moat)
**Reasoning:** Teaser must answer in 90s — *what does it do, why is it different, what do you want?* Everything else is the deep-dive's job.

---

## Shot list (16:9 master)

| # | TC in | TC out | Dur | Visual | KO VO | EN subtitle |
|---|---|---|---|---|---|---|
| 1 | 0:00 | 0:04 | 4s | Black. Korean text fades in: *"허리가 아픈데 강남에서 추천해줘"* | (silence — let viewer read) | *"My back hurts. Recommend a place in Gangnam."* |
| 2 | 0:04 | 0:08 | 4s | Same line stays. Cursor blinks at end. Quiet ambient sound. | 한 줄. 우리 사용자가 묻는 방식입니다. | One line. This is how our users ask. |
| 3 | 0:08 | 0:18 | 10s | **Cut to** Streamlit `demo_match_score.py`. Free-text box on screen. The query auto-types itself, char by char. | 대답은 광고가 아니라, **점수**입니다. | The answer isn't an ad. It's a score. |
| 4 | 0:18 | 0:30 | 12s | Map of Seoul renders. 8 studio pins drop in. Ranked table animates. **Itaewon Therapy Yoga · 80.3%** highlighted with a green ring. | 8개 검증 스튜디오, 5km 안. 1위는 가장 가까운 곳이 아니라 — | Eight verified studios within 5km. The winner isn't the closest — |
| 5 | 0:30 | 0:42 | 12s | Expander opens. Three bars animate: **Need fit 80% · Proximity 37% · Specialization 97%**. Cursor highlights the certification line: *"Physical Therapy Specialist."* | — *물리치료 자격*을 가진 강사가 있는 곳입니다. | — it's the one with a physical-therapy-certified instructor. |
| 6 | 0:42 | 0:50 | 8s | Caption full-screen, large typography over a soft-blurred map: **"가까운 곳보다, 맞는 곳."** | (beat — let it land) | "Not the closest. The right one." |
| 7 | 0:50 | 1:02 | 12s | **Cut to** browser DevTools side-by-side with mobile mockup. Highlight `<script type="application/ld+json">` block. Three nodes pulse in sequence: `SportsActivityLocation`, `FAQPage`, `HowTo`. | 모든 추천은 Google AI Overviews와 Naver Cue가 읽을 수 있는 형식으로도 발행됩니다. | Every recommendation is also published in a format Google AI Overviews and Naver Cue can read. |
| 8 | 1:02 | 1:10 | 8s | Lower-third bar slides in: **`AEO · LangGraph · CrewAI · RAG · PostGIS`**. DevTools fades behind it. | **AEO** — 다음 세대의 SEO입니다. | AEO — the next generation of SEO. |
| 9 | 1:10 | 1:22 | 12s | Founder portrait or B-roll of yoga studio. Lower-third: *"Founder · 20 years yoga instructor · Built the data, built the engine."* | 20년의 강사 데이터가 연료, AI가 엔진입니다. 우리는 둘을 모두 가지고 있습니다. | Twenty years of instructor data is the fuel. AI is the engine. We own both. |
| 10 | 1:22 | 1:30 | 8s | End card. Logo · `aeogeo.app` · single CTA: **"투자 미팅 요청 →"** / **"Request investor meeting →"** | (logo sting) | — |

**Total: 90s exactly.**

---

## 9:16 vertical re-cut (same 90s, framing changes)

| Shot | Vertical-specific change |
|---|---|
| 1–2 | Korean text centered, increase font 30% (legible on phone) |
| 3 | Crop Streamlit to free-text box + ranked-list column only (drop the map) |
| 4 | Map gets its own full-screen vertical shot (8 pins on a tight Seoul crop) |
| 5 | Three bars stack vertically, full-width — easier to read on phone |
| 6 | Caption stays the same, larger |
| 7 | Mobile mockup goes left-portrait, DevTools stacks below in landscape thumbnail |
| 8 | Lower-third becomes a centered chip stack |
| 9 | Founder shot in 9:16 native (portrait orientation) |
| 10 | End card unchanged |

---

## Asset checklist

- [ ] **Shot 3–6:** OBS recording of `streamlit run scripts/demo_match_score.py` — type the KO query in real time. Save raw at `assets/teaser/match_demo_4k.mov`.
- [ ] **Shot 7:** Browser session — render the JSON-LD into an HTML page and open DevTools. Source: `python3 scripts/jsonld_aeo.py --query "허리가 아픈데 강남에서 추천해줘" --script-tag > assets/teaser/jsonld.html`.
- [ ] **Shot 9:** Founder talking-head or yoga studio B-roll (TBD — provide footage).
- [ ] Voiceover: KO single take per shot, 48kHz WAV, target -16 LUFS.
- [ ] EN subtitles: SRT file, burn-in for vertical, soft-sub for horizontal.
- [ ] Music: ambient/soft (Epidemic Sound license — pick something with a quiet 0:50 → 1:02 swell).
- [ ] Color: warm grade for studio shots, cool grade for terminal/DevTools — keeps the *human vs. machine* tension visible.

## Pacing rule

Every shot ≤ 12s. The audience commits in the first 8s — that's why beats 1–2 are wordless. The headline ("가까운 곳보다, 맞는 곳") lands at 0:42, the differentiator (AEO) at 1:00, the ask at 1:22. If any shot runs long in edit, cut from shots 4 or 7 first — never from shot 6.

## Distribution-ready exports

| Channel | Format | Source cut |
|---|---|---|
| Investor email + Vimeo (password) | 1920×1080 H.264, 12 Mbps, 30fps, MP4 | 16:9 master |
| LinkedIn (KO + EN) | 1080×1920 H.264, 8 Mbps, 30fps, MP4 + burned subs | 9:16 vertical |
| Naver Blog / KakaoStory | 1080×1920 H.264, 6 Mbps, 30fps, MP4 + KO burned subs only | 9:16 vertical |
| YouTube Shorts (unlisted) | 1080×1920 H.264, 8 Mbps, 30fps, MP4 + auto-CC | 9:16 vertical |
| Twitter/X | 1280×720 H.264, 5 Mbps, 30fps, MP4 + burned subs | 16:9 downscale |
