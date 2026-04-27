# Pitch — Descript Production Kit

Two videos, both assembled in [Descript](https://www.descript.com/) from assets that
already live in this repo. Each "slide" in the decks below maps **1-to-1 to a
Descript scene**. Drop the listed asset into the scene canvas, paste the VO line
into the script panel, and run the listed Descript prompt (Underlord / Magic
Edit / AI Voice) to finish the scene.

## What's in the kit

| File | Purpose |
|---|---|
| [90s_teaser_descript.md](90s_teaser_descript.md) | Investor teaser, 90 s, 16:9. Ten scenes. |
| [5min_deepdive_descript.md](5min_deepdive_descript.md) | Engineering deep-dive, 5 min, 16:9. Five scenes. |
| [descript_script_ko.txt](descript_script_ko.txt) | Korean VO, Descript-importable (one paragraph per scene). |
| [descript_script_en.txt](descript_script_en.txt) | English VO, Descript-importable. |
| [9x16_social_cut.md](9x16_social_cut.md) | Vertical re-cut plan for Shorts/Reels/TikTok. |

## Source assets (already committed)

All teaser visuals: [../assets/teaser/](../assets/teaser/)
- `match_demo.mp4` — primary screen-capture (matching demo, ~12 s)
- `shot_03a_blank.png`, `shot_03_typing.png`, `shot_04_ranked.png`, `shot_05_breakdown.png`, `shot_07_jsonld.png` — stills
- `caption_06_headline.svg`, `caption_08_aeo.svg`, `end_card.svg` — overlay graphics
- `jsonld_doc.json`, `jsonld.html` — proof-point overlay
- `teaser_ko.srt`, `teaser_en.srt` — subtitle tracks
- `vo_ko.txt`, `vo_en.txt` — voiceover originals

Architecture diagram: [../video/ARCHITECTURE_DIAGRAM.md](../video/ARCHITECTURE_DIAGRAM.md)
Long-form script source: [../video/SCRIPT.md](../video/SCRIPT.md)

## Descript workflow (do this once)

1. **New project → "Screen recording / Slideshow"**, 1920×1080, 30 fps.
2. **Project → Import** → drag the entire `assets/teaser/` folder.
3. **Script panel → File → Import script** → pick `descript_script_ko.txt`
   (primary) **or** `descript_script_en.txt`. Each `# SCENE N` heading
   becomes a scene break automatically.
4. **Speakers → Add AI voice** (Overdub) — clone your own voice, or use a
   Descript stock voice. Recommended: **"Sora" (KO)** for Korean track,
   **"Atlas" (EN)** for English track. -16 LUFS.
5. For each scene, follow the slide deck:
   - drop the named asset onto the canvas
   - paste the **Descript prompt** into Underlord ("Compose this scene")
   - apply the listed transition
6. **Subtitles → Auto-generate**, then replace with `teaser_ko.srt` /
   `teaser_en.srt` from `assets/teaser/` for accurate Korean timing.
7. **Export → Master 1080p H.264** + **Export → 9:16 vertical** (Descript
   reframes automatically; verify caption position).

## Conventions used in the slide decks

- **VO** = the line spoken (paste into script panel).
- **On-screen** = literal text overlay (use Descript text layers).
- **Asset** = filename relative to `assets/teaser/`.
- **Prompt** = ready-to-paste Descript Underlord instruction.
- **Transition** = Descript built-in transition name.
- **Lower-third** = optional bottom-strip caption (Descript "Lower third" template).
