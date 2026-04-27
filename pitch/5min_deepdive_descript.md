# 5-Minute Deep-Dive — Descript Slide Deck

> **Format:** 1920×1080 · 30 fps · 5:00 · 16:9
> **Audience:** technical investors, hiring managers, partner CTOs.
> **Source narration:** [../video/SCRIPT.md](../video/SCRIPT.md) — VIDEO 2.
> **Architecture reference:** [../video/ARCHITECTURE_DIAGRAM.md](../video/ARCHITECTURE_DIAGRAM.md).

Five scenes. Each maps to one Descript scene. Use the same Descript project
as the teaser if you want shared assets/voice.

---

## SCENE 1 — Hook & framing · 0:00 – 0:30

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

## SCENE 2 — The problem · 0:30 – 1:00

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

### 3A · OCR pipeline · 1:00 – 1:45

- **Asset:** terminal screen recording running `python3 ocr_pipeline.py --book "Light on Yoga"` then `cat data/json/light-on-yoga/ocr_database.json | python3 -m json.tool | head -40`
- **VO:** *(SCRIPT.md SCENE 3A)*
- **Lower-third:** `intake · OCR + structured JSON`
- **Descript prompt:**
  > "Speed-ramp the terminal scrollback to 1.5× during the JSON dump.
  > Highlight the keys 'page_number', 'text', 'keywords' with a yellow
  > underline as the VO names them."

### 3B · Content adaptation · 1:45 – 2:15

- **Asset:** terminal recording of `python3 scripts/adapt_content.py --book "Light on Yoga"` and `cat content/light-on-yoga/page_042.md`
- **VO:** *(SCRIPT.md SCENE 3B)*
- **Lower-third:** `adaptation · contraindication tagging`
- **Descript prompt:**
  > "When the markdown front-matter appears, draw a soft red box around
  > the `contraindications:` field for 2.5 seconds. No transition between
  > 3A and 3B — straight cut."

### 3C · Search demo · 2:15 – 2:45

- **Asset:** browser screen-cap of `/yoga/search` typing `pranayama breathing`
- **VO:** *(SCRIPT.md SCENE 3C)*
- **Lower-third:** `retrieval · sub-200 ms · cited`
- **Descript prompt:**
  > "After the search returns, freeze on the first result and animate a
  > callout arrow pointing at the page-citation chip ('p. 142'). Hold
  > 2 seconds, then continue."

### 3D · Chat demo · 2:45 – 3:15

- **Asset:** browser screen-cap of `/yoga/chat` typing `허리 디스크가 있는데 타다사나를 해도 될까요?`
- **Optional inset:** thumbnail of `assets/teaser/shot_05_breakdown.png` to remind viewer of the score
- **VO:** *(SCRIPT.md SCENE 3D)*
- **Lower-third:** `AEO · natural-language → cited expert answer`
- **Descript prompt:**
  > "While the chat streams its reply, dim the right 30% of the canvas
  > and pop a thumbnail of `assets/teaser/shot_05_breakdown.png` in the
  > bottom-right for 4 seconds (label: 'same engine, different surface')."

---

## SCENE 4 — Architecture · 3:15 – 4:15

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

## SCENE 5 — Wrap & ask · 4:15 – 5:00

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
