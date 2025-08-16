import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

class WorkAIBrowser:
    def __init__(self):
        self.browser_context = None
        self.page = None
        self.playwright = None
        
    async def start_browser(self):
        """Initialize and start browser session"""
        try:
            self.playwright = await async_playwright().start()
            chromium = self.playwright.chromium

            chrome_path = os.getenv("BROWSER_USE_CHROME_PATH")
            user_data_dir = os.getenv("BROWSER_USE_USER_DATA_DIR")

            # Use launch_persistent_context if user_data_dir is set
            if user_data_dir:
                self.browser_context = await chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    executable_path=chrome_path if chrome_path else None,
                    headless=False,
                    slow_mo=1000 if os.getenv("DEBUG") == "True" else 0
                )
                # Get the existing page (Chrome opens with one page)
                self.page = self.browser_context.pages[0] if self.browser_context.pages else await self.browser_context.new_page()
            else:
                # Regular browser launch without persistent context
                self.browser_context = await chromium.launch(
                    headless=False,
                    executable_path=chrome_path if chrome_path else None,
                    slow_mo=1000 if os.getenv("DEBUG") == "True" else 0
                )
                self.page = await self.browser_context.new_page()

            timeout = int(os.getenv("SEARCH_TIMEOUT", "30000"))
            self.page.set_default_timeout(timeout)

            print("✅ Browser started successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            return False
    
    async def duckduckgo_search(self, query):
        """Perform DuckDuckGo search (more automation-friendly)"""
        try:
            await self.page.goto("https://duckduckgo.com")
            
            search_box = self.page.locator('input[name="q"]')
            await search_box.fill(query)
            await search_box.press("Enter")
            
            await self.page.wait_for_selector('h2', timeout=10000)
            
            results = []
            result_elements = await self.page.query_selector_all('h2 a')
            
            for i, element in enumerate(result_elements[:5]):
                try:
                    text = await element.inner_text()
                    href = await element.get_attribute('href')
                    results.append({
                        'title': text,
                        'url': href,
                        'position': i + 1
                    })
                except:
                    continue
            
            print(f"✅ Found {len(results)} search results for: {query}")
            return results
            
        except Exception as e:
            print(f"❌ Search failed for '{query}': {e}")
            return []
    
    async def extract_page_content(self, url):
        """Extract main content from a webpage"""
        try:
            await self.page.goto(url, wait_until='domcontentloaded')
            
            # Extract main text content
            content_selectors = [
                'main',
                'article', 
                '.content',
                '#content',
                '.post-content',
                '.entry-content',
                'body'
            ]
            
            content = ""
            for selector in content_selectors:
                try:
                    element = self.page.locator(selector).first
                    if await element.count() > 0:
                        content = await element.inner_text()
                        break
                except:
                    continue
            
            # Fallback to body if nothing found
            if not content:
                content = await self.page.locator('body').inner_text()
            
            # Clean and limit content
            content = content.strip()[:5000]  # Limit to 5000 chars
            
            print(f"✅ Extracted content from: {url[:50]}...")
            return content
            
        except Exception as e:
            print(f"❌ Failed to extract content from {url}: {e}")
            return ""
    
    async def close_browser(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.browser_context:
                await self.browser_context.close()
            if self.playwright:
                await self.playwright.stop()
            print("✅ Browser closed successfully")
        except Exception as e:
            print(f"❌ Error closing browser: {e}")

# Test the browser controller
async def test_browser():
    browser = WorkAIBrowser()
    await browser.start_browser()
    
    results = await browser.duckduckgo_search("OpenAI CEO")
    print("Search Results:")
    for result in results:
        print(f"- {result['title']}")
    
    await browser.close_browser()

if __name__ == "__main__":
    asyncio.run(test_browser())
