import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


async def fetch_page(url: str) -> str:
    """Download full page content using Playwright headless browser."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            content = await page.content()
            logger.info("fetched page", extra={"url": url, "length": len(content)})
            return content
        finally:
            await browser.close()
