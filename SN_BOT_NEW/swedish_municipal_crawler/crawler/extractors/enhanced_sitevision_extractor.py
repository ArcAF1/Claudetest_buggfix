import re
import logging
import asyncio
from datetime import datetime
from .sitevision_extractor import SitevisionExtractor
from ..utils.validators import SwedishValidators

class EnhancedSitevisionExtractor(SitevisionExtractor):
    """Enhanced Sitevision extractor with JavaScript support and validation"""
    
    def __init__(self):
        super().__init__()
        self.validators = SwedishValidators()
        
        # Enhanced Sitevision-specific selectors
        self.sitevision_selectors = {
            'content_areas': [
                '.sv-portlet',
                '.sv-text-portlet', 
                '.sv-article-portlet',
                '.sv-content-portlet',
                '.sv-layout-portlet',
                '.sv-page-content',
                '.sv-main-content'
            ],
            'fee_tables': [
                '.sv-table',
                '.sv-data-table',
                'table.sv-styled',
                '.sv-portlet table'
            ],
            'navigation': [
                '.sv-navigation',
                '.sv-menu',
                '.sv-breadcrumb'
            ]
        }
        
        # Enhanced Swedish fee patterns
        self.fee_patterns = [
            # Standard format: "1 250 kr" or "1 250,50 kr"
            r'(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr(?:/(\w+))?',
            # With kronor: "1 250 kronor"
            r'(\d{1,3}(?:\s\d{3})*)\s*kronor',
            # SEK format: "SEK 1 250,50"
            r'SEK\s*(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)/gi',
            # Alternative format: "1.250,50 kr"
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?)\s*kr',
            # Format with colon: "Avgift: 1 250 kr"
            r'[Aa]vgift:?\s*(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr',
            # Format with equals: "Taxa = 1 250 kr"
            r'[Tt]axa\s*=\s*(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr'
        ]
        
        # Service keywords for better context extraction
        self.service_keywords = [
            'avgift', 'taxa', 'kostnad', 'pris', 'handläggning', 'prövning',
            'ansökan', 'tillsyn', 'kontroll', 'besiktning', 'granskning',
            'bygglov', 'miljötillstånd', 'serveringstillstånd', 'näringstillstånd'
        ]
    
    async def extract_with_playwright(self, url):
        """Extract fees using Playwright for JavaScript-heavy pages"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                page = await browser.new_page()
                
                # Set user agent
                await page.set_extra_http_headers({
                    'User-Agent': 'SwedishMunicipalResearch/1.0 (+https://example.com/research)'
                })
                
                try:
                    # Navigate and wait for content
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    
                    # Wait for Sitevision portlets to load
                    try:
                        await page.wait_for_selector('.sv-portlet', timeout=5000)
                    except:
                        # Fallback if no portlets found
                        await page.wait_for_timeout(2000)
                    
                    # Extract fee information using JavaScript
                    fees_data = await page.evaluate('''
                        () => {
                            const fees = [];
                            const selectors = [
                                '.sv-portlet', '.sv-text-portlet', '.sv-article-portlet',
                                '.sv-content-portlet', '.sv-layout-portlet', '.sv-page-content'
                            ];
                            
                            selectors.forEach(selector => {
                                const elements = document.querySelectorAll(selector);
                                
                                elements.forEach(element => {
                                    const text = element.innerText || element.textContent || '';
                                    
                                    // Swedish currency patterns
                                    const patterns = [
                                        /(\\d{1,3}(?:\\s\\d{3})*(?:,\\d{1,2})?)\\s*kr(?:\\/(\\w+))?/gi,
                                        /(\\d{1,3}(?:\\s\\d{3})*)\\s*kronor/gi,
                                        /SEK\\s*(\\d{1,3}(?:\\s\\d{3})*(?:,\\d{1,2})?)/gi,
                                        /(\\d{1,3}(?:\\.\\d{3})*(?:,\\d{1,2})?)\\s*kr/gi
                                    ];
                                    
                                    patterns.forEach(pattern => {
                                        let match;
                                        while ((match = pattern.exec(text)) !== null) {
                                            // Get context around the match
                                            const index = match.index;
                                            const start = Math.max(0, index - 150);
                                            const end = Math.min(text.length, index + 150);
                                            const context = text.substring(start, end).trim();
                                            
                                            // Check if context contains service keywords
                                            const serviceKeywords = [
                                                'avgift', 'taxa', 'kostnad', 'pris', 'handläggning',
                                                'prövning', 'ansökan', 'tillsyn', 'kontroll'
                                            ];
                                            
                                            const hasServiceKeyword = serviceKeywords.some(keyword => 
                                                context.toLowerCase().includes(keyword)
                                            );
                                            
                                            if (hasServiceKeyword) {
                                                fees.push({
                                                    amount_text: match[0],
                                                    amount_value: match[1],
                                                    unit: match[2] || '',
                                                    context: context,
                                                    element_class: element.className,
                                                    element_tag: element.tagName
                                                });
                                            }
                                        }
                                    });
                                });
                            });
                            
                            // Also extract table data
                            const tables = document.querySelectorAll('table, .sv-table, .sv-data-table');
                            tables.forEach(table => {
                                const rows = table.querySelectorAll('tr');
                                rows.forEach(row => {
                                    const cells = row.querySelectorAll('td, th');
                                    if (cells.length >= 2) {
                                        const rowText = Array.from(cells).map(cell => cell.innerText).join(' | ');
                                        
                                        const match = rowText.match(/(\\d{1,3}(?:\\s\\d{3})*(?:,\\d{1,2})?)\\s*kr/);
                                        if (match) {
                                            fees.push({
                                                amount_text: match[0],
                                                amount_value: match[1],
                                                context: rowText,
                                                element_class: 'table-row',
                                                element_tag: 'TR'
                                            });
                                        }
                                    }
                                });
                            });
                            
                            return fees;
                        }
                    ''')
                    
                    await browser.close()
                    
                    # Process extracted fees
                    processed_fees = []
                    for fee_data in fees_data:
                        processed_fee = self._process_playwright_fee(fee_data, url)
                        if processed_fee and self._validate_fee(processed_fee):
                            processed_fees.append(processed_fee)
                    
                    return self._deduplicate_fees(processed_fees)
                    
                except Exception as e:
                    self.logger.error(f"Playwright page processing failed: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except ImportError:
            self.logger.error("Playwright not available for JavaScript extraction")
            return []
        except Exception as e:
            self.logger.error(f"Playwright extraction failed: {e}")
            return []
    
    def extract_fees_from_sitevision(self, response):
        """Enhanced extraction from SiteVision-based sites"""
        fees = []
        
        try:
            # Extract from content areas
            for selector in self.sitevision_selectors['content_areas']:
                containers = response.css(selector)
                for container in containers:
                    container_fees = self._extract_from_container(container, response.url)
                    fees.extend(container_fees)
            
            # Extract from tables
            for selector in self.sitevision_selectors['fee_tables']:
                tables = response.css(selector)
                for table in tables:
                    table_fees = self._extract_from_table(table, response.url)
                    fees.extend(table_fees)
            
            # Validate and deduplicate
            validated_fees = [fee for fee in fees if self._validate_fee(fee)]
            return self._deduplicate_fees(validated_fees)
        
        except Exception as e:
            self.logger.error(f"Enhanced SiteVision extraction failed: {e}")
            return []
    
    def _extract_from_container(self, container, source_url):
        """Extract fees from a content container"""
        fees = []
        text_content = ' '.join(container.css('::text').getall()).strip()
        
        if not text_content or len(text_content) < 10:
            return fees
        
        # Apply enhanced patterns
        for pattern in self.fee_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                # Extract context around the match
                start = max(0, match.start() - 100)
                end = min(len(text_content), match.end() + 100)
                context = text_content[start:end].strip()
                
                # Check if context contains service keywords
                if any(keyword in context.lower() for keyword in self.service_keywords):
                    amount = self._parse_swedish_currency(match.group(1))
                    
                    if amount and 50 <= amount <= 100000:  # Reasonable fee range
                        fee = {
                            'fee_name': self._extract_service_name(context, match.group(0)),
                            'amount': amount,
                            'currency': 'SEK',
                            'unit': match.group(2) if match.lastindex >= 2 else '',
                            'category': self._categorize_service(context),
                            'source_url': source_url,
                            'source_type': 'HTML',
                            'extraction_method': 'sitevision_enhanced',
                            'confidence': self._calculate_confidence(context, match.group(0)),
                            'description': context[:200],
                            'extraction_date': datetime.now().isoformat()
                        }
                        fees.append(fee)
        
        return fees
    
    def _extract_from_table(self, table, source_url):
        """Extract fees from table structures"""
        fees = []
        
        try:
            rows = table.css('tr')
            headers = []
            
            # Get headers
            header_row = rows[0] if rows else None
            if header_row:
                headers = [cell.css('::text').get('').strip().lower() 
                          for cell in header_row.css('th, td')]
            
            # Find amount and service columns
            amount_col = self._find_amount_column(headers)
            service_col = self._find_service_column(headers)
            
            # Process data rows
            for row in rows[1:]:  # Skip header
                cells = row.css('td')
                if len(cells) < 2:
                    continue
                
                try:
                    # Extract service and amount
                    service_text = ""
                    amount_text = ""
                    
                    if service_col is not None and service_col < len(cells):
                        service_text = ' '.join(cells[service_col].css('::text').getall()).strip()
                    
                    if amount_col is not None and amount_col < len(cells):
                        amount_text = ' '.join(cells[amount_col].css('::text').getall()).strip()
                    
                    # Fallback: search all cells for amount
                    if not amount_text:
                        for cell in cells:
                            cell_text = ' '.join(cell.css('::text').getall()).strip()
                            if re.search(r'\d+\s*kr', cell_text):
                                amount_text = cell_text
                                break
                    
                    # Extract amount
                    amount = self._extract_amount_from_text(amount_text)
                    
                    if amount and service_text and 50 <= amount <= 100000:
                        fee = {
                            'fee_name': self._clean_text(service_text),
                            'amount': amount,
                            'currency': 'SEK',
                            'category': self._categorize_service(service_text),
                            'source_url': source_url,
                            'source_type': 'HTML',
                            'extraction_method': 'sitevision_table',
                            'confidence': 0.9,
                            'description': f"{service_text} - {amount_text}",
                            'extraction_date': datetime.now().isoformat()
                        }
                        fees.append(fee)
                
                except Exception as e:
                    self.logger.debug(f"Failed to process table row: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Table extraction failed: {e}")
        
        return fees
    
    def _process_playwright_fee(self, fee_data, source_url):
        """Process fee data extracted via Playwright"""
        try:
            amount = self._parse_swedish_currency(fee_data['amount_value'])
            
            if not amount or amount < 50 or amount > 100000:
                return None
            
            service_name = self._extract_service_name(fee_data['context'], fee_data['amount_text'])
            
            return {
                'fee_name': service_name,
                'amount': amount,
                'currency': 'SEK',
                'unit': fee_data.get('unit', ''),
                'category': self._categorize_service(fee_data['context']),
                'source_url': source_url,
                'source_type': 'HTML',
                'extraction_method': 'sitevision_playwright',
                'confidence': self._calculate_confidence(fee_data['context'], fee_data['amount_text']),
                'description': fee_data['context'][:200],
                'element_info': {
                    'class': fee_data.get('element_class', ''),
                    'tag': fee_data.get('element_tag', '')
                },
                'extraction_date': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.debug(f"Failed to process Playwright fee: {e}")
            return None
    
    def _validate_fee(self, fee):
        """Validate extracted fee data"""
        try:
            # Check required fields
            if not all(key in fee for key in ['fee_name', 'amount', 'currency']):
                return False
            
            # Validate amount
            if not self.validators.validate_fee_amount(fee['amount']):
                return False
            
            # Check fee name length
            if len(fee['fee_name'].strip()) < 3:
                return False
            
            # Check for reasonable content
            fee_name_lower = fee['fee_name'].lower()
            if any(spam in fee_name_lower for spam in ['lorem ipsum', 'test', 'example']):
                return False
            
            return True
        
        except Exception:
            return False
    
    def _parse_swedish_currency(self, amount_str):
        """Parse Swedish currency format to float"""
        if not amount_str:
            return None
        
        try:
            # Remove spaces (thousand separators)
            cleaned = str(amount_str).replace(' ', '')
            # Replace comma decimal separator with dot
            cleaned = cleaned.replace(',', '.')
            # Remove any non-digit/dot characters except the first dot
            parts = cleaned.split('.')
            if len(parts) > 2:
                cleaned = parts[0] + '.' + ''.join(parts[1:])
            
            return float(cleaned)
        except:
            return None
    
    def _extract_amount_from_text(self, text):
        """Extract amount from text string"""
        if not text:
            return None
        
        for pattern in self.fee_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._parse_swedish_currency(match.group(1))
        
        return None
    
    def _extract_service_name(self, context, amount_text):
        """Extract service name from context"""
        # Remove the amount from context
        context_clean = context.replace(amount_text, '').strip()
        
        # Split into sentences
        sentences = re.split(r'[.!?]', context_clean)
        
        # Find the sentence with service keywords
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and any(keyword in sentence.lower() 
                                        for keyword in self.service_keywords):
                return self._clean_text(sentence)
        
        # Fallback: use first meaningful sentence
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:
                return self._clean_text(sentence)
        
        return self._clean_text(context_clean[:100])
    
    def _categorize_service(self, text):
        """Categorize service based on Swedish keywords"""
        text_lower = text.lower()
        
        categories = {
            'bygglov': ['bygglov', 'bygganmälan', 'startbesked', 'slutbesked', 'nybyggnad', 'tillbyggnad'],
            'miljö': ['miljö', 'miljötillsyn', 'kemikalie', 'avlopp', 'utsläpp'],
            'livsmedel': ['livsmedel', 'restaurang', 'serveringstillstånd', 'alkohol'],
            'näringsverksamhet': ['näringsverksamhet', 'handelstillstånd', 'företag'],
            'socialtjänst': ['hemtjänst', 'äldreomsorg', 'omsorg', 'färdtjänst'],
            'skola': ['förskola', 'fritids', 'pedagogisk', 'barnomsorg'],
            'vatten': ['vatten', 'va-', 'anslutning', 'servis', 'mätare']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'övrigt'
    
    def _calculate_confidence(self, context, amount_text):
        """Calculate confidence score for extraction"""
        score = 0.5  # Base score
        
        # Boost for service keywords
        service_keyword_count = sum(1 for keyword in self.service_keywords 
                                  if keyword in context.lower())
        score += min(service_keyword_count * 0.1, 0.3)
        
        # Boost for proper currency format
        if re.search(r'\d{1,3}(?:\s\d{3})*\s*kr', amount_text):
            score += 0.1
        
        # Boost for table context
        if 'table' in context.lower() or '|' in context:
            score += 0.1
        
        # Penalty for very short context
        if len(context) < 50:
            score -= 0.1
        
        return min(max(score, 0.1), 1.0)
    
    def _find_amount_column(self, headers):
        """Find column containing amounts"""
        amount_indicators = ['avgift', 'kostnad', 'pris', 'taxa', 'belopp', 'kr', 'kronor']
        
        for i, header in enumerate(headers):
            if any(indicator in header for indicator in amount_indicators):
                return i
        
        return None
    
    def _find_service_column(self, headers):
        """Find column containing service descriptions"""
        service_indicators = ['tjänst', 'service', 'beskrivning', 'åtgärd', 'typ', 'ärende']
        
        for i, header in enumerate(headers):
            if any(indicator in header for indicator in service_indicators):
                return i
        
        # Default to first column if no specific indicator found
        return 0 if headers else None
    
    def _clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common artifacts
        cleaned = re.sub(r'[●•▪▫◦‣⁃]', '', cleaned)
        cleaned = re.sub(r'\.{3,}', '', cleaned)
        cleaned = re.sub(r'-{3,}', '', cleaned)
        
        return cleaned[:200]  # Limit length
    
    def _deduplicate_fees(self, fees):
        """Remove duplicate fees"""
        seen = set()
        unique_fees = []
        
        for fee in fees:
            # Create unique key
            key = f"{fee.get('fee_name', '')[:50]}_{fee.get('amount', 0)}"
            
            if key not in seen:
                seen.add(key)
                unique_fees.append(fee)
            else:
                # Keep the one with higher confidence
                for i, existing_fee in enumerate(unique_fees):
                    existing_key = f"{existing_fee.get('fee_name', '')[:50]}_{existing_fee.get('amount', 0)}"
                    if existing_key == key and fee.get('confidence', 0) > existing_fee.get('confidence', 0):
                        unique_fees[i] = fee
                        break
        
        return unique_fees
    
    def get_priority_links_sitevision(self, response):
        """Enhanced priority link extraction for SiteVision sites"""
        try:
            links = []
            
            # Extract from navigation areas
            for selector in self.sitevision_selectors['navigation']:
                nav_links = response.css(f'{selector} a::attr(href)').getall()
                links.extend(nav_links)
            
            # Extract from content portlets
            for selector in self.sitevision_selectors['content_areas']:
                content_links = response.css(f'{selector} a::attr(href)').getall()
                links.extend(content_links)
            
            # Score and filter links
            fee_links = []
            fee_keywords = [
                'avgift', 'taxa', 'bygglov', 'pris', 'kostnad', 'handläggning',
                'miljötillstånd', 'serveringstillstånd', 'näringstillstånd'
            ]
            
            for link in links:
                if link and any(keyword in link.lower() for keyword in fee_keywords):
                    full_url = response.urljoin(link)
                    if full_url not in fee_links:
                        fee_links.append(full_url)
            
            return fee_links[:15]  # Increased limit for better coverage
        
        except Exception as e:
            self.logger.error(f"Enhanced SiteVision link extraction failed: {e}")
            return [] 