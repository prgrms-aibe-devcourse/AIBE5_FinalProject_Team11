# Recording Session Checklist

> Print or keep open during recording.  
> Platform: **Descript** (recommended) or Loom

---

## Before You Start

### System prep
- [ ] Quit Slack, Teams, email — no notification popups
- [ ] Enable **Do Not Disturb** (macOS: `⌘ + F1` or Control Centre)
- [ ] Close all browser tabs except elbee.yogaman.club
- [ ] Set browser zoom to **110%**
- [ ] Hide bookmarks bar (`⌘ + Shift + B` in Chrome)
- [ ] Set terminal font to **16pt minimum**
- [ ] Use a **dark terminal theme** (One Dark / Dracula / Catppuccin)
- [ ] Set screen resolution: 1920×1080 (or record Retina → export 1080p)

### Project prep
- [ ] `elbee.yogaman.club` is live and accessible
- [ ] At least one book's OCR data is processed and integrated
- [ ] `/yoga/search` returns results for "pranayama"
- [ ] `/yoga/chat` returns a cited answer for Tadasana query
- [ ] Terminal is `cd`'d to `geo/` directory
- [ ] `page_001.jpg` is staged but NOT yet in `screenshots/` (for live demo)

### Audio check
- [ ] Do a 30-second test recording — listen back for echo/hum
- [ ] Microphone gain: voice peaks at -12 dB, not clipping
- [ ] Quiet room (close windows, turn off fan if noisy)

---

## Recording Order (Descript scenes)

| Scene | Duration | What to show |
|---|---|---|
| 1 — Hook | 30s | elbee.yogaman.club homepage |
| 2 — Problem | 30s | Physical book photo |
| 3A — OCR run | 45s | Terminal: `ocr_pipeline.py` |
| 3B — Content | 30s | Terminal: `adapt_content.py` + MD output |
| 3C — Search | 30s | Browser: `/yoga/search` |
| 3D — Chat | 30s | Browser: `/yoga/chat` |
| 4 — Architecture | 60s | Architecture diagram |
| 5 — Wrap | 45s | GitHub + live site side-by-side |

**Total:** ~5:00

---

## Descript Workflow

```
1. Download Descript (Mac): https://www.descript.com/download
2. New Project → "Record" → Screen + Mic
3. Record scenes in order above (or record all at once)
4. In transcript: delete filler words, cut long pauses
5. "Clean Up Audio" → remove background noise
6. Add title card: "elbee.yogaman.club — Built by [your name]"
7. Export → MP4, 1080p, H.264
8. Upload to YouTube (unlisted) or Loom for sharing
```

---

## Loom Workflow (faster alternative)

```
1. Install Loom: https://loom.com/download
2. Record: Screen + Camera + Mic (camera optional)
3. After recording: trim start/end, add title
4. Copy share link → paste into README / portfolio
```

---

## Post-Production Checklist

- [ ] Video length ≤ 6 minutes
- [ ] All terminal text readable (pause ≥ 2s on each command)
- [ ] No personal info visible (emails, tokens, passwords)
- [ ] Captions added (Descript auto-generates; review for accuracy)
- [ ] Thumbnail created (see [THUMBNAIL_SPEC.md](THUMBNAIL_SPEC.md))
- [ ] Exported at 1080p H.264
- [ ] Uploaded and share link works without login

---

## README Embed

After uploading, add to `geo/README.md`:

```markdown
## Demo

[![elbee demo video](video/thumbnail.png)](YOUR_VIDEO_URL)

> 5-minute walkthrough: book image → OCR → search → AI chat
```
