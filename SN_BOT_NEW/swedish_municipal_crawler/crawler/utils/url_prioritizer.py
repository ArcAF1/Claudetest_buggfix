import requests
from urllib.parse import urljoin, urlparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
import redis
import hashlib
import re
import logging
import aiohttp
from collections import defaultdict
import json
from datetime import datetime, timedelta

class Phase1URLPrioritizer:
    """Phase 1 focused URL prioritizer - targets only food control and building permit hourly rates"""
    
    def __init__(self, redis_client=None, cache_ttl=86400):
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis_client
        self.cache_ttl = cache_ttl
        
        # Phase 1 specific priority patterns - ONLY for the three required data points
        self.priority_patterns = [
            # Food control patterns
            '/livsmedel/taxor/',
            '/livsmedelskontroll/',
            '/miljö-och-hälsoskydd/livsmedel/',
            '/taxor-och-avgifter/livsmedel/',
            '/näringsliv/tillstånd/livsmedel/',
            '/offentlig-kontroll/livsmedel/',
            '/miljo-och-halsa/livsmedel/',
            
            # Building permit patterns
            '/bygglov/taxor/',
            '/plan-och-bygg/taxor/',
            '/taxor-och-avgifter/bygglov/',
            '/bygga-bo-och-miljo/bygglov/',
            '/plan-och-bygglov/',
            
            # General tax/fee patterns that might contain our data
            '/taxor-och-avgifter/',
            '/avgifter/',
            '/priser-och-taxor/',
            '/styrdokument/taxor/',
        ]
        
        # Phase 1 specific keywords for URL content analysis
        self.phase1_keywords = {
            'livsmedel': [
                'livsmedelskontroll', 'livsmedelstillsyn', 'offentlig kontroll',
                'timtaxa livsmedel', 'avgift livsmedel', 'kontrollavgift',
                'förskott', 'efterhand', 'debitering', 'timavgift'
            ],
            'bygglov': [
                'bygglovstaxa', 'plan- och bygglov', 'bygglov avgift',
                'timtaxa bygglov', 'handläggning bygglov', 'byggnadsnämnd',
                'PBL', 'plan- och bygglagen'
            ]
        }
        
        # Document patterns for Phase 1 specific documents
        self.document_patterns = [
            r'(livsmedel).*taxa.*(\d{4})?\.pdf',
            r'(bygglov|plan).*taxa.*(\d{4})?\.pdf',
            r'(avgift|taxa).*livsmedel.*(\d{4})?\.pdf',
            r'(avgift|taxa).*bygg.*(\d{4})?\.pdf',
            r'taxa.*livsmedelskontroll.*\.pdf',
            r'plan.*och.*bygglov.*taxa.*\.pdf',
            # Enhanced patterns for Swedish municipal documents
            r'taxa.*f.*r.*offentlig.*kontroll.*\.pdf',
            r'offentlig.*kontroll.*enligt.*livsmedelslagstiftningen.*\.pdf',
            r'avgifter.*och.*taxor.*(\d{4})?\.pdf',
            r'kommunala.*avgifter.*(\d{4})?\.pdf',
            r'styrdokument.*taxa.*\.pdf',
            r'taxa.*milj.*och.*h.*lsa.*\.pdf',
            r'plan.*och.*bygg.*avgifter.*\.pdf'
        ]
        
        # Search terms for internal site search
        self.search_terms = {
            'livsmedel': [
                'livsmedelskontroll taxa',
                'taxa livsmedel',
                'avgift livsmedelstillsyn',
                'timtaxa livsmedel',
                'offentlig livsmedelskontroll avgift'
            ],
            'bygglov': [
                'bygglovstaxa',
                'plan- och bygglovstaxa',
                'bygglov avgift',
                'avgift bygglov',
                'byggnadsnämndens taxa',
                'taxebestämmelser bygglov'
            ]
        }
        
        # Menu keywords to identify relevant navigation
        self.menu_keywords = [
            'Bygga och bo', 'Bygglov', 'Livsmedel', 'Taxor och avgifter',
            'Avgifter', 'Priser och taxor', 'Företag', 'Miljö och hälsa',
            'Offentlig kontroll', 'Protokoll och beslut', 'Styrdokument'
        ]
    
    async def prioritize_urls(self, base_url, discovered_urls, max_urls=50):
        """Prioritize URLs for Phase 1 specific data extraction"""
        self.logger.info(f"Prioritizing URLs for Phase 1 data from {base_url}")
        
        # Check cache first
        cache_key = f"phase1_urls:{urlparse(base_url).netloc}"
        if self.redis_client:
            cached_urls = self._get_cached_urls(cache_key)
            if cached_urls:
                self.logger.info(f"Using cached Phase 1 URLs for {base_url}")
                return cached_urls[:max_urls]
        
        # Score all URLs for Phase 1 relevance
        scored_urls = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in discovered_urls:
                task = self._score_url_for_phase1(session, url, base_url)
                tasks.append(task)
            
            # Process in batches to avoid overwhelming the server
            batch_size = 10
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i + batch_size]
                results = await asyncio.gather(*batch, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, tuple) and result[1] > 0:
                        scored_urls.append(result)
                
                # Respectful delay between batches
                await asyncio.sleep(1)
        
        # Sort by Phase 1 relevance score
        scored_urls.sort(key=lambda x: x[1], reverse=True)
        
        # Extract top URLs
        prioritized_urls = [url for url, score in scored_urls[:max_urls]]
        
        # Cache results
        if self.redis_client and prioritized_urls:
            self._cache_urls(cache_key, prioritized_urls)
        
        self.logger.info(f"Prioritized {len(prioritized_urls)} URLs for Phase 1 extraction")
        return prioritized_urls
    
    async def _score_url_for_phase1(self, session, url, base_url):
        """Score URL based on Phase 1 relevance (food control and building permit hourly rates)"""
        try:
            score = 0
            url_lower = url.lower()
            
            # High priority: Direct pattern matches
            for pattern in self.priority_patterns:
                if pattern.lower() in url_lower:
                    score += 100
                    break
            
            # Medium priority: Document patterns
            for pattern in self.document_patterns:
                if re.search(pattern, url_lower):
                    score += 80
                    break
            
            # Phase 1 keyword scoring
            for category, keywords in self.phase1_keywords.items():
                for keyword in keywords:
                    if keyword.replace(' ', '-') in url_lower or keyword.replace(' ', '_') in url_lower:
                        score += 60
                        break
            
            # PDF bonus for Phase 1 (many municipalities publish rates in PDFs)
            if url_lower.endswith('.pdf'):
                score += 40
            
            # Check URL content for Phase 1 indicators
            if score > 0:  # Only check content if URL already looks promising
                content_score = await self._check_url_content_for_phase1(session, url)
                score += content_score
            
            return (url, score)
            
        except Exception as e:
            self.logger.debug(f"Error scoring URL {url}: {e}")
            return (url, 0)
    
    async def _check_url_content_for_phase1(self, session, url):
        """Check URL content for Phase 1 specific indicators"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return 0
                
                content = await response.text()
                content_lower = content.lower()
                score = 0
                
                # Look for Phase 1 validation indicators
                livsmedel_indicators = [
                    'livsmedelskontroll', 'offentlig kontroll', 'kontrollavgift',
                    'timtaxa', 'kronor per timme', 'livsmedelslagen',
                    'efterhandsdebitering', 'förskottsdebitering', 'förskott', 'efterhand'
                ]
                
                bygglov_indicators = [
                    'bygglovstaxa', 'plan- och bygglagen', 'pbl', 'bygglov',
                    'handläggningskostnad', 'avgift per timme', 'byggnadsnämnd',
                    'kommunfullmäktige beslutar', 'timtaxa bygglov'
                ]
                
                # Score based on Phase 1 indicators
                for indicator in livsmedel_indicators:
                    if indicator in content_lower:
                        score += 20
                
                for indicator in bygglov_indicators:
                    if indicator in content_lower:
                        score += 20
                
                # Bonus for finding specific rate patterns
                if re.search(r'\d{3,4}\s*kr.*timme', content_lower):
                    score += 30
                
                if re.search(r'timtaxa.*\d{3,4}', content_lower):
                    score += 30
                
                return min(score, 100)  # Cap content score
                
        except Exception as e:
            self.logger.debug(f"Error checking content for {url}: {e}")
            return 0
    
    def generate_phase1_search_urls(self, base_url):
        """Generate search URLs for Phase 1 specific terms"""
        search_urls = []
        
        # Common search URL patterns
        search_patterns = [
            '/sok/',
            '/search/',
            '/hitta/',
            '/?s=',
            '/search?q=',
            '/sok?q='
        ]
        
        for pattern in search_patterns:
            for category, terms in self.search_terms.items():
                for term in terms:
                    search_url = urljoin(base_url, f"{pattern}{term.replace(' ', '+')}")
                    search_urls.append(search_url)
        
        return search_urls
    
    def generate_phase1_discovery_urls(self, base_url):
        """Generate discovery URLs for Phase 1 documents"""
        discovery_urls = []
        
        # Base URL patterns commonly used by municipalities
        base_patterns = [
            '/bygga-bo-och-miljo/',
            '/bygglov/',
            '/livsmedel/',
            '/foretagare/',
            '/taxor-och-avgifter/',
            '/avgifter/',
            '/dokument/',
            '/download/',
            '/styrdokument/',
            '/protokoll/',
            '/kommun-och-politik/beslut/',
            '/miljo-och-halsa/',
            '/naring-och-arbete/',
            '/service-och-tjanster/'
        ]
        
        for pattern in base_patterns:
            discovery_url = urljoin(base_url, pattern)
            discovery_urls.append(discovery_url)
        
        return discovery_urls
    
    def _get_cached_urls(self, cache_key):
        """Get cached URLs from Redis"""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            self.logger.debug(f"Error getting cached URLs: {e}")
        return None
    
    def _cache_urls(self, cache_key, urls):
        """Cache URLs in Redis"""
        try:
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(urls)
            )
        except Exception as e:
            self.logger.debug(f"Error caching URLs: {e}")

# Backward compatibility - keep original class but mark as deprecated
class SwedishURLPrioritizer(Phase1URLPrioritizer):
    """Deprecated: Use Phase1URLPrioritizer for Phase 1 focused extraction"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.warning("SwedishURLPrioritizer is deprecated. Use Phase1URLPrioritizer for Phase 1 focused extraction.")

    def get_priority_urls(self, base_url):
        """Get high-priority URLs to crawl first with parallel checking"""
        priority_urls = []
        
        # Check cache first
        cache_key = f"priority_urls:{self._get_url_hash(base_url)}"
        if self.use_cache:
            cached = self.redis_client.get(cache_key)
            if cached:
                return cached.split(',')
        
        # Test known Swedish municipal patterns in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            test_urls = [urljoin(base_url, pattern) for pattern in self.priority_patterns]
            results = executor.map(self._url_exists, test_urls)
            
            priority_urls = [url for url, exists in zip(test_urls, results) if exists]
        
        # Cache results
        if self.use_cache and priority_urls:
            self.redis_client.setex(cache_key, 86400, ','.join(priority_urls))  # 24h cache
        
        return priority_urls
    
    def score_url(self, url):
        """Score URL based on Swedish municipal patterns"""
        url_lower = url.lower()
        score = 0
        
        # Keyword scoring
        for keyword, weight in self.url_keywords.items():
            if keyword in url_lower:
                score += weight
        
        # Boost for PDF files
        if url_lower.endswith('.pdf'):
            score += 25
        
        # Boost for depth (closer to root = higher priority)
        path_depth = len([p for p in urlparse(url).path.split('/') if p])
        score -= path_depth * 2
        
        # Boost for year indicators (current documents)
        current_year = 2025
        if re.search(rf'{current_year}|{current_year-1}', url):
            score += 10
        
        return max(0, score)
    
    def _url_exists(self, url):
        """Check if URL exists with HEAD request"""
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def _get_url_hash(self, url):
        """Get hash of URL for caching"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get_sitemap_urls(self, base_url):
        """Try to get URLs from sitemap.xml"""
        sitemap_urls = []
        sitemap_url = urljoin(base_url, '/sitemap.xml')
        
        try:
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                # Parse sitemap
                for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                    url_text = url.text
                    if any(keyword in url_text.lower() for keyword in self.url_keywords):
                        sitemap_urls.append(url_text)
        except:
            pass
        
        return sitemap_urls 