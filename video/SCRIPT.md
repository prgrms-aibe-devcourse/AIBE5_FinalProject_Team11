# Video Scripts — Smart Flow / elbee.yogaman.club

> Source ideation: [aeogeo#3](https://github.com/aiegoo/aeogeo/issues/3) · [yoga#115](https://github.com/aiegoo/yoga/issues/115)

---

# VIDEO 1: Marketing Short — "Stop Guessing, Start Flowing"

> **Format:** 9:16 vertical · **Length:** 60 seconds · **Platform:** YouTube Shorts / Instagram Reels / TikTok  
> **CTA:** Crowdfunding campaign — "Link in Bio"  
> **Edit in:** CapCut

## Storyboard

| Time | Visual | Dialogue / Caption |
|---|---|---|
| **0:00–0:05** | **(HOOK)** Person following an advanced YouTube yoga flow. Frustrated face. Their back ‘pops.’ They wince in pain. | **NARRATOR:** We’ve all been there. Following a random video... |
| **0:05–0:10** | Caption: “I thought this was for beginners?” Frustrated person sighs, rubs lower back. | **NARRATOR:** ...and paying for it the next day. A herniated disc isn’t “beginner-friendly.” |
| **0:10–0:20** | **(TRANSFORMATION)** Same person picks up phone. Opens **Smart Flow** app. Presses microphone icon. | **NARRATOR:** Stop guessing. Meet **Smart Flow** — the AI yoga app that actually *knows* you. |
| **0:20–0:30** | User speaks into phone in Korean: **“허리 디스크인데, 15분 요가 추천해줘.”** | **USER (snappy):** “I have a herniated disc... 15 minutes. Help.” |
| **0:30–0:40** | **(KEY VISUAL 1: AI FILTER)** Screen shows poses being crossed out with a large red ✗. Text overlay: `CONTRAINDICATIONS: BACK INJURY` | **NARRATOR:** Our AI filter — built on expert instructor knowledge — instantly removes unsafe poses. |
| **0:40–0:50** | **(KEY VISUAL 2: AEO/GEO LOGIC)** Screen shows map: blue dot (User) + green star (Studio). Text overlay: `AEO MATCH: LUMBAR THERAPY → GEO LINK: DOWNTOWN YOGA STUDIO` | **NARRATOR:** Then it matches your needs to a therapy-certified studio nearby. Online care. Offline connection. |
| **0:50–0:58** | **(RESOLUTION)** Same person calmly performing a modified pose. Face serene. Caption: **"Safe. Specific. Smart."** | **NARRATOR:** No pain. Just personalized, safe progress. |
| **0:58–1:00** | **(CALL TO ACTION)** End screen. Large text: `CROWDFUNDING NOW` Small text: `Link in Bio` | **NARRATOR:** Back our campaign. Stop guessing, start healing. |

## Production Notes (from aeogeo#3)

1. **Fast pacing** — every cut must be snappy. Pain (wince) → action (phone) → calm (flow) must be distinct and quick.
2. **Sound design** — exaggerated spine-pop for the hook; satisfying ding for the AEO match; gentle swoosh for safe flow.
3. **Color-coded overlays** — RED `#FF3B30` for danger/injuries; GREEN `#34C759` for safety/matches. People watch Shorts without sound.
4. **Bilingual captions** — Korean subtitles (primary) + English top caption (reach). Target is Korean GEO market + international investors.
5. **AEO/GEO visualization** — clean, simple map with a flashing `MATCH FOUND` banner.

---

# VIDEO 2: Employer Demo — Pipeline Walkthrough

> **Format:** 16:9 · **Length:** 5 minutes · **Audience:** Technical employer / portfolio  
> **Edit in:** Descript

## Full Narration Script

### [SCENE 1 — Hook] 0:00–0:30
*Screen: elbee.yogaman.club homepage*

> "Hi — I’m going to show you elbee: a yoga knowledge assistant I built from scratch.
> It answers questions using real yoga books — not web scraping, not Wikipedia.
> And it filters every recommendation through a contraindication engine built on expert instructor training data.
> Let me walk you through the full stack in about five minutes."

---

### [SCENE 2 — The Problem] 0:30–1:00
*Screen: photo of a printed yoga book page*

> "The problem is this: yoga apps today are just ranked video lists by difficulty.
> They have no awareness of individual physical contraindications — herniated discs, hypertension, carpal tunnel.
> Expert instructors carry this knowledge. Apps don’t.
> This project digitises that expert knowledge and puts it into an AI matching engine."

---

### [SCENE 3A — OCR Pipeline] 1:00–1:45
*Screen: Terminal in `geo/`*

> "I drop a book page screenshot here."

```bash
python3 ocr_pipeline.py --book "Light on Yoga"
```

> "The pipeline preprocesses the image with OpenCV — deskew, contrast boost —
> then Tesseract extracts the text.
> Output is structured JSON: page number, cleaned text, keyword index."

```bash
cat data/json/light-on-yoga/ocr_database.json | python3 -m json.tool | head -40
```

---

### [SCENE 3B — Content Adaptation] 1:45–2:15

```bash
python3 scripts/adapt_content.py --book "Light on Yoga"
cat content/light-on-yoga/page_042.md
```

> "The adapter tags each page: pose name, body region, benefits, and crucially — contraindications.
> This is the data layer that powers the AI filter you saw in the marketing video."

---

### [SCENE 3C — Search Demo] 2:15–2:45
*Screen: `/yoga/search`*

> "Search: 'pranayama breathing' — results with exact book, chapter, page citation.
> Sub-200-millisecond latency."

---

### [SCENE 3D — Chat Demo] 2:45–3:15
*Screen: `/yoga/chat`*

> "Chat is powered by Ollama running locally. No OpenAI dependency."

*Type:* `"허리 디스크가 있는데 타다사나를 해도 될까요?"`

> "The AI checks the contraindication index first, then returns a cited, modified pose recommendation.
> This is the AEO layer — Answer Engine Optimisation: user states their need in natural language,
> the system returns the precise expert answer."

---

### [SCENE 4 — Architecture] 3:15–4:15
*Screen: [video/ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)*

> "The architecture has three layers.
>
> **Intake:** geo repo — OCR pipeline ingests book pages, adapts to Jekyll Markdown with contraindication tags.
>
> **Agentic pipeline:** a LangGraph state machine runs three parallel branches:
> one finds nearby studios via geo-coordinates,
> one checks contraindications against the knowledge base,
> and one retrieves semantic pose chunks from a LlamaIndex vector store.
>
> **CrewAI** then takes the ranked results and runs a three-agent crew:
> Analyst reads location, time, and conditions;
> Matcher selects the top three poses and one studio;
> Writer generates Korean GEO copy for local studio marketing.
>
> This is the GEO layer — Generative Engine Optimisation:
> studios get pre-qualified leads matched to their specialty.
> Rehab yoga studios get users with disc injuries. Prenatal studios get pregnant users.
> Not mass advertising — precision matching."

---

### [SCENE 5 — Wrap] 4:15–5:00
*Screen: GitHub repo + live site side-by-side*

> "Full source on GitHub. Live at elbee.yogaman.club.
> Stack: Python, FastAPI, Jekyll, LangGraph, LlamaIndex, CrewAI, Ollama.
>
> The broader vision is a crowdfunding campaign — the marketing short positions this as
> an intelligent yoga ecosystem: safe personalized practice online,
> connected to specialist studios offline.
> AEO + GEO as twin growth engines — no paid ads.
>
> Happy to walk through any part of the architecture in detail."

*Fade to elbee logo*

---

## 🎙️ Recording Tips

- Speak at 130–150 words per minute (slower than conversation)
- Pause 0.5s after each terminal command before narrating the result
- For the Korean chat query: either speak it or paste it — note the language switch is intentional (shows bilingual market intent)
- Descript: record all scenes, then edit transcript to cut mistakes
