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

    def is_valid_url(self, url):
        """Filter out bad URLs that cause navigation errors"""
        if not url or url.startswith('/?t=h_&q='):  # Skip DuckDuckGo internal URLs
            return False
        if any(bad in url for bad in ['javascript:', 'mailto:', 'ads.', '#']):
            return False
        if not url.startswith(('http://', 'https://')):
            return False
        return True

    async def start_browser(self):
        try:
            self.playwright = await async_playwright().start()
            chromium = self.playwright.chromium
            chrome_path = os.getenv("BROWSER_USE_CHROME_PATH")
            user_data_dir = os.getenv("BROWSER_USE_USER_DATA_DIR")

            if user_data_dir:
                self.browser_context = await chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    executable_path=chrome_path if chrome_path else None,
                    headless=False,
                    slow_mo=1000 if os.getenv("DEBUG") == "True" else 0
                )
                self.page = self.browser_context.pages[0] if self.browser_context.pages else await self.browser_context.new_page()
            else:
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
        try:
            await self.page.goto("https://duckduckgo.com")
            search_box = self.page.locator('input[name="q"]')
            await search_box.fill(query)
            await search_box.press("Enter")
            await self.page.wait_for_selector('h2', timeout=10000)
            
            results = []
            result_elements = await self.page.query_selector_all('h2 a')
            
            for i, element in enumerate(result_elements[:8]):  # Get more results to filter
                try:
                    text = await element.inner_text()
                    href = await element.get_attribute('href')
                    
                    # Filter valid URLs only
                    if self.is_valid_url(href):
                        results.append({
                            'title': text,
                            'url': href,
                            'position': i + 1
                        })
                except Exception:
                    continue
            
            print(f"✅ Found {len(results)} valid search results for: {query}")
            return results
        except Exception as e:
            print(f"❌ Search failed for '{query}': {e}")
            return []

    def get_domain_credibility_score(self, url):
        """Score URLs based on domain credibility"""
        url_lower = url.lower()
        
        # High credibility domains
        if any(domain in url_lower for domain in ['.edu', '.gov', '.org']):
            return 10
        if any(domain in url_lower for domain in ['reuters.com', 'bbc.com', 'apnews.com']):
            return 9
        if any(domain in url_lower for domain in ['cnn.com', 'ndtv.com', 'firstpost.com']):
            return 8
        if 'wikipedia.org' in url_lower:
            return 7
        
        # Medium credibility
        if any(domain in url_lower for domain in ['.com', '.in', '.uk']):
            return 5
            
        return 3  # Low credibility

    async def extract_page_content(self, url):
        try:
            await self.page.goto(url, wait_until='domcontentloaded')
            
            # Priority selectors for better content extraction
            content_selectors = [
                'article',
                'main', 
                '.content',
                '#content',
                '.post-content',
                '.entry-content',
                '.article-content',
                'body'
            ]
            
            content = ""
            for selector in content_selectors:
                try:
                    element = self.page.locator(selector).first
                    if await element.count() > 0:
                        content = await element.inner_text()
                        if len(content.strip()) > 100:  # Ensure meaningful content
                            break
                except Exception:
                    continue
            
            if not content:
                content = await self.page.locator('body').inner_text()
            
            # Clean and limit content
            content = content.strip()[:5000]
            print(f"✅ Extracted {len(content)} chars from: {url[:50]}...")
            return content
        except Exception as e:
            print(f"❌ Failed to extract content from {url}: {e}")
            return ""

    async def close_browser(self):
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
