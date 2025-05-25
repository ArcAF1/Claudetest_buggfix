import scrapy
from scrapy_playwright.page import PageMethod
import csv
from crawler.extractors.cms_detector import SwedishCMSDetector
from crawler.extractors.enhanced_sitevision_extractor import EnhancedSitevisionExtractor
from crawler.extractors.enhanced_municipio_extractor import EnhancedMunicipioExtractor
from crawler.extractors.enhanced_generic_extractor import EnhancedGenericExtractor
from crawler.extractors.pdf_extractor import SwedishPDFExtractor
from crawler.extractors.bygglov_extractor import BygglovExtractor
from crawler.utils.url_prioritizer import SwedishURLPrioritizer
from crawler.utils.municipality_classifier import MunicipalityClassifier
from datetime import datetime
import asyncio
import logging

class SwedishMunicipalSpider(scrapy.Spider):
    name = 'swedish_municipal_fees'
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'SwedishMunicipalResearch/1.0 (+https://example.com/research)',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'DOWNLOAD_TIMEOUT': 60,
        'JOBDIR': 'crawls/swedish_municipalities',  # Enable resume capability
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_EXPIRATION_SECS': 86400,  # 24 hour cache
        'HTTPCACHE_DIR': 'data/cache',
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'timeout': 30000,
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 30000,
        'ITEM_PIPELINES': {
            'crawler.pipelines.enhanced_validation_pipeline.EnhancedValidationPipeline': 200,
            'crawler.pipelines.duplicate_pipeline.DuplicatesPipeline': 250,
            'crawler.pipelines.data_pipeline.SwedishFeeDataPipeline': 300,
        }
    }
    
    def __init__(self, municipalities_file='data/input/municipalities.csv', *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize enhanced extractors
        self.cms_detector = SwedishCMSDetector()
        self.sitevision_extractor = EnhancedSitevisionExtractor()
        self.municipio_extractor = EnhancedMunicipioExtractor()
        self.generic_extractor = EnhancedGenericExtractor()
        self.pdf_extractor = SwedishPDFExtractor()
        self.bygglov_extractor = BygglovExtractor()
        self.url_prioritizer = SwedishURLPrioritizer()
        self.classifier = MunicipalityClassifier()
        
        # Load municipalities
        self.municipalities = self._load_municipalities(municipalities_file)
        self.start_urls = [muni['url'] for muni in self.municipalities]
        
        # Enhanced tracking
        self.processed_municipalities = set()
        self.total_fees_extracted = 0
        self.start_time = datetime.now()
        self.failed_municipalities = []
        self.extraction_stats = {
            'sitevision': {'pages': 0, 'fees': 0, 'js_used': 0},
            'municipio': {'pages': 0, 'fees': 0, 'ajax_used': 0},
            'generic': {'pages': 0, 'fees': 0, 'strategies_used': 0},
            'pdf': {'processed': 0, 'fees': 0},
            'bygglov': {'processed': 0, 'fees': 0}
        }
        
        # Setup logging
        self.logger = logging.getLogger(self.name)
    
    def _load_municipalities(self, file_path):
        """Load municipalities from CSV file"""
        municipalities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    municipalities.append({
                        'name': row['municipality'],
                        'url': row['url'].rstrip('/'),
                        'org_number': row.get('org_number', ''),
                        'population': int(row.get('population', 0))
                    })
        except Exception as e:
            self.logger.error(f"Failed to load municipalities: {e}")
            raise
        
        self.logger.info(f"Loaded {len(municipalities)} municipalities")
        return municipalities
    
    def start_requests(self):
        """Generate initial requests with Playwright support for JS-heavy sites"""
        for municipality in self.municipalities:
            # Detect if JS rendering needed
            if municipality['name'] in self.processed_municipalities:
                self.logger.info(f"Skipping already processed: {municipality['name']}")
                continue
            
            # Check if municipality might need JS rendering
            js_likely = municipality['population'] > 50000  # Larger cities often have modern sites
            
            if js_likely:
                yield scrapy.Request(
                    municipality['url'],
                    callback=self.parse,
                    meta={
                        'playwright': True,
                        'playwright_include_page': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_load_state', 'networkidle'),
                            PageMethod('wait_for_timeout', 2000),
                        ],
                        'municipality': municipality
                    },
                    errback=self.errback_httpbin
                )
            else:
                yield scrapy.Request(
                    municipality['url'],
                    callback=self.parse,
                    meta={'municipality': municipality},
                    errback=self.errback_httpbin
                )
    
    async def parse(self, response):
        """Main parsing method with enhanced JavaScript support"""
        municipality = response.meta['municipality']
        municipality_name = municipality['name']
        
        # Check if we have Playwright page
        if 'playwright_page' in response.meta:
            page = response.meta['playwright_page']
            # Detect CMS with JavaScript evaluation
            cms_type = await self.cms_detector.detect_cms_with_js(response.url)
            await page.close()
        else:
            cms_type = self.cms_detector.detect_cms(response)
        
        municipality_type = self.classifier.classify_municipality(municipality_name)
        
        self.logger.info(f"Processing {municipality_name} (Type: {municipality_type}, CMS: {cms_type})")
        self.processed_municipalities.add(municipality_name)
        
        # Update crawler settings based on municipality type
        self._update_settings_for_municipality(municipality_type)
        
        # Get priority URLs first
        priority_urls = self.url_prioritizer.get_priority_urls(response.url)
        
        # Also try sitemap
        sitemap_urls = self.url_prioritizer.get_sitemap_urls(response.url)
        priority_urls.extend(sitemap_urls)
        
        # Remove duplicates while preserving order
        priority_urls = list(dict.fromkeys(priority_urls))
        
        if priority_urls:
            self.logger.info(f"Found {len(priority_urls)} priority URLs for {municipality_name}")
            
            for url in priority_urls[:10]:  # Limit per municipality
                cms_config = self.cms_detector.get_cms_config(cms_type)
                
                if cms_config['js_required']:
                    yield scrapy.Request(
                        url,
                        callback=self.parse_fee_page,
                        meta={
                            'playwright': True,
                            'playwright_page_methods': [
                                PageMethod('wait_for_load_state', 'networkidle'),
                            ],
                            'municipality': municipality,
                            'cms_type': cms_type,
                            'municipality_type': municipality_type,
                            'is_priority': True
                        },
                        dont_filter=True
                    )
                else:
                    yield scrapy.Request(
                        url,
                        callback=self.parse_fee_page,
                        meta={
                            'municipality': municipality,
                            'cms_type': cms_type,
                            'municipality_type': municipality_type,
                            'is_priority': True
                        },
                        dont_filter=True
                    )
        else:
            # No priority URLs found, parse main page
            for item in self.parse_fee_page(response):
                yield item
        
        # Also look for additional fee-related links
        additional_links = self._get_additional_fee_links(response, cms_type)
        
        for url in additional_links[:5]:  # Limit to 5 additional links
            yield scrapy.Request(
                url,
                callback=self.parse_fee_page,
                meta={
                    'municipality': municipality,
                    'cms_type': cms_type,
                    'municipality_type': municipality_type,
                    'is_priority': False
                }
            )
    
    async def parse_fee_page(self, response):
        """Enhanced fee page parsing with multiple extraction strategies"""
        municipality = response.meta['municipality']
        cms_type = response.meta['cms_type']
        
        self.logger.info(f"Parsing fee page: {response.url} ({cms_type})")
        
        # Extract fees based on CMS type with enhanced methods
        fees = await self._extract_fees_by_cms_enhanced(response, cms_type)
        
        # Extract PDF links and process them
        pdf_links = self._get_pdf_links_by_cms(response, cms_type)
        
        for pdf_url in pdf_links[:5]:  # Increased PDF limit
            try:
                # Use enhanced PDF extraction
                pdf_fees = self.pdf_extractor.extract_fees_from_pdf_url(pdf_url)
                self.extraction_stats['pdf']['processed'] += 1
                
                # Check if it's a bygglov document for specialized extraction
                if any(keyword in pdf_url.lower() for keyword in ['bygglov', 'byggnadsnämnd', 'pbl']):
                    bygglov_fees = self.bygglov_extractor.extract_bygglov_fees_from_url(pdf_url)
                    pdf_fees.extend(bygglov_fees)
                    self.extraction_stats['bygglov']['processed'] += 1
                    self.extraction_stats['bygglov']['fees'] += len(bygglov_fees)
                
                self.extraction_stats['pdf']['fees'] += len(pdf_fees)
                
                for fee in pdf_fees:
                    fee['municipality'] = municipality['name']
                    fee['municipality_org_number'] = municipality.get('org_number', '')
                    fee['extraction_date'] = datetime.now().isoformat()
                    fee['cms_type'] = cms_type
                    self.total_fees_extracted += 1
                    yield fee
            except Exception as e:
                self.logger.error(f"PDF extraction failed for {pdf_url}: {e}")
        
        # Yield HTML-extracted fees
        for fee in fees:
            fee['municipality'] = municipality['name']
            fee['municipality_org_number'] = municipality.get('org_number', '')
            fee['extraction_date'] = datetime.now().isoformat()
            fee['cms_type'] = cms_type
            self.total_fees_extracted += 1
            yield fee
        
        self.logger.info(f"Extracted {len(fees)} fees from {response.url}")
    
    async def _extract_fees_by_cms_enhanced(self, response, cms_type):
        """Enhanced fee extraction with JavaScript support and multiple strategies"""
        fees = []
        
        try:
            if cms_type == 'sitevision':
                self.extraction_stats['sitevision']['pages'] += 1
                
                # Try enhanced extraction first
                fees = self.sitevision_extractor.extract_fees_from_sitevision(response)
                
                # If few results and JavaScript available, try Playwright extraction
                if len(fees) < 3 and 'playwright_page' in response.meta:
                    try:
                        js_fees = await self.sitevision_extractor.extract_with_playwright(response.url)
                        fees.extend(js_fees)
                        self.extraction_stats['sitevision']['js_used'] += 1
                    except Exception as e:
                        self.logger.debug(f"Playwright extraction failed for SiteVision: {e}")
                
                self.extraction_stats['sitevision']['fees'] += len(fees)
                
            elif cms_type == 'municipio':
                self.extraction_stats['municipio']['pages'] += 1
                
                # Try enhanced extraction first
                fees = self.municipio_extractor.extract_fees_from_municipio(response)
                
                # If few results, try AJAX extraction
                if len(fees) < 3:
                    try:
                        ajax_fees = await self.municipio_extractor.extract_with_ajax(response.url)
                        fees.extend(ajax_fees)
                        self.extraction_stats['municipio']['ajax_used'] += 1
                    except Exception as e:
                        self.logger.debug(f"AJAX extraction failed for Municipio: {e}")
                
                self.extraction_stats['municipio']['fees'] += len(fees)
                
            else:
                self.extraction_stats['generic']['pages'] += 1
                
                # Try enhanced generic extraction
                fees = self.generic_extractor.extract_fees_generic(response)
                
                # If few results, try multiple strategies with Playwright
                if len(fees) < 3:
                    try:
                        strategy_fees = await self.generic_extractor.extract_with_multiple_strategies(response.url)
                        fees.extend(strategy_fees)
                        self.extraction_stats['generic']['strategies_used'] += 1
                    except Exception as e:
                        self.logger.debug(f"Multi-strategy extraction failed: {e}")
                
                self.extraction_stats['generic']['fees'] += len(fees)
        
        except Exception as e:
            self.logger.error(f"Enhanced fee extraction failed for {response.url}: {e}")
        
        return fees
    
    def errback_httpbin(self, failure):
        """Handle failed requests"""
        request = failure.request
        municipality = request.meta.get('municipality', {})
        municipality_name = municipality.get('name', 'Unknown')
        
        self.logger.error(f"Request failed for {municipality_name}: {failure.value}")
        self.failed_municipalities.append({
            'municipality': municipality_name,
            'url': request.url,
            'error': str(failure.value)
        })
    
    def _get_pdf_links_by_cms(self, response, cms_type):
        """Get PDF links based on CMS type"""
        try:
            cms_config = self.cms_detector.get_cms_config(cms_type)
            pdf_selectors = cms_config.get('pdf_selectors', ['a[href$=".pdf"]'])
            
            pdf_links = []
            for selector in pdf_selectors:
                links = response.css(selector + '::attr(href)').getall()
                pdf_links.extend([response.urljoin(link) for link in links])
            
            # Score and sort PDFs by relevance
            scored_links = [(self.url_prioritizer.score_url(link), link) for link in pdf_links]
            scored_links.sort(key=lambda x: x[0], reverse=True)
            
            return [link for score, link in scored_links]
        
        except Exception as e:
            self.logger.error(f"PDF link extraction failed: {e}")
            return []
    
    def _get_additional_fee_links(self, response, cms_type):
        """Get additional fee-related links using enhanced extractors"""
        try:
            if cms_type == 'sitevision':
                return self.sitevision_extractor.get_priority_links_sitevision(response)
            elif cms_type == 'municipio':
                return self.municipio_extractor.get_priority_links_municipio(response)
            else:
                return self.generic_extractor.get_generic_links(response)
        
        except Exception as e:
            self.logger.error(f"Enhanced link extraction failed: {e}")
            return []
    
    def _update_settings_for_municipality(self, municipality_type):
        """Update crawler settings based on municipality size"""
        config = self.classifier.get_crawl_config(municipality_type)
        
        # Update download delay
        self.crawler.settings.set('DOWNLOAD_DELAY', config['download_delay'])
        
        # Log the adjustment
        self.logger.info(f"Adjusted settings for {municipality_type} municipality: "
                        f"delay={config['download_delay']}s")
    
    def closed(self, reason):
        """Log final statistics when spider closes"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        self.logger.info(f"Spider completed. Reason: {reason}")
        self.logger.info(f"Duration: {duration}")
        self.logger.info(f"Total fees extracted: {self.total_fees_extracted}")
        self.logger.info(f"Municipalities processed: {len(self.processed_municipalities)}")
        self.logger.info(f"Failed municipalities: {len(self.failed_municipalities)}")
        
        # Enhanced extraction statistics
        self.logger.info("=== Enhanced Extraction Statistics ===")
        
        for extractor, stats in self.extraction_stats.items():
            if stats.get('pages', 0) > 0 or stats.get('processed', 0) > 0:
                self.logger.info(f"{extractor.upper()}:")
                for key, value in stats.items():
                    self.logger.info(f"  {key}: {value}")
        
        # Calculate efficiency metrics
        if self.total_fees_extracted > 0:
            avg_fees_per_municipality = self.total_fees_extracted / max(1, len(self.processed_municipalities))
            self.logger.info(f"Average fees per municipality: {avg_fees_per_municipality:.1f}")
            
            # CMS-specific efficiency
            for cms in ['sitevision', 'municipio', 'generic']:
                pages = self.extraction_stats[cms]['pages']
                fees = self.extraction_stats[cms]['fees']
                if pages > 0:
                    efficiency = fees / pages
                    self.logger.info(f"{cms.upper()} efficiency: {efficiency:.1f} fees/page")
        
        # Save enhanced statistics
        if self.failed_municipalities:
            import json
            
            # Save failed municipalities
            with open('data/output/failed_municipalities.json', 'w') as f:
                json.dump(self.failed_municipalities, f, indent=2, ensure_ascii=False)
            
            # Save extraction statistics
            enhanced_stats = {
                'crawl_summary': {
                    'total_fees': self.total_fees_extracted,
                    'municipalities_processed': len(self.processed_municipalities),
                    'failed_municipalities': len(self.failed_municipalities),
                    'duration_seconds': duration.total_seconds(),
                    'completion_time': end_time.isoformat()
                },
                'extraction_stats': self.extraction_stats,
                'failed_municipalities': self.failed_municipalities
            }
            
            with open('data/output/enhanced_crawl_stats.json', 'w') as f:
                json.dump(enhanced_stats, f, indent=2, ensure_ascii=False) 