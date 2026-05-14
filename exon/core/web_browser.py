"""
File: /opt/futureex/exon/core/web_browser.py
Author: Ashish Pal
Purpose: Headless Chromium web browser for advanced web scraping.
"""

import asyncio
import logging
from typing import Optional, List, Dict
from playwright.async_api import async_playwright, Browser, Page

logger = logging.getLogger(__name__)

class WebBrowser:
    """Headless Chromium browser for web scraping."""
    
    def __init__(self):
        self._browser: Optional[Browser] = None
        self._playwright = None
    
    async def start(self):
        """Launch headless browser."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--single-process'
            ]
        )
        logger.info("Headless Chromium started")
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search DuckDuckGo and return results."""
        if not self._browser:
            await self.start()
        
        results = []
        page: Page = await self._browser.new_page()
        
        try:
            # Go to DuckDuckGo
            await page.goto(f"https://html.duckduckgo.com/html/?q={query}", 
                          wait_until="domcontentloaded", timeout=15000)
            
            # Extract results
            result_elements = await page.query_selector_all('.result')
            
            for element in result_elements[:max_results]:
                try:
                    title_el = await element.query_selector('.result__title')
                    snippet_el = await element.query_selector('.result__snippet')
                    link_el = await element.query_selector('.result__url')
                    
                    title = await title_el.inner_text() if title_el else ""
                    snippet = await snippet_el.inner_text() if snippet_el else ""
                    link = await link_el.get_attribute('href') if link_el else ""
                    
                    if title and snippet:
                        results.append({
                            "title": title.strip(),
                            "snippet": snippet.strip(),
                            "url": link.strip()
                        })
                except Exception:
                    continue
            
            logger.info(f"Browser search found {len(results)} results")
            
        except Exception as e:
            logger.error(f"Browser search failed: {e}")
        finally:
            await page.close()
        
        return results
    
    async def fetch_page(self, url: str, max_chars: int = 5000) -> str:
        """Fetch and extract text from a URL."""
        if not self._browser:
            await self.start()
        
        page: Page = await self._browser.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            
            # Get page text
            text = await page.inner_text('body')
            
            # Clean up whitespace
            text = ' '.join(text.split())
            
            return text[:max_chars]
            
        except Exception as e:
            logger.error(f"Fetch page failed: {e}")
            return f"Error: {str(e)}"
        finally:
            await page.close()
    
    async def close(self):
        """Close browser."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()