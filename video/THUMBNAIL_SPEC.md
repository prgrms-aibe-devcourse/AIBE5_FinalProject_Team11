# Thumbnail Specification — elbee Demo Video

> Create this in Canva, Figma, or Photoshop.  
> Dimensions: **1280 × 720 px** (YouTube/LinkedIn standard)

---

## Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Background: dark gradient  #1a1a2e → #16213e                   │
│                                                                  │
│  LEFT half (40%):                                               │
│    ┌─────────────────┐                                          │
│    │  [Screenshot:   │  ← actual screenshot of chat interface   │
│    │   chat answer   │    with pose recommendation visible      │
│    │   with source   │                                          │
│    │   citation]     │                                          │
│    └─────────────────┘                                          │
│                                                                  │
│  RIGHT half (60%):                                              │
│                                                                  │
│    elbee                     ← brand name, bold white, 72pt     │
│    yogaman.club                                                  │
│                                                                  │
│    "Book → OCR → AI Chat"   ← subtitle, light purple, 28pt     │
│                                                                  │
│    [Stack badges]:                                               │
│     🐍 Python  ⚡ FastAPI  🧠 LangGraph  🦙 Ollama              │
│                                                                  │
│  Bottom right corner:                                            │
│    ▶ 5 min demo                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Colors

| Element | Hex |
|---|---|
| Background gradient start | `#1a1a2e` |
| Background gradient end | `#16213e` |
| Brand name text | `#ffffff` |
| Subtitle text | `#a78bfa` (violet-400) |
| Badge background | `#2d2d44` |
| Badge text | `#e2e8f0` |
| Play button accent | `#6C63FF` |

---

## Font
- Brand name: **Inter Black** or **Geist Bold**, 72pt
- Subtitle: **Inter Medium**, 28pt
- Badges: **JetBrains Mono**, 20pt

---

## Canva Template Steps

1. Go to https://canva.com → "Custom size" → 1280 × 720 px
2. Background: gradient from `#1a1a2e` to `#16213e` (left to right)
3. Left side: screenshot of `/yoga/chat` (crop to show only answer + citation)
4. Right side: text layers as specified above
5. Download as **PNG** → save as `video/thumbnail.png`
