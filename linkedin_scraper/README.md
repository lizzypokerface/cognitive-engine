# LinkedIn Job Research Tool

Systematic daily job research for Singapore. Browse configured search terms, take notes with job links, get an AI-summarised report.

---

## First-time setup

**1. Install dependencies**

```bash
cd linkedin_scraper
uv sync
uv run playwright install chromium
```

**2. Add your Poe API key to `.env`**

```
POE_API_KEY=your_key_here
```

**3. Save your LinkedIn session (once only)**

```bash
uv run python -m linkedin_scraper.auth
```

A browser opens. Log in to LinkedIn manually, then press Enter. Your session is saved to `auth.json` and reused automatically. Re-run this if scraping stops working (session expires after a few weeks).

---

## Daily workflow

All commands run from the `linkedin_scraper/` directory.

### Step 1 — Open searches

```bash
uv run python -m linkedin_scraper.search
```

Opens all configured search terms as tabs in one browser window and resets `research_notes.txt` with a blank section for each term. Browse the tabs, find interesting roles.

### Step 2 — Add your notes

Open `research_notes.txt`. Each section looks like:

```
%%% solutions engineer

https://www.linkedin.com/jobs/view/4426208455/?...
https://www.linkedin.com/jobs/view/4420087041/?...

Strong TikTok role. Hybrid sales-engineering. Going to apply.

%%% platform engineer

https://www.linkedin.com/jobs/view/4399001234/?...

Grab and Sea most active. Heavy Kubernetes/Terraform.
```

- Paste job URLs at the top of the section (copy directly from LinkedIn — tracking params are stripped automatically)
- Write any freetext observations below the links
- Skip sections where you found nothing — empty sections are ignored

### Step 3 — Generate the report

```bash
uv run python -m linkedin_scraper.summarise
```

- Opens a browser, scrapes each job page using your saved session
- Summarises each JD individually (title, salary, skills, requirements, observation)
- Summarises your freetext notes
- Writes everything to `output/YYYY-MM-DD-research-summary.md`

---

## Updating the config

All configuration lives in `linkedin_scraper/config.py`.

### Change search terms

Edit `SEARCH_TERMS` — the list drives both `search.py` (which tabs to open) and `research_notes.txt` (which sections are scaffolded):

```python
SEARCH_TERMS = [
    "cloud engineer",
    "solutions engineer",
    # add, remove, or reorder freely
]
```

### Change the LLM model

```python
LLM_CONFIG = {"provider": "poe", "model": "gemini-3-flash-lite"}
```

| Provider | Model | Notes |
|---|---|---|
| `poe` | `gemini-3-flash` | Larger context, better quality |
| `poe` | `gemini-3-flash-lite` | Faster, cheaper |
| `mock` | `default` | No API calls — returns canned text for testing |

### Change the output location

```python
OUTPUT_DIR = "output"
```

---

## Troubleshooting

**Scraping returns "could not load"**
Your LinkedIn session has expired. Run `uv run python -m linkedin_scraper.auth` to refresh it.

**No content but no auth error either**
LinkedIn changed their HTML structure. Check `output/debug_last_jd.html` (saved automatically) to inspect what the page actually returned, and update the selectors in `summarise.py`.

**Testing without API calls**
Set `LLM_CONFIG = {"provider": "mock", "model": "default"}` in `config.py`, then run `summarise.py` — it returns canned responses without hitting Poe.
