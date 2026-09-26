from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
import logging

logger = logging.getLogger(__name__)

class PlaywrightBrowser:
    def __init__(self):
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None

    async def launch(self, headless: bool = True) -> Browser:
        if not self.playwright:
            self.playwright = await async_playwright().start()
        if not self.browser:
            logger.info("Launching Chromium browser...")
            self.browser = await self.playwright.chromium.launch(headless=headless)
        return self.browser

    async def new_context(self, **kwargs) -> BrowserContext:
        if not self.browser:
            await self.launch()
        return await self.browser.new_context(**kwargs)

    async def close(self):
        if self.browser:
            logger.info("Closing browser...")
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
