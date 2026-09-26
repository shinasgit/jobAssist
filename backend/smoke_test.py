import asyncio
from app.automation.playwright.manager import browser_manager

async def run_smoke_test():
    print("Starting Playwright smoke test...")
    try:
        async with browser_manager.get_page(timeout_ms=15000) as page:
            test_url = "https://example.com"
            print(f"Navigating to {test_url}...")
            await page.goto(test_url)
            title = await page.title()
            print(f"Success! Page title is: '{title}'")
    except Exception as e:
        print(f"Smoke test failed: {e}")
    finally:
        await browser_manager.shutdown()
        print("Browser closed.")

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
