import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = await context.new_page()
        
        # Test search directly via URL
        url = "https://remoteok.com/remote-junior-ai-developer-jobs"
        print(f"Navigating to {url}...")
        await page.goto(url)
        await page.wait_for_timeout(3000)
        
        title = await page.title()
        print(f"Page Title: {title}")
        
        content = await page.content()
        if "captcha" in content.lower() or "cloudflare" in content.lower() or "just a moment" in content.lower():
            print("WARNING: Captcha or bot protection detected!")
        else:
            print("No captcha text detected.")
        
        # Check job cards
        jobs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('tr.job')).map(job => {
                const title = job.querySelector('h2[itemprop="title"]');
                const company = job.querySelector('h3[itemprop="name"]');
                const locs = Array.from(job.querySelectorAll('.location')).map(l => l.innerText);
                const time = job.querySelector('time');
                const url = job.getAttribute('data-url');
                return {
                    title: title ? title.innerText.trim() : null,
                    company: company ? company.innerText.trim() : null,
                    locations: locs,
                    posted: time ? time.getAttribute('datetime') : null,
                    url: url ? `https://remoteok.com${url}` : null
                };
            });
        }''')
        
        print(f"\\n--- JOBS FOUND: {len(jobs)} ---")
        for j in jobs[:5]:
            print(j)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
