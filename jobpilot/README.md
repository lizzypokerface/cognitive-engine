# jobpilot

Job searching is unpleasant. The process is draining, the feedback loop is slow, and it's easy to procrastinate indefinitely because no single day feels urgent. The solution isn't motivation — it's removing the decisions.

This is a system with fixed rules. You follow the rules, the work gets done, you don't have to feel anything about it.

## The system

**Monday to Wednesday — research (this tool)**

Two hours, then stop. Set a timer. Run the searches, paste the links, write brief notes. Generate the summary. Close the laptop.

The goal for these three days is a shortlist: 15–20 roles worth applying to. Not every role in the list will be strong. That's fine. You're building volume, not making final calls.

**Thursday to Friday — applications**

Work from the summary only — no new searching. Submit 10 applications and stop. Ten is enough. More is not better; it produces worse applications and burns time that belongs elsewhere.

**What this tool does**

It handles the mechanical half of research days. One command opens every configured search as a browser tab and resets your notes file. You browse, paste URLs, add a line of context. One more command scrapes each JD, runs it through an LLM, and writes a structured summary to a dated file in `output/`. That file is what you apply from on Thursday.

The point is that you shouldn't have to think about the process — only the content. Open, browse, note, summarise, done.

---

## First-time setup

**1. Install dependencies**

```bash
cd jobpilot
uv sync
uv run playwright install chromium
```

**2. Add your Poe API key to `.env`**

```
POE_API_KEY=your_key_here
```

**3. Save your LinkedIn session (once only)**

```bash
uv run python -m jobpilot.auth
```

A browser opens. Log in to LinkedIn manually, then press Enter. Your session is saved to `auth.json` and reused automatically. Re-run this if scraping stops working (sessions expire after a few weeks).

---

## Daily workflow (research days)

All commands run from the `jobpilot/` directory.

### Step 1 — Open searches

```bash
uv run python -m jobpilot.search
```

Opens all configured search terms as tabs in one browser window. Also resets `research_notes.txt` with a blank section for each term. Browse the tabs, find the interesting roles.

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
- Write any observations below the links
- Skip sections where you found nothing — empty sections are ignored

### Step 3 — Generate the report

```bash
uv run python -m jobpilot.summarise
```

Opens a browser, scrapes each job page using your saved session, summarises each JD (title, salary, skills, requirements, one key observation), and writes everything to `output/YYYY-MM-DD-research-summary.md`.

That file is your shortlist input for application days.

---

## Further reading

- `docs/job_search_schedule.md` — full schedule, daily rules, and the reasoning behind them
- `docs/interview_and_communications.md` — interview prep and communications framework

---

## Configuration

All configuration lives in `jobpilot/config.py`.

### Search terms

Edit `SEARCH_TERMS` — drives both the browser tabs and the note sections:

```python
SEARCH_TERMS = [
    "cloud engineer",
    "solutions engineer",
    # add, remove, or reorder freely
]
```

### LLM model

```python
LLM_CONFIG = {"provider": "poe", "model": "gemini-3.1-flash-lite"}
```

| Provider | Model | Notes |
|---|---|---|
| `poe` | `gemini-3-flash` | Larger context, better quality |
| `poe` | `gemini-3.1-flash-lite` | Faster, cheaper |
| `mock` | `default` | No API calls — returns canned text for testing |

### Output location

```python
OUTPUT_DIR = "output"
```

---

## Troubleshooting

**Scraping returns "could not load"**
Session has expired. Run `uv run python -m jobpilot.auth` to refresh it.

**No content but no auth error**
LinkedIn changed their HTML structure. Check `output/debug_last_jd.html` (saved automatically) to see what the page actually returned, and update the selectors in `summarise.py`.

**Testing without API calls**
Set `LLM_CONFIG = {"provider": "mock", "model": "default"}` in `config.py`, then run `summarise.py` — returns canned responses without hitting Poe.
