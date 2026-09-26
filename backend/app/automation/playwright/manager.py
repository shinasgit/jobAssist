from app.automation.playwright.browser import PlaywrightBrowser
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self):
        self.browser_wrapper = PlaywrightBrowser()

    @asynccontextmanager
    async def get_page(self, timeout_ms: int = 30000):
        context = None
        page = None
        try:
            context = await self.browser_wrapper.new_context()
            page = await context.new_page()
            page.set_default_timeout(timeout_ms)
            yield page
        except Exception as e:
            logger.error(f"Error during browser session: {e}")
            raise
        finally:
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.error(f"Error closing page: {e}")
            if context:
                try:
                    await context.close()
                except Exception as e:
                    logger.error(f"Error closing context: {e}")

    async def shutdown(self):
        await self.browser_wrapper.close()

browser_manager = BrowserManager()
