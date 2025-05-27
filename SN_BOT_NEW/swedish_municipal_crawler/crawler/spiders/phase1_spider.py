#!/usr/bin/env python3
"""
Phase 1 Spider - Swedish Municipal Fee Crawler
Focuses ONLY on extracting three specific data points:
1. Timtaxan för livsmedelskontroll (Hourly rate for food control)
2. Debiteringsmodell för livsmedelskontroll (Billing model: prepaid vs post-paid)
3. Timtaxan för bygglov (Hourly rate for building permits)
"""

import scrapy
import logging
import csv
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path
import re
import time
import json

from ..items import Phase1DataItem
from ..extractors.phase1_extractors import Phase1ExtractorManager
from ..extractors.phase1_pdf_extractor import Phase1PDFExtractor
from ..utils.url_prioritizer import Phase1URLPrioritizer
from ..utils.validators import SwedishValidators
from ..ml.page_classifier import PageClassifier

class Phase1Spider(scrapy.Spider):
    """Phase 1 focused spider for Swedish municipal fee extraction"""
    
    name = 'phase1_municipal_fees'
    allowed_domains = []  # Will be populated from municipalities file
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'crawler.pipelines.phase1_enhanced_validation_pipeline.Phase1EnhancedValidationPipeline': 100,
            'crawler.pipelines.phase1_duplicate_pipeline.Phase1DuplicatesPipeline': 200,
            'crawler.pipelines.phase1_data_pipeline.Phase1DataPipeline': 300,
        },
        'DOWNLOAD_DELAY': 5,  # Increased from 3 to 5 seconds for more thorough processing
        'RANDOMIZE_DOWNLOAD_DELAY': 2.0,  # Increased randomization for more natural crawling
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,  # Keep at 1 to be respectful
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 3,  # Increased from 2 to 3
        'AUTOTHROTTLE_MAX_DELAY': 20,  # Increased from 15 to 20
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,  # Keep at 1.0
        'PHASE1_DATA_PIPELINE_SETTINGS': {
            'output_dir': 'data/output/phase1'
        },
        # Enhanced settings for deeper crawling
        'DEPTH_LIMIT': 6,  # Increased from 5 to 6 for deeper exploration
        'DEPTH_PRIORITY': 1,  # Prioritize breadth-first for better discovery
        'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
        # Disable job persistence to avoid queue corruption
        'JOBDIR': None,
    }
    
    def __init__(self, municipalities_file='data/input/municipalities_full.csv', max_municipalities=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize statistics
        self.stats = {
            'municipalities_processed': 0,
            'municipalities_with_data': 0,
            'total_phase1_items': 0,
            'items_with_livsmedel_timtaxa': 0,
            'items_with_debitering_model': 0,
            'items_with_bygglov_timtaxa': 0,
            'complete_items': 0,
            'html_processed': 0,
            'pdf_processed': 0
        }
        
        # Initialize extractors
        self.phase1_extractor = Phase1ExtractorManager()
        self.phase1_pdf_extractor = Phase1PDFExtractor()
        self.page_classifier = PageClassifier()
        
        # Load municipalities
        self.municipalities_file = municipalities_file
        self.max_municipalities = int(max_municipalities) if max_municipalities else None
        self.municipalities = self._load_municipalities()
        
        # Add timeout tracking
        self.start_time = time.time()
        self.max_runtime = 3600  # 1 hour maximum runtime
        
        # Track municipalities with complete data to stop early
        self.municipality_complete_data = set()
        self.municipality_visited_urls = {}

        # Error logging setup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        self.error_log = []
        self.error_log_path = Path('data/output') / f'phase1_errors_{timestamp}.json'
        
        # Set allowed domains from municipalities
        self.allowed_domains = []
        for municipality in self.municipalities:
            domain = urlparse(municipality['url']).netloc
            if domain:
                self.allowed_domains.append(domain)
        
        self.logger.info(f"Loaded {len(self.municipalities)} municipalities for Phase 1 extraction")
        if self.max_municipalities:
            self.logger.info(f"Limited to {self.max_municipalities} municipalities (out of {len(self.municipalities)} available)")
        
        # Initialize Phase 1 components
        self.url_prioritizer = Phase1URLPrioritizer()
        self.validators = SwedishValidators()
    
    def _load_municipalities(self):
        """Load municipalities from CSV file"""
        try:
            municipalities_path = Path(self.municipalities_file)
            if not municipalities_path.exists():
                self.logger.error(f"Municipalities file not found: {self.municipalities_file}")
                return []  # Return empty list instead of None
            
            all_municipalities = []
            with open(municipalities_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Support both old and new column naming conventions
                    municipality_name = row.get('municipality_name') or row.get('municipality')
                    website_url = row.get('website_url') or row.get('url')
                    municipality_code = row.get('municipality_code') or row.get('org_number')
                    
                    if municipality_name and website_url:
                        municipality = {
                            'name': municipality_name.strip(),
                            'url': website_url.strip(),
                            'org_number': municipality_code.strip() if municipality_code else '',
                            'population': row.get('population', '').strip()
                        }
                        all_municipalities.append(municipality)
            
            # Apply max_municipalities limit if specified
            if self.max_municipalities:
                municipalities = all_municipalities[:self.max_municipalities]
                self.logger.info(f"Limited to {self.max_municipalities} municipalities (out of {len(all_municipalities)} available)")
            else:
                municipalities = all_municipalities
            
            self.logger.info(f"Loaded {len(municipalities)} municipalities for Phase 1 extraction")
            return municipalities  # Return the list
            
        except Exception as e:
            self.logger.error(f"Error loading municipalities: {e}")
            return []  # Return empty list on error
    
    def start_requests(self):
        """Generate initial requests using research-based navigation intelligence"""
        self.logger.info(f"Starting research-based crawling for {len(self.municipalities)} municipalities")
        
        for municipality in self.municipalities:
            self.logger.info(f"Creating research-based request for {municipality['name']}: {municipality['url']}")
            
            # Start with main municipality page using navigation intelligence
            yield scrapy.Request(
                url=municipality['url'],
                callback=self.parse_start_url,
                meta={'municipality': municipality},
                errback=self.handle_error,
                dont_filter=True,
                priority=100  # High priority for main pages
            )
    
    def parse_strategic_page(self, response):
        """Parse strategic entry points with focused extraction and enhanced discovery"""
        municipality = response.meta['municipality']
        
        self.logger.info(f"Parsing strategic page for {municipality['name']}: {response.url}")
        
        # Check if this is a PDF
        if response.url.lower().endswith('.pdf') or 'application/pdf' in response.headers.get('content-type', b'').decode():
            yield from self.parse_pdf_page(response)
            return
        
        # Look for direct PDF links with high relevance
        pdf_links = self._extract_relevant_pdf_links(response)
        for pdf_url in pdf_links:
            yield scrapy.Request(
                url=pdf_url,
                callback=self.parse_pdf_page,
                meta={'municipality': municipality},
                priority=150  # Highest priority for relevant PDFs
            )
        
        # Look for structured documents (CSV, XLSX, etc.)
        structured_docs = self._extract_structured_documents(response)
        for doc_url in structured_docs:
            yield scrapy.Request(
                url=doc_url,
                callback=self.parse_structured_document,
                meta={'municipality': municipality},
                priority=140  # High priority for structured data
            )
        
        # Look for document listing pages
        document_pages = self._extract_document_listing_pages(response)
        for doc_url in document_pages:
            municipality_domain = urlparse(municipality['url']).netloc
            if self._is_valid_municipal_url(doc_url, municipality_domain):
                yield scrapy.Request(
                    url=doc_url,
                    callback=self.parse_document_listing,
                    meta={'municipality': municipality},
                    priority=120  # High priority for document listings
                )
        
        # Look for internal search functionality
        search_forms = self._detect_search_functionality(response)
        for search_url in search_forms:
            yield scrapy.Request(
                url=search_url,
                callback=self.parse_search_results,
                meta={'municipality': municipality},
                priority=110  # Medium-high priority for search results
            )
        
        # Extract Phase 1 data from this page
        yield from self.parse_phase1_page(response)
    
    def _detect_search_functionality(self, response):
        """Detect and utilize internal website search functionality"""
        search_urls = []
        
        # Look for search forms
        search_forms = response.css('form')
        for form in search_forms:
            action = form.css('::attr(action)').get()
            method = form.css('::attr(method)').get() or 'GET'
            
            # Look for search-related inputs
            search_inputs = form.css('input[type="search"], input[name*="search"], input[name*="sok"], input[id*="search"]')
            if search_inputs:
                if action:
                    # Construct search URLs for relevant terms
                    search_terms = ['avgift', 'taxa', 'livsmedel', 'bygglov', 'styrdokument']
                    for term in search_terms:
                        if method.upper() == 'GET':
                            search_input_name = search_inputs[0].css('::attr(name)').get() or 'q'
                            search_url = response.urljoin(action) + f'?{search_input_name}={term}'
                            search_urls.append(search_url)
                            self.logger.debug(f"Generated search URL: {search_url}")
        
        # Look for direct search links
        search_links = response.css('a[href*="search"], a[href*="sok"]::attr(href)').getall()
        for link in search_links[:3]:  # Limit to 3 search links
            search_urls.append(response.urljoin(link))
        
        return search_urls[:5]  # Limit to 5 search attempts
    
    def parse_search_results(self, response):
        """Parse search results pages for relevant documents"""
        municipality = response.meta['municipality']
        
        self.logger.info(f"Parsing search results for {municipality['name']}: {response.url}")
        
        # Extract PDFs from search results
        pdf_links = self._extract_relevant_pdf_links(response)
        for pdf_url in pdf_links:
            yield scrapy.Request(
                url=pdf_url,
                callback=self.parse_pdf_page,
                meta={'municipality': municipality},
                priority=130  # High priority for search result PDFs
            )
        
        # Extract structured documents from search results
        structured_docs = self._extract_structured_documents(response)
        for doc_url in structured_docs:
            yield scrapy.Request(
                url=doc_url,
                callback=self.parse_structured_document,
                meta={'municipality': municipality},
                priority=125  # High priority for search result structured docs
            )
    
    def parse_structured_document(self, response):
        """Parse structured documents (CSV, XLSX, etc.) for Phase 1 data"""
        municipality = response.meta['municipality']
        
        self.logger.info(f"Processing structured document for {municipality['name']}: {response.url}")
        
        try:
            # For now, log the discovery - actual parsing would require 
            # specific logic based on document format and structure
            self.logger.info(f"Found structured document: {response.url}")
            
            # Create a basic item to track the discovery
            item = Phase1DataItem()
            item['municipality'] = municipality['name']
            item['municipality_org_number'] = municipality.get('org_number', '')
            item['source_url'] = response.url
            item['source_type'] = 'STRUCTURED'
            item['extraction_date'] = datetime.now().isoformat()
            item['confidence'] = 0.5  # Medium confidence for structured docs
            item['data_completeness'] = 0.0  # Will be updated if data is found
            item['extraction_method'] = 'structured_document'
            item['validation_warnings'] = [f'Structured document found but not yet parsed: {response.url}']
            item['status'] = 'discovered'
            
            yield item
            
        except Exception as e:
            self.logger.error(f"Error processing structured document {response.url}: {e}")
    
    def _extract_structured_documents(self, response):
        """Extract structured documents (CSV, XLSX, XLS) that may contain fee data"""
        structured_links = []
        
        # Look for structured data files
        structured_selectors = [
            'a[href$=".csv"]::attr(href)',
            'a[href$=".xlsx"]::attr(href)', 
            'a[href$=".xls"]::attr(href)',
            'a[href$=".ods"]::attr(href)',  # OpenDocument Spreadsheet
        ]
        
        for selector in structured_selectors:
            links = response.css(selector).getall()
            for link in links:
                link_lower = link.lower()
                # Filter for relevant structured documents
                if any(keyword in link_lower for keyword in ['avgift', 'taxa', 'budget', 'ekonomi', 'kostnad', 'pris']):
                    absolute_url = response.urljoin(link)
                    structured_links.append(absolute_url)
                    self.logger.info(f"Found relevant structured document: {absolute_url}")
        
        return structured_links[:5]  # Limit to 5 most relevant
    
    def _extract_relevant_pdf_links(self, response):
        """Extract PDF links that are highly relevant to Phase 1 data with enhanced filtering"""
        pdf_links = response.css('a[href$=".pdf"]::attr(href)').getall()
        relevant_pdfs = []
        
        # Enhanced high-relevance patterns for Phase 1 data
        high_relevance_patterns = [
            # Tax and fee documents
            r'.*taxa.*livsmedel.*\.pdf',
            r'.*livsmedel.*taxa.*\.pdf',
            r'.*bygglov.*taxa.*\.pdf',
            r'.*taxa.*bygglov.*\.pdf',
            r'.*avgift.*livsmedel.*\.pdf',
            r'.*avgift.*bygglov.*\.pdf',
            r'.*kommunal.*avgift.*\.pdf',
            r'.*debiteringsmodell.*\.pdf',
            r'.*timtaxa.*\.pdf',
            
            # Control and permit documents
            r'.*offentlig.*kontroll.*\.pdf',
            r'.*livsmedelskontroll.*\.pdf',
            r'.*miljöhälsa.*taxa.*\.pdf',
            r'.*plan.*bygg.*avgift.*\.pdf',
            
            # Budget and financial documents (may contain fee schedules)
            r'.*budget.*\.pdf',
            r'.*arsredovisning.*\.pdf',
            r'.*ekonomi.*\.pdf',
            r'.*finansiell.*\.pdf',
            
            # Policy and governance documents (may contain fee structures)
            r'.*styrdokument.*\.pdf',
            r'.*forfattning.*\.pdf',
            r'.*reglemente.*\.pdf',
            r'.*bestämmelse.*\.pdf',
            r'.*föreskrift.*\.pdf',
            
            # General fee and tax documents
            r'.*avgift.*\.pdf',
            r'.*taxa.*\.pdf',
            r'.*gebyr.*\.pdf',
            r'.*kostnad.*\.pdf',
            r'.*pris.*\.pdf',
        ]
        
        for link in pdf_links:
            link_lower = link.lower()
            for pattern in high_relevance_patterns:
                if re.search(pattern, link_lower):
                    absolute_url = response.urljoin(link)
                    relevant_pdfs.append(absolute_url)
                    self.logger.info(f"Found relevant PDF: {absolute_url}")
                    break
        
        return relevant_pdfs[:10]  # Increased from 5 to 10 most relevant
    
    def _extract_document_listing_pages(self, response):
        """Extract links to pages that likely contain document listings with enhanced detection"""
        all_links = response.css('a::attr(href)').getall()
        document_pages = []
        
        # Enhanced patterns for document listing pages
        listing_patterns = [
            # Document repositories
            r'.*dokument.*lista.*',
            r'.*publikation.*lista.*',
            r'.*styrdokument.*',
            r'.*forfattning.*',
            r'.*reglemente.*',
            
            # Financial and budget listings
            r'.*budget.*',
            r'.*ekonomi.*',
            r'.*arsredovisning.*',
            r'.*finansiell.*',
            
            # Fee and tax listings
            r'.*avgift.*lista.*',
            r'.*taxa.*lista.*',
            r'.*avgift.*taxa.*',
            r'.*gebyr.*',
            
            # Administrative listings
            r'.*bestämmelse.*',
            r'.*föreskrift.*',
            r'.*policy.*',
            r'.*riktlinje.*',
            
            # Search and archive pages
            r'.*sok.*dokument.*',
            r'.*arkiv.*',
            r'.*bibliotek.*',
        ]
        
        for link in all_links:
            if link:
                link_lower = link.lower()
                for pattern in listing_patterns:
                    if re.search(pattern, link_lower):
                        absolute_url = response.urljoin(link)
                        document_pages.append(absolute_url)
                        self.logger.debug(f"Found document listing page: {absolute_url}")
                        break
        
        return document_pages[:5]  # Increased from 3 to 5 most relevant
    
    def parse_document_listing(self, response):
        """Parse document listing pages to find relevant PDFs"""
        municipality = response.meta['municipality']
        
        self.logger.info(f"Parsing document listing for {municipality['name']}: {response.url}")
        
        # Extract all PDF links from listing page
        pdf_links = response.css('a[href$=".pdf"]::attr(href)').getall()
        
        # Process all PDFs from listing (these are likely relevant)
        for pdf_link in pdf_links[:10]:  # Limit to 10 PDFs per listing
            pdf_url = response.urljoin(pdf_link)
            yield scrapy.Request(
                url=pdf_url,
                callback=self.parse_pdf_page,
                meta={'municipality': municipality},
                priority=140  # Very high priority for listing PDFs
            )
    
    def parse_start_url(self, response):
        """Parse municipality start page with research-based navigation intelligence"""
        municipality = response.meta.get('municipality')
        if not municipality:
            self.logger.error(f"No municipality data in response meta for {response.url}")
            return

        self.logger.info(f"Starting research-based navigation for {municipality['name']}: {response.url}")
        
        # Initialize visited URLs tracking per municipality
        municipality_key = municipality['name']
        if not hasattr(self, 'municipality_visited_urls'):
            self.municipality_visited_urls = {}
        if municipality_key not in self.municipality_visited_urls:
            self.municipality_visited_urls[municipality_key] = set()
        
        visited_urls = self.municipality_visited_urls[municipality_key]
        visited_urls.add(response.url)
        
        # Check if we already have complete data for this municipality
        if hasattr(self, 'municipality_complete_data'):
            if municipality_key in self.municipality_complete_data:
                self.logger.info(f"✅ Complete data already found for {municipality['name']}, skipping further crawling")
                return
        else:
            self.municipality_complete_data = set()
        
        # Start intelligent navigation from homepage
        yield from self.parse_with_navigation_intelligence(response)
    
    def parse_with_navigation_intelligence(self, response, visited_urls=None):
        """Parse pages using research-based navigation intelligence"""
        municipality = response.meta['municipality']
        municipality_key = municipality['name']
        
        # Check timeout to prevent hanging
        if hasattr(self, 'start_time') and time.time() - self.start_time > self.max_runtime:
            self.logger.warning(f"Maximum runtime exceeded ({self.max_runtime}s), stopping crawler")
            return
        
        # Get municipality-specific visited URLs
        if not hasattr(self, 'municipality_visited_urls'):
            self.municipality_visited_urls = {}
        if municipality_key not in self.municipality_visited_urls:
            self.municipality_visited_urls[municipality_key] = set()
        
        visited_urls = self.municipality_visited_urls[municipality_key]
        
        # Check if we already have complete data for this municipality - STOP CRAWLING
        if hasattr(self, 'municipality_complete_data') and municipality_key in self.municipality_complete_data:
            self.logger.info(f"✅ Complete data already found for {municipality['name']}, stopping all further crawling for this municipality")
            return
        
        self.logger.debug(f"Parsing with navigation intelligence for {municipality['name']}: {response.url}")
        
        # Check if this is a PDF
        if response.url.lower().endswith('.pdf') or 'application/pdf' in response.headers.get('content-type', b'').decode():
            yield from self.parse_pdf_page(response)
            # Check again after PDF processing
            if hasattr(self, 'municipality_complete_data') and municipality_key in self.municipality_complete_data:
                self.logger.info(f"✅ Complete data found in PDF for {municipality['name']}, stopping further crawling")
                return
        
        # Extract Phase 1 data from current HTML page
        yield from self.parse_phase1_page(response)
        
        # Check again after HTML processing - CRITICAL CHECK
        if hasattr(self, 'municipality_complete_data') and municipality_key in self.municipality_complete_data:
            self.logger.info(f"✅ Complete data found for {municipality['name']}, stopping further crawling")
            return
        
        # Limit the number of URLs we process per municipality to prevent hanging
        if len(visited_urls) > 300:  # Increased from 200 to 300 since we're now much more selective
            self.logger.info(f"Reached URL limit for {municipality['name']}, stopping further crawling")
            return
        
        # Extract breadcrumbs to understand current navigation depth
        breadcrumbs = response.css('.breadcrumb a::text, .breadcrumbs a::text, nav a::text').getall()
        current_depth = len(breadcrumbs)
        
        # Filter for relevant links using simple keyword matching
        relevant_keywords = [
            'livsmedel', 'bygglov', 'taxa', 'avgift', 'dokument', 'publikation',
            'styrdokument', 'regelverk', 'företag', 'foretag', 'service', 'tjänster'
        ]
        
        # High priority keywords that are more likely to contain fee information
        high_priority_keywords = [
            'taxa', 'avgift', 'timtaxa', 'debiteringsmodell', 'livsmedelskontroll',
            'bygglovsavgift', 'offentlig-kontroll', 'styrdokument', 'forfattningssamling'
        ]
        
        # Municipal administration areas (most likely to contain fee information)
        admin_keywords = [
            'foretagare', 'foretag', 'naringsliv', 'tillstand', 'anmalan',
            'bygga-bo', 'bygga-och-bo', 'plan-bygg', 'miljo', 'halsa',
            'kommunfakta', 'politik', 'styrdokument', 'forfattning',
            'avgifter', 'taxor', 'ekonomi', 'budget'
        ]
        
        # URLs to completely avoid (tourism, entertainment, etc.)
        avoid_patterns = [
            'visit', 'uppleva', 'evenemang', 'aktivitet', 'simma', 'bada', 'bad',
            'ung-i-', 'ungdom', 'fritid', 'kultur', 'sport', 'idrott', 'bibliotek',
            'museum', 'turism', 'historia', 'sevardhet', 'natur', 'upptack',
            'gruppaktivitet', 'feriearbete', 'lediga-jobb', 'jobba-hos-oss'
        ]
        
        relevant_links = []
        
        for link in response.css('a::attr(href)').getall()[:50]:  # Reduced from 100 to 50 to be more selective
            if not link:
                continue
                
            absolute_url = response.urljoin(link)
            
            # Skip if already visited
            if absolute_url in visited_urls:
                continue
                
            # Skip irrelevant URLs (expanded list)
            if any(skip in absolute_url.lower() for skip in [
                'facebook', 'twitter', 'instagram', 'youtube', 'linkedin',
                'kontakt', 'nyheter', 'kalender', 'om-oss', 'historia'
            ]):
                continue
            
            # Skip tourism and entertainment content
            if any(avoid in absolute_url.lower() for avoid in avoid_patterns):
                continue
            
            # Validate URL
            municipality_domain = urlparse(municipality['url']).netloc
            if not self._is_valid_municipal_url(absolute_url, municipality_domain):
                continue
            
            # Check for relevant keywords or PDF files
            link_lower = link.lower()
            
            # Prioritize PDFs and high-priority keywords
            is_high_priority = (link_lower.endswith('.pdf') or 
                              any(keyword in link_lower for keyword in high_priority_keywords))
            
            # Check for municipal administration areas
            is_admin_area = any(keyword in link_lower for keyword in admin_keywords)
            
            # Only follow relevant municipal administration links
            is_relevant = (any(keyword in link_lower for keyword in relevant_keywords) or 
                          is_admin_area or
                          current_depth < 3)  # Increased from 2 to 3 for deeper exploration
            
            if is_high_priority or is_relevant:
                # Add high priority items first
                if is_high_priority:
                    relevant_links.insert(0, absolute_url)  # Add to front of list
                elif is_admin_area:
                    # Add admin areas after PDFs but before general links
                    pdf_count = len([x for x in relevant_links if x.endswith('.pdf')])
                    relevant_links.insert(pdf_count, absolute_url)
                else:
                    relevant_links.append(absolute_url)
                
            # Limit to 10 relevant links per page for more focused crawling
            if len(relevant_links) >= 10:
                break
        
        # Process relevant links
        for url in relevant_links:
            visited_urls.add(url)
            yield scrapy.Request(
                url=url,
                callback=self.parse_with_navigation_intelligence,
                meta={'municipality': municipality},
                errback=self.handle_error,
                dont_filter=True
            )
    
    def parse_municipality_page(self, response):
        """Parse main municipality page and discover Phase 1 relevant URLs"""
        municipality = response.meta['municipality']
        self.stats['municipalities_processed'] += 1
        self.logger.info(f"Processing municipality: {municipality['name']} ({self.stats['municipalities_processed']}/{len(self.municipalities)})")
        
        # Extract all links from the page
        all_links = response.css('a::attr(href)').getall()
        absolute_links = [urljoin(response.url, link) for link in all_links if link]
        
        # Combine with discovery and search URLs
        discovery_urls = response.meta.get('discovery_urls', [])
        search_urls = response.meta.get('search_urls', [])
        all_urls = list(set(absolute_links + discovery_urls + search_urls))
        
        # Prioritize URLs for Phase 1 relevance
        # Use manual filtering to avoid async/event loop conflicts
        prioritized_urls = self._manual_url_filter(all_urls)[:30]
        
        self.logger.info(f"Found {len(prioritized_urls)} prioritized URLs for {municipality['name']}")
        
        # Process prioritized URLs
        for url in prioritized_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_phase1_page,
                meta={'municipality': municipality},
                errback=self.handle_error
            )
    
    def _manual_url_filter(self, urls):
        """Enhanced manual URL filtering for Phase 1 relevance based on learnings"""
        # Phase 1 specific keywords (Swedish municipal terminology) - enhanced based on successful discoveries
        phase1_keywords = [
            # Food control related (learned from successful extractions)
            'livsmedel', 'livsmedelskontroll', 'livsmedelstillsyn', 'miljöhälsa',
            'hälsoskydd', 'miljö', 'miljöavgift', 'miljötaxa',
            'foderlagstiftningen', 'kontrollmyndighet', 'offentlig-kontroll',
            
            # Building permit related (learned from municipal patterns)
            'bygglov', 'byggnadslov', 'plan-och-bygg', 'planochbygg', 'pob',
            'byggnadsnämnd', 'byggnämnd', 'byggavgift', 'byggtaxa',
            
            # General fee/tax related (core municipal terminology)
            'taxa', 'avgift', 'avgifter', 'taxor', 'timtaxa', 'timavgift',
            'debiteringsmodell', 'förskott', 'efterhand', 'kommunal-avgift',
            
            # Document types and navigation (learned from successful document discoveries)
            'styrdokument', 'reglemente', 'föreskrift', 'bestämmelse',
            'prislista', 'taxetabell', 'publikationer', 'dokument',
            'regelverk', 'bestämmelser', 'forfattningssamling',
            
            # Municipal navigation terms (learned from successful site structures)
            'service', 'tjänster', 'företag', 'foretag', 'näringsidkare', 'verksamhetsutövare',
            'verksamhet', 'tillstånd', 'tillstand', 'kontroll', 'kommun', 'politik',
            'kommunfakta', 'ekonomi', 'budget', 'arsredovisning'
        ]
        
        # High priority patterns (learned from successful data extractions)
        high_priority_patterns = [
            'livsmedelstaxa', 'livsmedelskontroll', 'bygglovstaxa', 'bygglovsavgift',
            'miljöhälsotaxa', 'plan-och-byggtaxa', 'timtaxa', 'debiteringsmodell',
            'offentlig-kontroll', 'foderlagstiftningen', 'kontrollmyndighet',
            'forfattningssamling', 'styrande-dokument', 'avgifter-och-taxor'
        ]
        
        # Navigation patterns that lead to documents (learned from successful crawls)
        navigation_patterns = [
            'publikationer', 'styrdokument', 'dokument', 'regelverk',
            'kommun-och-politik', 'tjänster', 'service', 'företag', 'foretag',
            'forfattningssamling', 'styrande-dokument', 'kommunfakta',
            'ekonomi', 'budget', 'arsredovisning', 'analys-och-statistik'
        ]
        
        # Document repository indicators (learned from successful document discoveries)
        document_indicators = [
            'publikationer', 'styrdokument', 'dokument', 'regelverk',
            'forfattningssamling', 'styrande-dokument', 'bestämmelser',
            'föreskrifter', 'policy', 'riktlinjer'
        ]
        
        # Score URLs based on relevance
        scored_urls = []
        
        for url in urls:
            url_lower = url.lower()
            score = 0
            
            # High priority patterns get highest scores (learned from successful extractions)
            for pattern in high_priority_patterns:
                if pattern in url_lower:
                    score += 15
            
            # Navigation patterns get medium scores (learned successful navigation paths)
            for pattern in navigation_patterns:
                if pattern in url_lower:
                    score += 8
            
            # Document indicators get good scores (learned from document discoveries)
            for indicator in document_indicators:
                if indicator in url_lower:
                    score += 10
            
            # Regular keywords get base scores
            for keyword in phase1_keywords:
                if keyword in url_lower:
                    score += 2
            
            # PDF files are valuable for municipal data (learned from successful extractions)
            if url_lower.endswith('.pdf'):
                score += 12
            
            # Structured documents are valuable (learned from municipal data patterns)
            if any(url_lower.endswith(ext) for ext in ['.xlsx', '.xls', '.csv', '.ods']):
                score += 8
            
            # Prefer pages with multiple relevant terms (learned pattern)
            keyword_count = sum(1 for keyword in phase1_keywords if keyword in url_lower)
            if keyword_count > 1:
                score += keyword_count * 3
            
            # Boost URLs that contain "taxa" + another relevant term (learned successful pattern)
            if 'taxa' in url_lower:
                for keyword in ['livsmedel', 'bygglov', 'offentlig', 'kontroll', 'avgift']:
                    if keyword in url_lower:
                        score += 5
                        break
            
            # Boost URLs with successful path patterns (learned from Ale/Alingsås success)
            successful_path_patterns = [
                'forfattningssamling', 'styrande-dokument', 'kommunfakta',
                'ekonomi', 'budget', 'arsredovisning', 'analys-och-statistik'
            ]
            for pattern in successful_path_patterns:
                if pattern in url_lower:
                    score += 6
            
            # Avoid clearly irrelevant sections (learned from crawling experience)
            irrelevant_terms = [
                'nyheter', 'kalender', 'kontakt', 'om-oss', 'historia', 
                'evenemang', 'jobb', 'karriär', 'press', 'media',
                'facebook', 'twitter', 'instagram', 'youtube'
            ]
            if any(term in url_lower for term in irrelevant_terms):
                score -= 8
            
            # Boost deeper URLs that might contain specific content (learned pattern)
            url_depth = url.count('/')
            if url_depth > 4:  # URLs with more path segments often have specific documents
                score += 2
            
            if score > 0:
                scored_urls.append((url, score))
        
        # Sort by score (highest first) and return URLs
        scored_urls.sort(key=lambda x: x[1], reverse=True)
        return [url for url, score in scored_urls]
    
    def parse_phase1_page(self, response):
        """Extract Phase 1 data from HTML pages with proper content type handling"""
        municipality = response.meta.get('municipality')
        if not municipality:
            return

        municipality_key = municipality['name']
        
        # Check if we already have complete data for this municipality
        if hasattr(self, 'municipality_complete_data') and municipality_key in self.municipality_complete_data:
            self.logger.info(f"✅ Skipping extraction for {municipality['name']} - already complete")
            return

        self.logger.debug(f"Extracting Phase 1 data from {response.url}")
        
        # Check content type and route appropriately
        content_type = response.headers.get('content-type', b'').decode().lower()
        
        # Handle PDF content
        if 'application/pdf' in content_type or response.url.lower().endswith('.pdf'):
            self.logger.debug(f"Routing PDF to PDF parser: {response.url}")
            yield from self.parse_pdf_page(response)
            return
        
        # Handle non-HTML content
        if not ('text/html' in content_type or 'text/plain' in content_type):
            self.logger.debug(f"Skipping non-HTML content: {content_type} for {response.url}")
            return
        
        # Extract clean text from HTML
        try:
            # Method 1: Try to extract clean text using CSS selectors
            try:
                # Extract text from main content areas, avoiding navigation and footer
                text_elements = response.css('main *::text, article *::text, .content *::text, #content *::text, .main *::text').getall()
                if not text_elements:
                    # Fallback: extract from body, excluding script and style
                    text_elements = response.css('body *:not(script):not(style)::text').getall()
                if not text_elements:
                    # Final fallback: extract all text
                    text_elements = response.css('*::text').getall()
                
                # Clean and join text
                clean_text = ' '.join([text.strip() for text in text_elements if text.strip()])
                
            except Exception as css_error:
                self.logger.debug(f"CSS text extraction failed for {response.url}: {css_error}")
                # Fallback to response.text with HTML tag removal
                import re
                clean_text = re.sub(r'<[^>]+>', ' ', response.text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            # Validate extracted text
            if not clean_text or len(clean_text) < 50:
                self.logger.debug(f"Insufficient text content in {response.url} (length: {len(clean_text)})")
                return
            
            # Log text sample for debugging
            self.logger.debug(f"Extracted {len(clean_text)} characters from {response.url}")
            if len(clean_text) > 200:
                self.logger.debug(f"Text sample: {clean_text[:200]}...")

            # Use ML classifier to skip irrelevant pages
            if not self.page_classifier.is_relevant(clean_text):
                self.logger.debug(f"Page not classified as relevant: {response.url}")
                return

            # Use the Phase 1 extractor manager
            extracted_data = self.phase1_extractor.extract_all_phase1_data(clean_text, response.url)
            
            # Check if any data was found
            if extracted_data and any(extracted_data.get(field) for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov']):
                # Add municipality information
                extracted_data.update({
                    'municipality': municipality['name'],
                    'municipality_org_number': municipality.get('org_number', ''),
                    'source_url': response.url,
                    'source_type': 'HTML'
                })
                
                self.logger.info(f"✅ Found Phase 1 data for {municipality['name']} from HTML: {response.url}")
                
                # Log what was found
                found_fields = []
                if extracted_data.get('timtaxa_livsmedel'):
                    found_fields.append(f"livsmedel_timtaxa: {extracted_data['timtaxa_livsmedel']}")
                if extracted_data.get('debitering_livsmedel'):
                    found_fields.append(f"debitering: {extracted_data['debitering_livsmedel']}")
                if extracted_data.get('timtaxa_bygglov'):
                    found_fields.append(f"bygglov_timtaxa: {extracted_data['timtaxa_bygglov']}")
                
                self.logger.info(f"Found fields: {', '.join(found_fields)}")
                
                # Check if we have complete data (all 3 fields)
                fields_found = sum(1 for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov'] 
                                 if extracted_data.get(field))
                
                if fields_found >= 2:  # Consider 2/3 fields as "complete enough"
                    if not hasattr(self, 'municipality_complete_data'):
                        self.municipality_complete_data = set()
                    self.municipality_complete_data.add(municipality_key)
                    self.logger.info(f"🎯 Marking {municipality['name']} as complete ({fields_found}/3 fields found) - stopping further crawling for this municipality")
                
                yield extracted_data
            else:
                # Log why no data was found
                confidence = extracted_data.get('confidence', 0) if extracted_data else 0
                completeness = extracted_data.get('data_completeness', 0) if extracted_data else 0
                self.logger.debug(f"No Phase 1 data found in {response.url} (confidence: {confidence:.2f}, completeness: {completeness:.1%})")
                
        except Exception as e:
            self.logger.error(f"Error extracting Phase 1 data from {response.url}: {e}")
            # Continue processing other pages even if one fails
    
    def parse_pdf_page(self, response):
        """Parse PDF for Phase 1 data"""
        municipality = response.meta['municipality']
        municipality_key = municipality['name']
        
        # Check if we already have complete data for this municipality
        if hasattr(self, 'municipality_complete_data') and municipality_key in self.municipality_complete_data:
            self.logger.info(f"✅ Complete data already found for {municipality['name']}, skipping PDF processing")
            return
        
        self.stats['pdf_processed'] += 1
        
        try:
            # Save PDF temporarily
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(response.body)
                tmp_file_path = tmp_file.name
            
            # Check if PDF is relevant for Phase 1
            if not self.phase1_pdf_extractor.is_phase1_relevant_pdf(tmp_file_path):
                self.logger.debug(f"PDF not relevant for Phase 1: {response.url}")
                return
            
            # Extract Phase 1 data from PDF
            phase1_data = self.phase1_pdf_extractor.extract_phase1_from_pdf(tmp_file_path, response.url)
            
            if self._has_phase1_data(phase1_data):
                # Create Phase 1 item
                item = Phase1DataItem()
                
                # Fill basic information
                item['municipality'] = municipality['name']
                item['municipality_org_number'] = municipality.get('org_number', '')
                item['source_url'] = response.url
                item['source_type'] = 'PDF'
                item['extraction_date'] = datetime.now().isoformat()
                
                # Fill Phase 1 data
                if phase1_data.get('timtaxa_livsmedel'):
                    item['timtaxa_livsmedel'] = phase1_data['timtaxa_livsmedel']
                    self.stats['items_with_livsmedel_timtaxa'] += 1
                
                if phase1_data.get('debitering_livsmedel'):
                    item['debitering_livsmedel'] = phase1_data['debitering_livsmedel']
                    self.stats['items_with_debitering_model'] += 1
                
                if phase1_data.get('timtaxa_bygglov'):
                    item['timtaxa_bygglov'] = phase1_data['timtaxa_bygglov']
                    self.stats['items_with_bygglov_timtaxa'] += 1
                
                # Fill metadata
                item['confidence'] = phase1_data.get('confidence', 0)
                item['data_completeness'] = phase1_data.get('data_completeness', 0)
                item['extraction_method'] = phase1_data.get('extraction_method', 'phase1_pdf')
                item['validation_warnings'] = phase1_data.get('validation_warnings', [])
                
                # Check if complete and mark municipality as complete
                fields_found = sum(1 for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov'] 
                                 if item.get(field))
                
                if self._is_complete_item(item):
                    self.stats['complete_items'] += 1
                    item['status'] = 'complete'
                else:
                    item['status'] = 'partial'
                
                # Mark municipality as complete if we have enough data
                if fields_found >= 2:  # Consider 2/3 fields as "complete enough"
                    if not hasattr(self, 'municipality_complete_data'):
                        self.municipality_complete_data = set()
                    self.municipality_complete_data.add(municipality_key)
                    self.logger.info(f"🎯 Marking {municipality['name']} as complete from PDF ({fields_found}/3 fields found) - stopping further crawling")
                
                # Track municipality with data
                if not hasattr(self, '_municipalities_with_data'):
                    self._municipalities_with_data = set()
                if municipality['name'] not in self._municipalities_with_data:
                    self._municipalities_with_data.add(municipality['name'])
                    self.stats['municipalities_with_data'] += 1
                
                self.stats['total_phase1_items'] += 1
                
                self.logger.info(f"Found Phase 1 data in PDF for {municipality['name']}: "
                               f"completeness={item['data_completeness']:.1%}, "
                               f"confidence={item['confidence']:.2f}, "
                               f"status={item['status']}")
                
                yield item
            
            # Cleanup
            import os
            os.unlink(tmp_file_path)
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {response.url}: {e}")
    
    def _has_phase1_data(self, data):
        """Check if extracted data contains any Phase 1 fields"""
        return any(data.get(field) for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov'])
    
    def _is_complete_item(self, item):
        """Check if item has all three Phase 1 fields"""
        return all(item.get(field) for field in ['timtaxa_livsmedel', 'debitering_livsmedel', 'timtaxa_bygglov'])
    
    def handle_error(self, failure):
        """Enhanced error handling with detailed logging"""
        request = failure.request
        municipality = request.meta.get('municipality', {})
        municipality_name = municipality.get('name', 'Unknown')
        
        # Log different types of errors with context
        if failure.check(scrapy.spidermiddlewares.httperror.HttpError):
            response = failure.value.response
            self.logger.error(f"HTTP Error {response.status} for {municipality_name}: {request.url}")
            
            # Log specific error details based on status code
            if response.status == 404:
                self.logger.info(f"Strategic URL not found (404) for {municipality_name}: {request.url}")
            elif response.status == 403:
                self.logger.warning(f"Access forbidden (403) for {municipality_name}: {request.url}")
            elif response.status == 500:
                self.logger.error(f"Server error (500) for {municipality_name}: {request.url}")
            else:
                self.logger.error(f"Unexpected HTTP status {response.status} for {municipality_name}: {request.url}")
                
        elif failure.check(scrapy.exceptions.DNSLookupError):
            self.logger.error(f"DNS lookup failed for {municipality_name}: {request.url}")
            
        elif failure.check(scrapy.exceptions.TimeoutError):
            self.logger.warning(f"Request timeout for {municipality_name}: {request.url}")
            
        elif failure.check(scrapy.exceptions.ConnectionRefusedError):
            self.logger.error(f"Connection refused for {municipality_name}: {request.url}")
            
        else:
            self.logger.error(f"Unknown error for {municipality_name}: {request.url} - {failure.value}")
        
        # Track error statistics
        if not hasattr(self, 'error_stats'):
            self.error_stats = {}
        
        error_type = failure.value.__class__.__name__
        if error_type not in self.error_stats:
            self.error_stats[error_type] = 0
        self.error_stats[error_type] += 1

        # Store detailed error for later review
        self.error_log.append({
            'municipality': municipality_name,
            'url': request.url,
            'error': failure.value.__class__.__name__,
        })
    
    def closed(self, reason):
        """Log final statistics when spider closes with enhanced error reporting"""
        self.logger.info("=== Phase 1 Spider Final Statistics ===")
        self.logger.info(f"Municipalities processed: {self.stats['municipalities_processed']}")
        self.logger.info(f"Municipalities with Phase 1 data: {self.stats['municipalities_with_data']}")
        self.logger.info(f"Total Phase 1 items found: {self.stats['total_phase1_items']}")
        self.logger.info(f"Items with food control hourly rate: {self.stats['items_with_livsmedel_timtaxa']}")
        self.logger.info(f"Items with billing model: {self.stats['items_with_debitering_model']}")
        self.logger.info(f"Items with building permit hourly rate: {self.stats['items_with_bygglov_timtaxa']}")
        self.logger.info(f"Complete items (all 3 fields): {self.stats['complete_items']}")
        self.logger.info(f"HTML pages processed: {self.stats['html_processed']}")
        self.logger.info(f"PDF documents processed: {self.stats['pdf_processed']}")
        
        # Log error statistics
        if hasattr(self, 'error_stats') and self.error_stats:
            self.logger.info("=== Error Statistics ===")
            for error_type, count in self.error_stats.items():
                self.logger.info(f"{error_type}: {count}")
        
        if self.stats['total_phase1_items'] > 0:
            success_rate = (self.stats['complete_items'] / self.stats['total_phase1_items']) * 100
            self.logger.info(f"Phase 1 success rate: {success_rate:.1f}% (complete items)")

        # Write error log if any errors were recorded
        if self.error_log:
            try:
                with open(self.error_log_path, 'w', encoding='utf-8') as f:
                    json.dump(self.error_log, f, ensure_ascii=False, indent=2)
                self.logger.info(f"Detailed errors written to {self.error_log_path}")
            except Exception as e:
                self.logger.error(f"Failed to write error log: {e}")

        self.logger.info(f"Spider closed: {reason}")

    def _is_valid_municipal_url(self, url, base_domain):
        """Check if URL is valid for municipal crawling"""
        if not url:
            return False
        
        # Skip mailto links
        if url.startswith('mailto:'):
            return False
        
        # Skip javascript links
        if url.startswith('javascript:'):
            return False
        
        # Skip tel links
        if url.startswith('tel:'):
            return False
        
        # Skip anchor links
        if url.startswith('#'):
            return False
        
        # Parse URL to check domain
        try:
            parsed = urlparse(url)
            url_domain = parsed.netloc.lower()
            
            # Skip if no domain
            if not url_domain:
                return False
            
            # Allow same domain
            if url_domain == base_domain.lower():
                return True
            
            # Allow subdomains of the municipality
            if url_domain.endswith('.' + base_domain.lower()):
                return True
            
            # Skip external domains we don't want to follow
            external_domains_to_skip = [
                'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
                'youtube.com', 'google.com', 'translate.google.com',
                'mynewsdesk.com', 'skr.se', 'flexiteext.',
                'eservice.', 'e-service.', 'webapps.',
                'forms.', 'form.', 'survey.'
            ]
            
            for skip_domain in external_domains_to_skip:
                if skip_domain in url_domain:
                    return False
            
            # Allow other Swedish municipal domains (.se domains)
            if url_domain.endswith('.se'):
                # But skip if it's clearly not a municipal site
                non_municipal_keywords = [
                    'facebook', 'twitter', 'linkedin', 'instagram', 'youtube',
                    'google', 'microsoft', 'apple', 'amazon'
                ]
                if any(keyword in url_domain for keyword in non_municipal_keywords):
                    return False
                return True
            
            # Skip all other external domains
            return False
            
        except Exception as e:
            self.logger.debug(f"Error parsing URL {url}: {e}")
            return False 