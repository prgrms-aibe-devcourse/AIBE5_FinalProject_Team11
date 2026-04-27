# 5-Minute Deep-Dive — Descript Slide Deck

> **Format:** 1920×1080 · 30 fps · 5:45 · 16:9
> **Audience:** technical investors, hiring managers, partner CTOs.
> **Source narration:** [../video/SCRIPT.md](../video/SCRIPT.md) — VIDEO 2 + new founder cold open.
> **Architecture reference:** [../video/ARCHITECTURE_DIAGRAM.md](../video/ARCHITECTURE_DIAGRAM.md).

Six scenes. Each maps to one Descript scene. Use the same Descript project
as the teaser if you want shared assets/voice.

> **Time-code convention:** the **scene heading** uses absolute master
> timecodes (e.g. `0:45 – 1:15`). All inline cues inside a scene
> (e.g. *"Cutaway at 0:18"*) are **scene-relative seconds from the scene
> start** — Descript shows this same value in the per-scene timeline.

---

## SCENE 0 — Founder cold open · 0:00 – 0:45

Emotional opener that establishes **why this service must exist** before any
tech is shown. Founder voice, in Korean. Visuals stay quiet so the words land.
**Thesis:** breath → daily-life change → "proper start is hard" → fear of
re-injury → expert KB ported into AI → AEO safety filter → GEO studio match
→ "healing journey, not pain."

- **Asset:** B-roll montage — stitch four 8–10 s clips:
  1. close-up of someone breathing slowly (chest rise-fall)
  2. desk worker rolling shoulders, slight wince
  3. hand resting on lower back, soft wince
  4. slow exhale → calm gaze toward window light
  *(no original B-roll? Descript Stock → "breath calm", "back pain office", "yoga sunrise". Lower contrast −5, desaturate to 80%.)*
- **VO (KO):** the block tagged `# SCENE 10B (Founder Cold Open)` in [descript_script_ko.txt](descript_script_ko.txt) — verbatim.
- **On-screen text (centered Korean, fade in/out per beat):**
  - 0:08 — "'제대로 된 시작'이 생각보다 어렵습니다." (4 s)
  - 0:22 — "운동은 선택이 아닌 생존의 문제입니다." (4 s)
  - 0:34 — "기술이 당신의 몸을 이해할 때, 운동은 치유가 됩니다." (5 s)
- **Transition in:** Slow fade from black (1.0 s)
- **Lower-third (0:42 – 0:45):** `창업자 · 20년 요가 강사 · elbee.yogaman.club`
- **Audio bed:** soft pad (Descript stock → "Ambient Calm"), −32 dB under VO. No drums.
- **Descript prompt (Underlord):**
  > "Compose a 45-second emotional cold open. Place the four B-roll clips
  > in the listed order, each with a slow 102%→106% Ken Burns push-in.
  > Cross-dissolve (0.6 s) between clips. Burn the three Korean text
  > overlays at 0:08, 0:22, 0:34 with a 0.4 s fade in/out. Lay the VO
  > from `descript_script_ko.txt` SCENE 10B at −16 LUFS over the whole
  > scene. Music bed 'Ambient Calm' at −32 dB, duck under VO. End on a
  > gentle exhale beat (no swell) and dissolve to SCENE 1."

---

## SCENE 1 — Hook & framing · 0:45 – 1:15

- **Asset:** screen recording of `https://elbee.yogaman.club` homepage (record fresh in Descript → Screen)
- **Cutaway at 0:18 – 0:25:** drop in `assets/teaser/match_demo.mp4` (first 7 s) as a quick visual proof
- **VO:** *(from SCRIPT.md SCENE 1 — verbatim)*
- **On-screen text (lower-third 0:00 – 0:05):** `aeogeo · yoga knowledge engine`
- **Transition in:** Fade from black (0.5 s)
- **Descript prompt (Underlord):**
  > "Compose a 30-second hook. Open with the elbee.yogaman.club home page,
  > record a slow scroll for 18 seconds. At 0:18 cut to
  > `assets/teaser/match_demo.mp4` (first 7 seconds, ranked-list reveal),
  > then return to the homepage logo for the final 5 seconds. Sub-bass
  > sting on the cut-back. Burn the lower-third 'aeogeo · yoga knowledge
  > engine' for the first 5 seconds."

---

## SCENE 2 — The problem · 1:15 – 1:45

- **Asset:** photo of a printed yoga book page (use any from `data/raw/` or shoot a fresh phone photo and drop in)
- **Optional cutaway at 0:48:** `shot_03_typing.png` (the 'I have a herniated disc' query)
- **VO:** *(from SCRIPT.md SCENE 2 — verbatim)*
- **On-screen text (centered, 0:42 – 0:50):**
  ```
  Apps rank by difficulty.
  Experts know contraindications.
  ```
- **Transition in:** Cross-dissolve (0.4 s)
- **Lower-third (0:30 – 0:34):** `the gap — generic apps vs. expert knowledge`
- **Descript prompt (Underlord):**
  > "Hold a photo of a printed yoga book page for 30 seconds with a slow
  > 105% Ken Burns push-in. At 0:42, fade in the two-line caption
  > 'Apps rank by difficulty. / Experts know contraindications.' for
  > 8 seconds. At 0:48, briefly cut away (1.5 s) to
  > `assets/teaser/shot_03_typing.png` then return."

---

## SCENE 3 — Pipeline walkthrough · 1:00 – 3:15

