import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to YC Companies with query...")
        await page.goto("https://www.workatastartup.com/companies?query=developer")
        await page.wait_for_timeout(3000)
        
        final_url = page.url
        print(f"Final URL: {final_url}")
        
        content = await page.content()
        if "Log in" in content or "Sign up" in content:
            print("Login links found.")
        
        inputs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('input')).map(i => i.outerHTML);
        }''')
        print("\\n--- INPUTS ---")
        for i in inputs:
            print(i)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
