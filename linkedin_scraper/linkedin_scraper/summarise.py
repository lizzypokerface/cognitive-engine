"""
Reads research_notes.txt, splits on '%%% <label>' blocks.
For each block, LinkedIn job URLs are scraped and summarised individually.
Any freetext notes in the block are summarised separately.
Output: output/YYYY-MM-DD-research-summary.md

    python -m linkedin_scraper.summarise
"""

import asyncio
import os
import re
import sys
from datetime import date

from dotenv import load_dotenv

load_dotenv()

from playwright.async_api import async_playwright

from linkedin_scraper.config import AUTH_FILE, LLM_CONFIG, OUTPUT_DIR, RESEARCH_NOTES_FILE
from linkedin_scraper.llm import MockLLMClient, ProductionLLMClient

LINKEDIN_JOB_RE = re.compile(r"https://www\.linkedin\.com/jobs/view/(\d+)/[^\s]*")

JD_SELECTORS = [
    "#job-details",
    ".jobs-description__content",
    ".jobs-description-content__text",
    ".job-view-layout",
]

TITLE_SELECTORS = [
    ".job-details-jobs-unified-top-card__job-title",
    "h1",
]

COMPANY_SELECTORS = [
    ".job-details-jobs-unified-top-card__company-name",
    ".jobs-unified-top-card__company-name",
]

JD_PROMPT = """You are a job market intelligence analyst. Read the role description below and extract what matters.

ROLE DESCRIPTION:
{content}

Return your analysis in this exact format:

### {title}

[1-2 sentences on what this team actually does and what you'd be doing day-to-day.]

Salary: [stated range, or estimate from seniority signals labelled (est.)]
Skills: [4-6 key skills or tools, comma separated]
Requirements: [seniority level, years of experience, must-have qualifications]
Observation: [One sentence. The single most useful thing to remember about this role.]

URL: {url}"""

NOTES_PROMPT = """Summarise these job research notes in 2-4 bullet points. \
Report only what is stated. Do not ask for more information.

NOTES:
{notes}"""


def get_client():
    if LLM_CONFIG.get("provider") == "mock":
        return MockLLMClient()
    return ProductionLLMClient(LLM_CONFIG)


def load_blocks(path: str) -> list[tuple[str, str]]:
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    entries = []
    for chunk in raw.split("%%%"):
        chunk = chunk.strip()
        if not chunk:
            continue
        first_line, _, rest = chunk.partition("\n")
        heading = first_line.strip()
        notes = rest.strip()
        if heading and notes:
            entries.append((heading, notes))
    return entries


def extract_urls(text: str) -> tuple[list[str], str]:
    """Returns (clean_job_urls, remaining_freetext)."""
    job_ids = LINKEDIN_JOB_RE.findall(text)
    urls = [f"https://www.linkedin.com/jobs/view/{jid}/" for jid in job_ids]
    freetext = LINKEDIN_JOB_RE.sub("", text).strip()
    return urls, freetext


async def scrape_jd(page, url: str) -> dict:
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)

    current_url = page.url
    page_title = await page.title()
    print(f"    page: {page_title[:70]}")

    if any(x in current_url for x in ("login", "authwall", "checkpoint")):
        print("    ⚠ Redirected to auth page — run `python -m linkedin_scraper.auth` to refresh your session")
        return {"url": url, "title": "", "content": ""}

    for btn_sel in ["button.jobs-description__footer-button", "button.show-more-less-html__button"]:
        btn = await page.query_selector(btn_sel)
        if btn:
            await btn.click()
            await page.wait_for_timeout(500)
            break

    title = ""
    for sel in TITLE_SELECTORS:
        el = await page.query_selector(sel)
        if el:
            title = (await el.inner_text()).strip()
            if title:
                break

    company = ""
    for sel in COMPANY_SELECTORS:
        el = await page.query_selector(sel)
        if el:
            company = (await el.inner_text()).strip()
            if company:
                break

    content = ""
    for sel in JD_SELECTORS:
        el = await page.query_selector(sel)
        if el:
            content = (await el.inner_text()).strip()
            if content:
                break

    # Fallback: grab visible text from the main layout column
    if not content:
        for fallback in ["main", ".scaffold-layout__main", "article", "body"]:
            el = await page.query_selector(fallback)
            if el:
                text = (await el.inner_text()).strip()
                if len(text) > 300:
                    content = text[:8000]
                    print(f"    used fallback selector: {fallback}")
                    break

    if not content:
        html = await page.content()
        debug_path = os.path.join(OUTPUT_DIR, "debug_last_jd.html")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"    ⚠ No content found. Debug HTML saved → {debug_path}")

    return {
        "url": url,
        "title": f"{title} — {company}" if company else title,
        "content": content,
    }


async def scrape_all(urls: list[str]) -> dict[str, dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        storage = AUTH_FILE if os.path.exists(AUTH_FILE) else None
        context = await browser.new_context(storage_state=storage)
        page = await context.new_page()

        results = {}
        for i, url in enumerate(urls, 1):
            print(f"  [{i}/{len(urls)}] scraping {url}")
            results[url] = await scrape_jd(page, url)

        await browser.close()
    return results


def main():
    if not os.path.exists(RESEARCH_NOTES_FILE):
        print(f"No file found at {RESEARCH_NOTES_FILE}")
        sys.exit(1)

    blocks = load_blocks(RESEARCH_NOTES_FILE)
    if not blocks:
        print("No note blocks found.")
        sys.exit(1)

    # Parse each block into URLs + freetext
    parsed = [(heading, *extract_urls(notes)) for heading, notes in blocks]

    # Collect and scrape all URLs in one browser session
    all_urls = [url for _, urls, _ in parsed for url in urls]
    scraped = {}
    if all_urls:
        print(f"\nScraping {len(all_urls)} job page(s)...")
        scraped = asyncio.run(scrape_all(all_urls))

    client = get_client()
    model = LLM_CONFIG.get("model", "default")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{date.today().isoformat()}-research-summary.md")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Job Research Summary — {date.today().isoformat()}\n\n")

        for heading, urls, freetext in parsed:
            f.write(f"## {heading}\n\n")

            for url in urls:
                data = scraped.get(url, {})
                if data.get("content"):
                    print(f"  Summarising: {data['title'][:60]}...")
                    prompt = JD_PROMPT.format(
                        content=data["content"][:6000],
                        title=data["title"],
                        url=url,
                    )
                    f.write(client.query(prompt, model=model).strip())
                    f.write("\n\n")
                else:
                    f.write(f"- {url} *(could not load)*\n\n")

            if freetext:
                print(f"  Summarising notes: {heading}...")
                f.write("**Notes:**\n\n")
                f.write(client.query(NOTES_PROMPT.format(notes=freetext), model=model).strip())
                f.write("\n\n")

            f.write("---\n\n")

    print(f"\nDone → {out_path}")


if __name__ == "__main__":
    main()
