"""
Daily LinkedIn JD scraper.

    python -m linkedin_scraper.scraper

Reads preset search URLs from config.py, scrapes up to MAX_JOBS_PER_SEARCH listings,
summarises each with the LLM, and writes a dated markdown file to output/.
"""

import asyncio
import os
import random
import sys
from datetime import date

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from linkedin_scraper.config import AUTH_FILE, LLM_CONFIG, MAX_JOBS_PER_SEARCH, OUTPUT_DIR, SEARCH_URLS
from linkedin_scraper.prompts import DAILY_SUMMARY_PROMPT, PER_JD_PROMPT
from src.core.llm import get_llm_client

JUNK_TAGS = ["nav", "footer", "header", "aside", "script", "style", "noscript", "form"]

JD_PANEL_SELECTOR = ".jobs-search__job-details"
LISTING_SELECTOR = ".jobs-search-results__list-item"
SEE_MORE_SELECTOR = "button.jobs-description__footer-button"


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(JUNK_TAGS):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def _write(path: str, text: str):
    with open(path, "a", encoding="utf-8") as f:
        f.write(text + "\n\n")


async def scrape_search(page, search_url: str, llm, output_path: str, model: str) -> list[str]:
    notes = []

    await page.goto(search_url, wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)

    listings = await page.query_selector_all(LISTING_SELECTOR)
    listings = listings[:MAX_JOBS_PER_SEARCH]

    if not listings:
        print(f"  No listings found for {search_url}")
        return notes

    print(f"  Found {len(listings)} listings")

    for i, listing in enumerate(listings, 1):
        try:
            await listing.click()
            await page.wait_for_timeout(int(random.uniform(1000, 3000)))

            # Expand "See more" if present
            see_more = await page.query_selector(SEE_MORE_SELECTOR)
            if see_more:
                await see_more.click()
                await page.wait_for_timeout(1000)

            panel = await page.query_selector(JD_PANEL_SELECTOR)
            if not panel:
                print(f"  [{i}] JD panel not found, skipping")
                continue

            html = await panel.inner_html()
            jd_text = _extract_text(html)

            if len(jd_text) < 200:
                print(f"  [{i}] JD text too short ({len(jd_text)} chars), skipping")
                continue

            prompt = PER_JD_PROMPT.format(role_description=jd_text[:6000])
            print(f"  [{i}] Summarising...")
            note = llm.query(prompt, model=model)
            notes.append(note)
            _write(output_path, f"---\n\n{note}")

            await page.wait_for_timeout(int(random.uniform(1000, 3000)))

        except Exception as e:
            print(f"  [{i}] Error: {e}")
            continue

    return notes


async def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"{date.today().isoformat()}.md")

    llm = get_llm_client(LLM_CONFIG)
    model = LLM_CONFIG.get("model", "default")

    _write(output_path, f"# LinkedIn Job Research — {date.today().isoformat()}\n")

    all_notes: list[str] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        storage = AUTH_FILE if os.path.exists(AUTH_FILE) else None
        if not storage:
            print("WARNING: auth.json not found — you may hit a login wall. Run auth.py first.")

        context = await browser.new_context(storage_state=storage)
        page = await context.new_page()

        for url in SEARCH_URLS:
            print(f"\nSearching: {url}")
            notes = await scrape_search(page, url, llm, output_path, model)
            all_notes.extend(notes)

        await browser.close()

    if all_notes:
        print("\nGenerating daily summary...")
        summary_prompt = DAILY_SUMMARY_PROMPT.format(all_role_outputs="\n\n---\n\n".join(all_notes))
        summary = llm.query(summary_prompt, model=model)
        _write(output_path, f"---\n\n# Daily Summary\n\n{summary}")

    print(f"\nDone. Output: {output_path}")


if __name__ == "__main__":
    asyncio.run(run())
