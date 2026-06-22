"""
Opens LinkedIn job search pages for all configured search terms as browser tabs.

    python -m linkedin_scraper.search
"""

import asyncio
import os
import sys
from urllib.parse import quote_plus

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright

from linkedin_scraper.config import AUTH_FILE, LINKEDIN_SEARCH_BASE, RESEARCH_NOTES_FILE, SEARCH_TERMS


def reset_notes():
    with open(RESEARCH_NOTES_FILE, "w", encoding="utf-8") as f:
        for term in SEARCH_TERMS:
            f.write(f"%%% {term}\n\n\n\n")
    print(f"Research notes reset → {RESEARCH_NOTES_FILE}\n")


async def run():
    reset_notes()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        storage = AUTH_FILE if os.path.exists(AUTH_FILE) else None
        context = await browser.new_context(storage_state=storage)

        for i, term in enumerate(SEARCH_TERMS):
            url = LINKEDIN_SEARCH_BASE.format(keywords=quote_plus(term))
            page = await context.new_page()
            print(f"[{i + 1}/{len(SEARCH_TERMS)}] {term}")
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(500)

        print(f"\nAll {len(SEARCH_TERMS)} searches open. Browse and take notes in research_notes.txt.")
        print("Press Enter to close the browser...")
        input()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(run())
