"""
Run once to save your LinkedIn session.

    python -m linkedin_scraper.auth

A browser window will open. Log in to LinkedIn manually, then press Enter here.
The session is saved to auth.json and loaded automatically by scraper.py.
"""

import asyncio

from linkedin_scraper.config import AUTH_FILE
from playwright.async_api import async_playwright


async def save_session():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.linkedin.com/login")
        print("\nLog in to LinkedIn in the browser window that just opened.")
        input("Press Enter here once you are logged in and can see your feed... ")

        await context.storage_state(path=AUTH_FILE)
        await browser.close()
        print(f"Session saved to {AUTH_FILE}")


if __name__ == "__main__":
    asyncio.run(save_session())