This scene is **four sub-clips back-to-back** — record each terminal/browser
clip once with Descript Screen, then arrange. Total 2:15.

### 3A · OCR pipeline · 1:45 – 2:30

- **Asset:** terminal screen recording running `python3 ocr_pipeline.py --book "Light on Yoga"` then `cat data/json/light-on-yoga/ocr_database.json | python3 -m json.tool | head -40`
- **VO:** *(SCRIPT.md SCENE 3A)*
- **Lower-third:** `intake · OCR + structured JSON`
- **Descript prompt:**
  > "Speed-ramp the terminal scrollback to 1.5× during the JSON dump.
  > Highlight the keys 'page_number', 'text', 'keywords' with a yellow
  > underline as the VO names them."

### 3B · Content adaptation · 2:30 – 3:00

- **Asset:** terminal recording of `python3 scripts/adapt_content.py --book "Light on Yoga"` and `cat content/light-on-yoga/page_042.md`
- **VO:** *(SCRIPT.md SCENE 3B)*
- **Lower-third:** `adaptation · contraindication tagging`
- **Descript prompt:**
  > "When the markdown front-matter appears, draw a soft red box around
  > the `contraindications:` field for 2.5 seconds. No transition between
  > 3A and 3B — straight cut."

### 3C · Search demo · 3:00 – 3:30

- **Asset:** browser screen-cap of `/yoga/search` typing `pranayama breathing`
- **VO:** *(SCRIPT.md SCENE 3C)*
- **Lower-third:** `retrieval · sub-200 ms · cited`
- **Descript prompt:**
  > "After the search returns, freeze on the first result and animate a
  > callout arrow pointing at the page-citation chip ('p. 142'). Hold
  > 2 seconds, then continue."

### 3D · Chat demo · 3:30 – 4:00

- **Asset:** browser screen-cap of `/yoga/chat` typing `허리 디스크가 있는데 타다사나를 해도 될까요?`
- **Optional inset:** thumbnail of `assets/teaser/shot_05_breakdown.png` to remind viewer of the score
- **VO:** *(SCRIPT.md SCENE 3D)*
- **Lower-third:** `AEO · natural-language → cited expert answer`
- **Descript prompt:**
  > "While the chat streams its reply, dim the right 30% of the canvas
  > and pop a thumbnail of `assets/teaser/shot_05_breakdown.png` in the
  > bottom-right for 4 seconds (label: 'same engine, different surface')."

---

## SCENE 4 — Architecture · 4:00 – 5:00

- **Asset:** render `../video/ARCHITECTURE_DIAGRAM.md` to PNG (Mermaid → PNG via VS Code Mermaid preview, or use Excalidraw export). Save as `assets/teaser/architecture.png`.
- **Optional cutaway at 3:50:** `assets/teaser/shot_07_jsonld.png`
- **VO:** *(SCRIPT.md SCENE 4 — verbatim, both the LangGraph and CrewAI paragraphs)*
- **On-screen text:** highlight three layers in turn — `Intake` (3:20), `Agentic pipeline` (3:32), `CrewAI crew` (3:48)
- **Lower-third:** rotate — `LangGraph state machine` → `LlamaIndex vector store` → `CrewAI three-agent crew`
- **Descript prompt (Underlord):**
  > "Display the architecture PNG full-frame for 60 seconds. Animate a
  > soft yellow spotlight that travels through the three layers in sync
  > with the VO: Intake at 3:20-3:30, Agentic pipeline at 3:32-3:46,
  > CrewAI crew at 3:48-4:05. At 3:50 quickly cut away to
  > `assets/teaser/shot_07_jsonld.png` for 5 seconds (lower-third:
  > 'AEO output · schema.org/FAQPage'), then back to the diagram."

---

## SCENE 5 — Wrap & ask · 5:00 – 5:45

- **Asset:** split-screen — left: GitHub repo `https://github.com/aiegoo/aeogeo`, right: live site `https://elbee.yogaman.club`
- **End frame:** `assets/teaser/end_card.svg` (last 5 seconds)
- **VO:** *(SCRIPT.md SCENE 5 — verbatim)*
- **On-screen text (4:45 – 5:00):**
  ```
  Stack: Python · FastAPI · Jekyll
  LangGraph · LlamaIndex · CrewAI · Ollama
  AEO + GEO — twin growth engines
  ```
- **Lower-third (4:15 – 4:25):** `aeogeo · github.com/aiegoo · elbee.yogaman.club`
- **Transition out:** Cross-dissolve to `end_card.svg` (0.6 s)
- **Descript prompt (Underlord):**
  > "Render a 50/50 split-screen for 40 seconds: left half shows the
  > GitHub repo home with a slow scroll through the README, right half
  > shows the live elbee.yogaman.club homepage. At 4:45 fade in the
  > three-line stack caption above. At 4:55 cross-dissolve to
  > `assets/teaser/end_card.svg` and hold for 5 seconds. Soft logo bell
  > sting on the dissolve."

---

## Recording checklist (do before importing)

- [ ] Record terminal clips (3A, 3B) at 1280×800 with a large monospace font (≥18 pt) and dark theme.
- [ ] Record browser clips (3C, 3D) zoomed to 110% so callouts read on Vimeo at 720p.
- [ ] Render `architecture.png` from [`../video/ARCHITECTURE_DIAGRAM.md`](../video/ARCHITECTURE_DIAGRAM.md) at 2560×1440 (so spotlight zooms stay sharp).
- [ ] Record VO with the same mic/preset used for the teaser so voice matches across both videos.
