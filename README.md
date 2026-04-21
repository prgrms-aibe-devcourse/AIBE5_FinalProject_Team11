# geo

> OCR intake layer for **elbee.yogaman.club** — extracts, cleans and integrates
> book knowledge into the [yoga-chatbot](https://github.com/aiegoo/yoga-chatbot)
> search (`/yoga/search`) and chat (`/yoga/chat`) interfaces.

---

## Folder layout

```
geo/
├── screenshots/          # ← drop book page images here  (gitignored)
├── ocr/
│   ├── raw/              # raw tesseract output per book  (gitignored)
│   └── processed/        # cleaned plain-text copies      (tracked)
├── content/              # Jekyll Markdown with frontmatter (tracked)
├── data/json/            # ocr_database.json + indexes     (tracked)
├── scripts/
│   ├── adapt_content.py  # OCR text → Jekyll Markdown
│   ├── integrate.py      # push content into yoga-chatbot
│   └── watch.py          # auto-OCR on file drop (optional)
├── ocr_pipeline.py       # main OCR runner (entry point)
├── ROADMAP.md
└── requirements.txt
```

---

## Quick start

```bash
# 1. Install deps (tesseract already present via homebrew)
pip install -r requirements.txt

# 2. Drop screenshots into screenshots/  (jpg / png / webp)
#    Name them page_001.jpg … page_NNN.jpg (sorted order = book order)

# 3. Run OCR
python3 ocr_pipeline.py --book "Light on Yoga"

# 4. Adapt to Jekyll Markdown
python3 scripts/adapt_content.py --book "Light on Yoga"

# 5. Integrate into yoga-chatbot
python3 scripts/integrate.py --book "Light on Yoga"

# (Optional) Auto-watch folder and process on drop
python3 scripts/watch.py --book "Light on Yoga"
```

## Windows / WSL2 notes

- In WSL2, install Linux Python and Tesseract inside the distro:
  ```bash
  sudo apt update && sudo apt install -y python3.11 python3-pip python3-venv tesseract-ocr
  ```
- If Ollama runs on the Windows host and the API runs in WSL2, override the host URL:
  ```bash
  export OLLAMA_BASE_URL=http://host.docker.internal:11434
  ```
- If using native Windows Python and Tesseract is not on PATH, set:
  ```powershell
  setx TESSERACT_CMD "C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```

## Output schema

Each book produces three JSON files in `data/json/<slug>/`:

| File | Purpose |
|---|---|
| `ocr_database.json` | Full DB matching yoga-chatbot schema (metadata + pages array) |
| `page_index.json` | `{ "42": "cleaned text …" }` quick lookup |
| `keyword_index.json` | Inverted index: `{ "pranayama": [3, 17, 42, …] }` |

---

## Brand

Site: **elbee.yogaman.club**  
Target: `https://aiegoo.github.io/yoga/search` · `/yoga/chat`  
Repo: `git@github.com:aiegoo/aeogeo` (private)
