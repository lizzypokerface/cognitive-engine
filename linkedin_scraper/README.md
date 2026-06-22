# LinkedIn Job Research Tool

A two-step daily workflow for systematic LinkedIn job research. Browse searches, take notes, get summaries.

## First-time setup

Save your LinkedIn session to `auth.json` (only needed once):

```bash
python -m linkedin_scraper.auth
```

A browser window opens. Log in manually, then press Enter. Your session is saved and reused on every subsequent run.

## Daily workflow

### Step 1 — Browse

```bash
python -m linkedin_scraper.search
```

- Resets `research_notes.txt` with a section for each search term
- Opens all 10 searches as tabs in one browser window
- Browse through the tabs, then come back to the terminal and press Enter to close

### Step 2 — Take notes

Open `research_notes.txt`. Each section looks like:

```
%%% platform engineer
<paste your notes here>

%%% ai engineer
<paste your notes here>
```

Paste your observations under the relevant `%%%` heading. You can note company names, salary signals, skills required, or anything else. Skip sections where you found nothing interesting.

### Step 3 — Summarise

```bash
python -m linkedin_scraper.summarise
```

Each `%%%` block is sent to an LLM and summarised. Output is written to:

```
output/YYYY-MM-DD-research-summary.md
```

One `##` section per block, labelled by the heading you wrote after `%%%`.

## Search terms

Configured in `config.py` under `SEARCH_TERMS`. Edit that list to add, remove, or reorder terms — `search.py` and `research_notes.txt` will reflect the change automatically on the next run.

## Testing without API calls

Set `LLM_CONFIG` in `config.py` to use the mock provider:

```python
LLM_CONFIG = {"provider": "mock", "model": "default"}
```

Then run `summarise.py` — it returns canned responses without hitting Poe.
