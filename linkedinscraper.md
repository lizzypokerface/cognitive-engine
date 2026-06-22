# LinkedIn JD Scraper — Project Spec

## What This Is

A daily Python script that automates job market research. It opens LinkedIn job search pages, reads the top job listings, summarises each one using Claude, and writes the results to a file. Run it once a day, read the output, move on.

---

## The Problem It Solves

Manually browsing LinkedIn job listings is slow, noisy, and pulls you into the recommendation system. This script treats it as a data extraction process: in, extract, out. The output is structured intelligence notes, not a browser session.

---

## Workflow — Step by Step

```
1. AUTH (run once)
   └── Playwright opens a browser window
   └── You log in to LinkedIn manually
   └── Session saved to auth.json
   └── All future runs load auth.json — no login needed

2. LOAD SEARCH URLS (from config)
   └── A simple list of preset LinkedIn search URLs in config.py
   └── Each URL is a saved search (keyword + location + filters already baked in)
   └── Example:
       https://www.linkedin.com/jobs/search-results/?keywords=solutions%20engineer&geoId=102454443

3. FOR EACH SEARCH URL:
   └── Load the page in Playwright
   └── Collect the top 10 job listings from the left-hand results panel
   └── For each listing:
       ├── Click the listing to load the JD on the right
       ├── Wait for content to render
       ├── Click "See more" / "Show more" if present
       └── Extract the full job description text

4. SUMMARISE EACH JD
   └── Pass the raw JD text to Claude API (claude-sonnet-4-6)
   └── Use the analysis prompt (see below)
   └── Receive structured output: role, company, salary, key skills, observation

5. WRITE TO FILE
   └── Append each structured note to output/YYYY-MM-DD.md
   └── After all JDs processed, run the end-of-day summary prompt
   └── Append the daily rollup to the same file
```

---

## Config (config.py)

```python
SEARCH_URLS = [
    "https://www.linkedin.com/jobs/search-results/?keywords=solutions%20engineer&geoId=102454443&distance=0.0",
    "https://www.linkedin.com/jobs/search-results/?keywords=cloud%20engineer&geoId=102454443&distance=0.0",
    # add more as needed
]

MAX_JOBS_PER_SEARCH = 10
OUTPUT_DIR = "output"
AUTH_FILE = "auth.json"
```

---

## File Structure

```
linkedin-scraper/
├── auth.py           ← Run once to save LinkedIn session
├── config.py         ← Your preset search URLs live here
├── scraper.py        ← Main daily runner
├── prompts.py        ← Analysis and summary prompts
├── auth.json         ← Saved session (auto-generated, gitignore this)
└── output/
    └── 2026-06-22.md ← Daily output file
```

---

## Prompts

### Per-JD Analysis Prompt

```
You are a job market intelligence analyst. Your job is to read a role
description so the user doesn't have to, and surface only what matters.

ROLE DESCRIPTION:
{role_description}

Return your analysis in this exact format, nothing else:

ROLE TITLE:
COMPANY:
SALARY: [stated range, or estimate from seniority signals with a (est.) label]
KEY SKILLS: [3-5 skills or tools that kept appearing, comma separated]
OBSERVATION: [One sentence. The single most useful thing to remember about
this role when looking back at 30 roles later.]
```

### End-of-Day Summary Prompt

```
You are a job market research analyst. Read all of today's role notes
together and produce a concise end-of-day research summary.

Do not summarise each role individually. Extract what the collection reveals.

TODAY'S ROLE NOTES:
{all_role_outputs}

Return in this exact structure:

DATE: [today's date]
ROLES SCANNED: [count]

SKILL PATTERNS
SALARY LANDSCAPE
EMPLOYER PATTERNS
LANGUAGE FLAGS
SIGNAL ROLES
ONE THING
```

---

## Key Technical Decisions

**Auth:** Playwright saves session state after a one-time manual login. No credentials stored in code.

**Anti-bot:** Add random delays between clicks (1–3 seconds). Don't hammer. Behave like a human.

**"See more" handling:** After clicking a JD, check for and click any expand buttons before extracting text. LinkedIn often hides the bottom half of a JD behind one.

**Output format:** Plain markdown. One file per day. Append-only. Easy to read, easy to grep.

**Model:** `claude-sonnet-4-6` via Anthropic API. Fast and cheap enough for 10–20 JDs a day.

---

## What It Does NOT Do

- It does not apply to jobs
- It does not store data in a database
- It does not run on a schedule (you run it manually each day)
- It does not scrape salary data if not shown — it estimates from seniority signals and labels it `(est.)`

---

## Prior Art

This is a well-trodden pattern. Existing repos to reference:

- `ManiMozaffar/linkedIn-scraper` — Playwright + ChatGPT analysis, closest to this use case
- `yagyeshVyas/linkedin-scraper` — clean structure, session caching, Excel output
- DEV.to tutorial: "Web Scraping LinkedIn Jobs with Playwright" — covers login, search params, CSV export

The main difference here: we start from preset search URLs (already filtered), not keyword inputs. Simpler entry point, less configuration overhead.

---

## Known Risk

LinkedIn actively detects and rate-limits scrapers. Mitigation:
- Use a persistent browser session (looks like a real user)
- Keep delays human-like
- Don't run more than once per day
- If you get CAPTCHAs, slow down or add a proxy

---

## Next Steps When Picking This Up

1. Clone or create the repo
2. Run `auth.py` once to save your LinkedIn session
3. Add your preset search URLs to `config.py`
4. Set your `ANTHROPIC_API_KEY` environment variable
5. Run `scraper.py` and check `output/`