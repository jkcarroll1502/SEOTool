# Jasleen — SEO Article Generation Tool

A step-by-step web tool that takes you from a keyword to a fully optimised, publish-ready SEO article — powered by Claude AI and built on DIAL Agents best practice guides.

## Features

- **6-step guided workflow** — keyword → LSI research → content brief → full article → refine → export
- **Live streaming** — watch the article write itself in real time
- **Based on best practice guides** — Flesch-Kincaid readability, LSI keywords, nested headings, meta data, FAQs
- **Refine & review** — one-click refinements or custom instructions
- **Export** — saves as `.md` + `.json` to your Desktop

## Setup

### 1. Install dependencies
```bash
pip3 install anthropic flask
```

### 2. Set your Anthropic API key
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Run the app
```bash
python3 app.py
```

Then open **http://127.0.0.1:5000** in your browser.

### Or use the launcher script
```bash
./start.sh
```

## Workflow

| Step | What happens |
|---|---|
| 1 | Enter primary keyword, brand, industry, audience & tone |
| 2 | Generate LSI/semantic keywords with search volume estimates |
| 3 | Build content angle, outline, title tag & meta description |
| 4 | Write full 800–2000 word SEO article |
| 5 | Refine with quick presets or custom instructions |
| 6 | Save to Desktop as Markdown + JSON |

## Output files

Saved to `~/Desktop/SEO Articles/`:
- `keyword_timestamp.md` — formatted article ready to copy into your CMS
- `keyword_timestamp.json` — structured data with all SEO fields

## Requirements

- Python 3.9+
- Anthropic API key with credits
- `anthropic` and `flask` packages
