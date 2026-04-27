# Video Demo Production Guide — Smart Flow / elbee.yogaman.club

> Branch: `feat/video-demo-package`  
> Source ideation: [aeogeo#3](https://github.com/aiegoo/aeogeo/issues/3) · [yoga#115](https://github.com/aiegoo/yoga/issues/115)  
> Brand: **Smart Flow** powered by **elbee** · Domain: `elbee.yogaman.club`

---

## 📁 video/ Folder Index

| File | Purpose |
|---|---|
| [video/INVESTOR_PITCH_KO.md](video/INVESTOR_PITCH_KO.md) | 9-beat Korean investor pitch · DaVinci Resolve · Modoo funding |
| [video/SCRIPT.md](video/SCRIPT.md) | 60s Shorts storyboard + 5min English employer demo narration |
| [video/ARCHITECTURE_DIAGRAM.md](video/ARCHITECTURE_DIAGRAM.md) | AEO/GEO architecture diagram for Scene 4 |
| [video/RECORDING_CHECKLIST.md](video/RECORDING_CHECKLIST.md) | Pre-recording system + project checklist |
| [video/THUMBNAIL_SPEC.md](video/THUMBNAIL_SPEC.md) | 1280×720 thumbnail design spec |

---

## 🎯 Campaign Concept: "Stop Guessing, Start Flowing"

> Core message (from issue #3): *"The AI yoga app that actually knows you."*

The project has **three video deliverables** targeting different audiences:

| Video | Length | Format | Goal | Edit tool |
|---|---|---|---|---|
| **Korean Investor Pitch** | 5 min + 90s teaser | 16:9 + 9:16 vertical cut | Modoo crowdfunding / investor deck | DaVinci Resolve |
| **Marketing Short** | 60 sec | Vertical 9:16 (Shorts/Reels/TikTok) | Crowdfunding campaign CTA | CapCut |
| **Employer Demo** | 5 min | Horizontal 16:9 | Portfolio / technical showcase | Descript |

---

## ✅ Recommended Platform: **CapCut** (Marketing Short) + **Descript** (Employer Demo)

### Platform Comparison

| Criterion | CapCut | Descript | Loom | OBS |
|---|---|---|---|---|
| Vertical 9:16 templates | ✅ best | limited | ❌ | ❌ |
| Screen recording | ❌ | ✅ | ✅ | ✅ |
| AI auto-captions (Korean+English) | ✅ | ✅ | ✅ | ❌ |
| Edit video by editing text | ❌ | ✅ | ❌ | ❌ |
| Remove filler words AI | ❌ | ✅ | ❌ | ❌ |
| Sound FX library (for Shorts hook) | ✅ | limited | ❌ | ❌ |
| Color-coded text overlays | ✅ | ✅ | ❌ | ❌ |
| Free tier | ✅ unlimited | 1hr/mo | 5min clips | ✅ |
| Best for | **60-sec Marketing Short** | **5-min Tech Demo** | quick share | full control |

### Why CapCut for the Marketing Short
Issue #3 specifies fast pacing, exaggerated sound FX, and large color-coded overlays (red = danger, green = match). CapCut's mobile + desktop app is purpose-built for this:
1. Pre-built Shorts/Reels templates handle the 9:16 aspect ratio automatically
2. Auto-caption with bilingual Korean/English support (critical for GEO market)
3. Beat-sync cuts align the "AI filter" visual to a ding sound in one click
4. Free — no watermark on export at 1080p

### Why Descript for the Employer Demo
1. Record screen + voiceover once → fix mistakes by deleting words in the transcript
2. AI removes "ums" and "ahs" automatically
3. Export `.mp4` for GitHub README embed, LinkedIn, or YouTube
4. Free Hobbyist tier: 1hr transcription/month — enough for a 5-min demo

### Alternative: **Loom** (fastest path — share link in under 1 hour)
- Chrome extension or Mac app → record → share URL (no login required to view)
- Free tier: max 5-minute clips (sufficient for employer demo)
- URL: https://loom.com

---

## 🎬 Video 1: Marketing Short — "Stop Guessing, Start Flowing" (60-sec Vertical)

> Full storyboard: [video/SCRIPT.md](video/SCRIPT.md)  
> Source: [aeogeo#3](https://github.com/aiegoo/aeogeo/issues/3)  
> Platform: **CapCut** · Format: 9:16 vertical · CTA: crowdfunding link in bio

### Target Audience (from yoga#115)
1. **Injury/rehab practitioners** — disc, wrist, hypertension; afraid to follow generic videos
2. **Nomadic practitioners** — overwhelmed by thousands of YouTube options, can't find the right 20-minute session
3. **Local yoga studios** — losing members to home workout trend, need pre-qualified leads

### Scene Summary
| Time | Visual | Key Overlay |
|---|---|---|
| 0:00–0:05 | Person follows advanced YouTube flow → back pops, winces | Hook: relatable pain |
| 0:05–0:10 | Caption: "I thought this was for beginners?" | Red text: HERNIATED DISC |
| 0:10–0:20 | Same person picks up phone → opens Smart Flow app | Brand reveal |
| 0:20–0:30 | User speaks: "허리 디스크, 15분, 도와줘" | AEO: natural language input |
| 0:30–0:40 | Poses crossed out with red ✗ | **CONTRAINDICATIONS: BACK INJURY** |
| 0:40–0:50 | Map: blue dot (user) + green star (studio) | **AEO MATCH → GEO LINK** |
| 0:50–0:58 | Same person doing a modified pose, serene | Caption: "Safe. Specific. Smart." |
| 0:58–1:00 | End card | **CROWDFUNDING NOW · Link in Bio** |

---

## 🎬 Video 2: Employer Demo — Pipeline Walkthrough (5-minute Horizontal)

> Full script: [video/SCRIPT.md](video/SCRIPT.md)  
> Platform: **Descript** · Format: 16:9 · Audience: technical employer / investor

### Scene Summary
| Scene | Duration | Focus |
|---|---|---|
| 1 — Hook | 0:30 | elbee.yogaman.club overview |
| 2 — Problem | 0:30 | Knowledge locked in print; contraindication gap |
| 3A — OCR run | 0:45 | `ocr_pipeline.py` live terminal |
| 3B — Content | 0:30 | `adapt_content.py` → Jekyll MD with tags |
| 3C — Search | 0:30 | `/yoga/search` → sub-200ms results |
| 3D — Chat | 0:30 | `/yoga/chat` → cited AI answer |
| 4 — Architecture | 1:00 | LangGraph + LlamaIndex + CrewAI + AEO/GEO layer |
| 5 — Wrap | 0:45 | GitHub + live site + stack summary |

---

## 🖥️ Recording Checklist

### For both videos
- [ ] Enable **Do Not Disturb** on macOS
- [ ] Close Slack / email / all notifications
- [ ] Do a 30-second audio test before starting

### Marketing Short (CapCut — record on phone or with screen mirror)
- [ ] Film "wince" scene in portrait orientation (9:16)
- [ ] Use large, bold text overlays: RED (#FF3B30) for injuries, GREEN (#34C759) for matches
- [ ] Record app demo screen on phone (or screen-mirror iPhone to Mac via QuickTime)
- [ ] Add sound FX: spine-pop for hook, satisfying ding for AEO match, gentle swoosh for safe flow
- [ ] Add bilingual captions: Korean subtitle + English top caption
- [ ] End card: crowdfunding URL + "Link in Bio"

### Employer Demo (Descript — screen recording)
- [ ] Set terminal font size ≥ 16pt, dark theme (One Dark / Dracula)
- [ ] Hide browser bookmarks bar (`⌘ + Shift + B`)
- [ ] Set browser zoom to 110%
- [ ] Set resolution to 1920×1080
- [ ] Terminal and browser side-by-side (split screen) for pipeline scenes

---

## 📁 Assets Needed

| Asset | Used in | Status |
|---|---|---|
| "Wince" actor footage (or stock) | Marketing Short — hook | ⬜ needed |
| Phone screen recording: Smart Flow UI | Marketing Short — scenes 3–6 | ⬜ needed |
| Map UI with blue dot + green star | Marketing Short — AEO/GEO scene | ⬜ needed |
| Book screenshot (page_001.jpg) | Employer Demo — OCR scene | ⬜ needed |
| Architecture diagram PNG | Employer Demo — scene 4 | ⬜ see [video/ARCHITECTURE_DIAGRAM.md](video/ARCHITECTURE_DIAGRAM.md) |
| elbee / Smart Flow logo SVG | Both — end card | ⬜ needed |
| Thumbnail 1280×720 | Employer Demo — YouTube | ⬜ see [video/THUMBNAIL_SPEC.md](video/THUMBNAIL_SPEC.md) |

---

## 📤 Distribution

| Channel | Video | Notes |
|---|---|---|
| YouTube Shorts | Marketing Short | Upload as Shorts (< 60s, 9:16) |
| Instagram Reels | Marketing Short | Same file, add bio link |
| TikTok | Marketing Short | Add trending audio layer in app |
| LinkedIn (native video) | Employer Demo | Native upload = 3× reach vs link |
| GitHub README | Employer Demo | Embed thumbnail linking to YouTube |
| Portfolio page | Employer Demo | `<iframe>` embed |
| Crowdfunding page (Wadiz / Kickstarter) | Marketing Short | Primary hero video |

```markdown
<!-- README embed -->
[![Smart Flow Demo](video/thumbnail.png)](YOUR_VIDEO_URL)
> 5-minute walkthrough: book image → OCR → AI contraindication filter → AEO/GEO match
```

---

## 🔗 Resources

- CapCut (desktop): https://www.capcut.com/desktop
- Descript: https://www.descript.com
- Loom: https://loom.com
- OBS (full control): https://obsproject.com
- macOS built-in: `⌘ + Shift + 5` (no editing)
- Crowdfunding: [Wadiz](https://www.wadiz.kr) (Korea) · [Kickstarter](https://www.kickstarter.com)
