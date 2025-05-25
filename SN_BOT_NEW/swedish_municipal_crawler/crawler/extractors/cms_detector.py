import re
import asyncio
from playwright.async_api import async_playwright

class SwedishCMSDetector:
    def __init__(self):
        self.cms_signatures = {
            'sitevision': {
                'patterns': [
                    r'sv-portlet', r'sitevision', r'sv-layout',
                    r'sv-search-result', r'sv-cookie-consent',
                    r'sv-normal-link'
                ],
                'js_markers': ['SitevisionPublic', 'sv.PageContext'],
                'requires_js': True
            },
            'municipio': {
                'patterns': [
                    r'municipio-theme', r'wp-content', r'wp-includes',
                    r'acf-', r'helsingborg', r'municipio'
                ],
                'js_markers': ['wp', 'municipio'],
                'requires_js': False
            },
            'episerver': {
                'patterns': [
                    r'episerver', r'optimizely', r'epi-cms',
                    r'EPiServer'
                ],
                'js_markers': ['epi', 'episerver'],
                'requires_js': True
            },
            'sitecore': {
                'patterns': [
                    r'sitecore', r'sc_', r'scLayout'
                ],
                'js_markers': [],
                'requires_js': False
            }
        }
        
        # Cache for detected CMS types
        self.cms_cache = {}
    
    async def detect_cms_with_js(self, url):
        """Detect CMS using Playwright for JavaScript rendering"""
        if url in self.cms_cache:
            return self.cms_cache[url]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Get rendered HTML
                content = await page.content()
                
                # Check JavaScript variables
                js_markers_found = []
                for cms, config in self.cms_signatures.items():
                    for marker in config.get('js_markers', []):
                        try:
                            exists = await page.evaluate(f"typeof {marker} !== 'undefined'")
                            if exists:
                                js_markers_found.append(cms)
                        except:
                            pass
                
                await browser.close()
                
                # Detect from content
                detected_cms = self._detect_from_content(content)
                
                # Prefer JS marker detection
                if js_markers_found:
                    detected_cms = js_markers_found[0]
                
                self.cms_cache[url] = detected_cms
                return detected_cms
                
            except Exception as e:
                await browser.close()
                return 'generic'
    
    def detect_cms(self, response):
        """Detect CMS type from response content (sync version)"""
        return self._detect_from_content(response.text)
    
    def _detect_from_content(self, content):
        """Detect CMS from HTML content"""
        content_lower = content.lower()
        scores = {}
        
        for cms, config in self.cms_signatures.items():
            patterns = config['patterns']
            pattern_matches = sum(1 for pattern in patterns 
                                if re.search(pattern, content_lower, re.IGNORECASE))
            scores[cms] = pattern_matches
        
        # Return CMS with highest score if above threshold
        best_cms = max(scores, key=scores.get)
        if scores[best_cms] >= 2:
            return best_cms
        
        return 'generic'
    
    def get_cms_config(self, cms_type):
        """Return CMS-specific crawling configuration"""
        configs = {
            'sitevision': {
                'js_required': True,
                'wait_time': 3,
                'css_selectors': ['.sv-portlet', '.sv-text-portlet'],
                'link_patterns': [r'/sv\.portlet'],
                'pdf_selectors': ['.sv-document-portlet a[href$=".pdf"]']
            },
            'municipio': {
                'js_required': False,
                'wait_time': 1,
                'css_selectors': ['.entry-content', '.wp-content'],
                'api_endpoints': ['/wp-json/wp/v2/'],
                'pdf_selectors': ['a[href*="/wp-content/uploads/"][href$=".pdf"]']
            },
            'episerver': {
                'js_required': True,
                'wait_time': 2,
                'css_selectors': ['.block', '.content-area'],
                'pdf_selectors': ['a[href$=".pdf"]']
            },
            'generic': {
                'js_required': False,
                'wait_time': 1,
                'css_selectors': ['main', '.content', '#content'],
                'link_patterns': [],
                'pdf_selectors': ['a[href$=".pdf"]']
            }
        }
        return configs.get(cms_type, configs['generic']) 