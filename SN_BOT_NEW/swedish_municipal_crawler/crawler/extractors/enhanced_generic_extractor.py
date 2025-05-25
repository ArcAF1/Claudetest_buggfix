import re
import logging
import asyncio
from datetime import datetime
from .generic_extractor import GenericExtractor
from ..utils.validators import SwedishValidators

class EnhancedGenericExtractor(GenericExtractor):
    """Enhanced generic extractor with multiple strategies and validation"""
    
    def __init__(self):
        super().__init__()
        self.validators = SwedishValidators()
        
        # Comprehensive generic selectors for various CMS types
        self.generic_selectors = {
            'content_areas': [
                'main', '.content', '#content', '.main-content', 'article',
                '.page-content', '.post-content', '.entry-content',
                '.site-content', '.primary-content', '.main-area',
                '.content-wrapper', '.page-wrapper', '.container',
                '.row', '.col', '.section', '.article-body'
            ],
            'fee_tables': [
                'table', '.table', '.data-table', '.fee-table', '.price-table',
                '.cost-table', '.tariff-table', '.rates-table',
                '.table-responsive table', '.table-striped', '.table-bordered'
            ],
            'lists': [
                'ul', 'ol', '.list', '.fee-list', '.price-list',
                '.service-list', '.cost-list', '.rates-list'
            ],
            'cards': [
                '.card', '.box', '.panel', '.widget', '.block',
                '.service-card', '.fee-card', '.price-card'
            ]
        }
        
        # Enhanced Swedish fee patterns for various formats
        self.fee_patterns = [
            # Standard Swedish format: "1 250 kr" or "1 250,50 kr"
            r'(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr(?:\s*/\s*(\w+))?',
            # Alternative thousand separator: "1.250,50 kr"
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?)\s*kr(?:\s*/\s*(\w+))?',
            # With kronor: "1 250 kronor"
            r'(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kronor',
            # SEK format: "SEK 1 250,50"
            r'SEK\s*(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)',
            # Colon format: "Avgift: 1 250 kr"
            r'[Aa]vgift:?\s*(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr',
            # Equals format: "Taxa = 1 250 kr"
            r'[Tt]axa\s*[=:]\s*(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr',
            # Dash format: "Handläggning - 1 250 kr"
            r'([^-]+)\s*-\s*(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr',
            # Parentheses format: "Service (1 250 kr)"
            r'([^(]+)\s*\(\s*(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr\s*\)',
            # Tab separated: "Service\t1 250 kr"
            r'([^\t]+)\t+(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr',
            # Multiple spaces: "Service    1 250 kr"
            r'([^0-9]+?)\s{3,}(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr'
        ]
        
        # Comprehensive Swedish service keywords
        self.service_keywords = [
            # Basic fee terms
            'avgift', 'taxa', 'kostnad', 'pris', 'tariff', 'belopp',
            # Administrative terms
            'handläggning', 'prövning', 'ansökan', 'tillsyn', 'kontroll',
            'besiktning', 'granskning', 'registrering', 'anmälan',
            # Specific services
            'bygglov', 'miljötillstånd', 'serveringstillstånd', 'näringstillstånd',
            'licens', 'tillstånd', 'certifikat', 'godkännande',
            # Municipal services
            'hemtjänst', 'äldreomsorg', 'barnomsorg', 'förskola',
            'vatten', 'avlopp', 'renhållning', 'parkering'
        ]
        
        # Extraction strategies in order of preference
        self.extraction_strategies = [
            'structured_tables',
            'semantic_lists',
            'card_layouts',
            'text_patterns',
            'fallback_patterns'
        ]
    
    async def extract_with_multiple_strategies(self, url):
        """Extract fees using multiple strategies with Playwright"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                try:
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    
                    # Wait for dynamic content
                    await page.wait_for_timeout(2000)
                    
                    # Extract page content
                    page_content = await page.evaluate('''
                        () => {
                            return {
                                html: document.documentElement.outerHTML,
                                text: document.body.innerText || document.body.textContent,
                                tables: Array.from(document.querySelectorAll('table')).map(table => ({
                                    html: table.outerHTML,
                                    text: table.innerText
                                })),
                                lists: Array.from(document.querySelectorAll('ul, ol')).map(list => ({
                                    html: list.outerHTML,
                                    text: list.innerText
                                }))
                            };
                        }
                    ''')
                    
                    await browser.close()
                    
                    # Apply multiple extraction strategies
                    all_fees = []
                    
                    for strategy in self.extraction_strategies:
                        strategy_fees = self._apply_extraction_strategy(strategy, page_content, url)
                        all_fees.extend(strategy_fees)
                    
                    # Validate and deduplicate
                    validated_fees = [fee for fee in all_fees if self._validate_fee(fee)]
                    return self._deduplicate_fees(validated_fees)
                    
                except Exception as e:
                    self.logger.error(f"Playwright extraction failed: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except ImportError:
            self.logger.error("Playwright not available for enhanced extraction")
            return []
        except Exception as e:
            self.logger.error(f"Enhanced extraction setup failed: {e}")
            return []
    
    def extract_fees_generic(self, response):
        """Enhanced generic extraction with multiple strategies"""
        fees = []
        
        try:
            # Strategy 1: Extract from structured tables
            table_fees = self._extract_from_tables(response)
            fees.extend(table_fees)
            
            # Strategy 2: Extract from lists
            list_fees = self._extract_from_lists(response)
            fees.extend(list_fees)
            
            # Strategy 3: Extract from card layouts
            card_fees = self._extract_from_cards(response)
            fees.extend(card_fees)
            
            # Strategy 4: Extract from content areas using patterns
            content_fees = self._extract_from_content_areas(response)
            fees.extend(content_fees)
            
            # Strategy 5: Fallback text pattern extraction
            if not fees:
                fallback_fees = self._extract_with_fallback_patterns(response)
                fees.extend(fallback_fees)
            
            # Validate and deduplicate
            validated_fees = [fee for fee in fees if self._validate_fee(fee)]
            return self._deduplicate_fees(validated_fees)
        
        except Exception as e:
            self.logger.error(f"Enhanced generic extraction failed: {e}")
            return []
    
    def _apply_extraction_strategy(self, strategy, page_content, url):
        """Apply a specific extraction strategy"""
        fees = []
        
        try:
            if strategy == 'structured_tables':
                fees = self._extract_from_playwright_tables(page_content['tables'], url)
            elif strategy == 'semantic_lists':
                fees = self._extract_from_playwright_lists(page_content['lists'], url)
            elif strategy == 'text_patterns':
                fees = self._extract_from_playwright_text(page_content['text'], url)
            elif strategy == 'fallback_patterns':
                fees = self._extract_with_playwright_fallback(page_content['html'], url)
        
        except Exception as e:
            self.logger.debug(f"Strategy {strategy} failed: {e}")
        
        return fees
    
    def _extract_from_tables(self, response):
        """Extract fees from table structures"""
        fees = []
        
        for selector in self.generic_selectors['fee_tables']:
            tables = response.css(selector)
            
            for table in tables:
                # Check if table contains fee information
                table_text = ' '.join(table.css('::text').getall()).lower()
                
                if any(keyword in table_text for keyword in self.service_keywords):
                    table_fees = self._parse_table_structure(table, response.url)
                    fees.extend(table_fees)
        
        return fees
    
    def _extract_from_lists(self, response):
        """Extract fees from list structures"""
        fees = []
        
        for selector in self.generic_selectors['lists']:
            lists = response.css(selector)
            
            for list_element in lists:
                # Check if list contains fee information
                list_text = ' '.join(list_element.css('::text').getall()).lower()
                
                if any(keyword in list_text for keyword in self.service_keywords):
                    list_fees = self._parse_list_structure(list_element, response.url)
                    fees.extend(list_fees)
        
        return fees
    
    def _extract_from_cards(self, response):
        """Extract fees from card/widget layouts"""
        fees = []
        
        for selector in self.generic_selectors['cards']:
            cards = response.css(selector)
            
            for card in cards:
                # Check if card contains fee information
                card_text = ' '.join(card.css('::text').getall()).lower()
                
                if any(keyword in card_text for keyword in self.service_keywords):
                    card_fees = self._parse_card_structure(card, response.url)
                    fees.extend(card_fees)
        
        return fees
    
    def _extract_from_content_areas(self, response):
        """Extract fees from general content areas"""
        fees = []
        
        for selector in self.generic_selectors['content_areas']:
            containers = response.css(selector)
            
            for container in containers:
                container_text = ' '.join(container.css('::text').getall())
                
                if len(container_text) > 50:  # Skip very short content
                    container_fees = self._extract_from_text_content(container_text, response.url)
                    fees.extend(container_fees)
        
        return fees
    
    def _extract_with_fallback_patterns(self, response):
        """Fallback extraction using aggressive text patterns"""
        fees = []
        
        try:
            full_text = response.text
            
            # Use more aggressive patterns for fallback
            fallback_patterns = [
                # Any number followed by kr with context
                r'([^.!?]{10,100}?)(\d{1,3}(?:[\s.,]\d{3})*(?:,\d{1,2})?)\s*kr',
                # Lines containing both service keywords and amounts
                r'([^\n]*(?:' + '|'.join(self.service_keywords[:10]) + r')[^\n]*\d{1,3}(?:[\s.,]\d{3})*(?:,\d{1,2})?\s*kr[^\n]*)',
            ]
            
            for pattern in fallback_patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    if len(match.groups()) >= 2:
                        service_text = match.group(1)
                        amount_text = match.group(2)
                    else:
                        content = match.group(0)
                        amount_text = self._extract_amount_from_text(content)
                        service_text = content
                    
                    amount = self._parse_swedish_currency(amount_text) if isinstance(amount_text, str) else amount_text
                    
                    if amount and 50 <= amount <= 100000:
                        fee = {
                            'fee_name': self._clean_text(service_text),
                            'amount': amount,
                            'currency': 'SEK',
                            'category': self._categorize_service(service_text),
                            'source_url': response.url,
                            'source_type': 'HTML',
                            'extraction_method': 'generic_fallback',
                            'confidence': 0.6,
                            'description': service_text[:200],
                            'extraction_date': datetime.now().isoformat()
                        }
                        fees.append(fee)
        
        except Exception as e:
            self.logger.error(f"Fallback extraction failed: {e}")
        
        return fees
    
    def _parse_table_structure(self, table, source_url):
        """Parse table structure for fees"""
        fees = []
        
        try:
            rows = table.css('tr')
            if len(rows) < 2:  # Need at least header and one data row
                return fees
            
            headers = []
            header_row = rows[0]
            if header_row:
                headers = [cell.css('::text').get('').strip().lower() 
                          for cell in header_row.css('th, td')]
            
            # Find relevant columns
            amount_col = self._find_amount_column(headers)
            service_col = self._find_service_column(headers)
            
            # Process data rows
            for row in rows[1:]:
                cells = row.css('td')
                if len(cells) < 2:
                    continue
                
                try:
                    service_text = ""
                    amount_text = ""
                    
                    # Extract service and amount based on column detection
                    if service_col is not None and service_col < len(cells):
                        service_text = ' '.join(cells[service_col].css('::text').getall()).strip()
                    
                    if amount_col is not None and amount_col < len(cells):
                        amount_text = ' '.join(cells[amount_col].css('::text').getall()).strip()
                    
                    # Fallback: search all cells
                    if not amount_text:
                        for cell in cells:
                            cell_text = ' '.join(cell.css('::text').getall()).strip()
                            if re.search(r'\d+\s*kr', cell_text):
                                amount_text = cell_text
                                break
                    
                    if not service_text:
                        for cell in cells:
                            cell_text = ' '.join(cell.css('::text').getall()).strip()
                            if len(cell_text) > 5 and not re.search(r'\d+\s*kr', cell_text):
                                service_text = cell_text
                                break
                    
                    amount = self._extract_amount_from_text(amount_text)
                    
                    if amount and service_text and 50 <= amount <= 100000:
                        fee = {
                            'fee_name': self._clean_text(service_text),
                            'amount': amount,
                            'currency': 'SEK',
                            'category': self._categorize_service(service_text),
                            'source_url': source_url,
                            'source_type': 'HTML',
                            'extraction_method': 'generic_table',
                            'confidence': 0.85,
                            'description': f"{service_text} - {amount_text}",
                            'extraction_date': datetime.now().isoformat()
                        }
                        fees.append(fee)
                
                except Exception as e:
                    self.logger.debug(f"Failed to process table row: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Table parsing failed: {e}")
        
        return fees
    
    def _parse_list_structure(self, list_element, source_url):
        """Parse list structure for fees"""
        fees = []
        
        try:
            items = list_element.css('li')
            
            for item in items:
                item_text = ' '.join(item.css('::text').getall()).strip()
                
                if len(item_text) > 10:  # Skip very short items
                    item_fees = self._extract_from_text_content(item_text, source_url, 'generic_list')
                    fees.extend(item_fees)
        
        except Exception as e:
            self.logger.error(f"List parsing failed: {e}")
        
        return fees
    
    def _parse_card_structure(self, card, source_url):
        """Parse card/widget structure for fees"""
        fees = []
        
        try:
            card_text = ' '.join(card.css('::text').getall()).strip()
            
            if len(card_text) > 20:  # Skip very short cards
                card_fees = self._extract_from_text_content(card_text, source_url, 'generic_card')
                fees.extend(card_fees)
        
        except Exception as e:
            self.logger.error(f"Card parsing failed: {e}")
        
        return fees
    
    def _extract_from_text_content(self, text, source_url, method='generic_text'):
        """Extract fees from text content using patterns"""
        fees = []
        
        for pattern in self.fee_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                try:
                    # Handle different pattern groups
                    if len(match.groups()) >= 2 and match.group(1) and match.group(2):
                        # Pattern with service and amount separated
                        service_text = match.group(1)
                        amount_text = match.group(2)
                    else:
                        # Pattern with amount only
                        amount_text = match.group(1)
                        # Get context around the match
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end]
                        service_text = self._extract_service_from_context(context, match.group(0))
                    
                    amount = self._parse_swedish_currency(amount_text)
                    
                    if amount and 50 <= amount <= 100000:
                        # Check if context contains service keywords
                        full_context = service_text + " " + amount_text
                        if any(keyword in full_context.lower() for keyword in self.service_keywords):
                            fee = {
                                'fee_name': self._clean_text(service_text),
                                'amount': amount,
                                'currency': 'SEK',
                                'category': self._categorize_service(service_text),
                                'source_url': source_url,
                                'source_type': 'HTML',
                                'extraction_method': method,
                                'confidence': self._calculate_confidence(full_context, amount_text),
                                'description': full_context[:200],
                                'extraction_date': datetime.now().isoformat()
                            }
                            fees.append(fee)
                
                except Exception as e:
                    self.logger.debug(f"Failed to process text match: {e}")
                    continue
        
        return fees
    
    # Playwright-specific extraction methods
    def _extract_from_playwright_tables(self, tables, url):
        """Extract from tables using Playwright data"""
        fees = []
        
        for table_data in tables:
            table_text = table_data['text']
            
            if any(keyword in table_text.lower() for keyword in self.service_keywords):
                # Parse table text line by line
                lines = table_text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if len(line) > 10:
                        line_fees = self._extract_from_text_content(line, url, 'generic_playwright_table')
                        fees.extend(line_fees)
        
        return fees
    
    def _extract_from_playwright_lists(self, lists, url):
        """Extract from lists using Playwright data"""
        fees = []
        
        for list_data in lists:
            list_text = list_data['text']
            
            if any(keyword in list_text.lower() for keyword in self.service_keywords):
                list_fees = self._extract_from_text_content(list_text, url, 'generic_playwright_list')
                fees.extend(list_fees)
        
        return fees
    
    def _extract_from_playwright_text(self, text, url):
        """Extract from full page text using Playwright"""
        return self._extract_from_text_content(text, url, 'generic_playwright_text')
    
    def _extract_with_playwright_fallback(self, html, url):
        """Fallback extraction from HTML using Playwright"""
        fees = []
        
        # Remove HTML tags and extract text
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return self._extract_from_text_content(text, url, 'generic_playwright_fallback')
    
    # Utility methods
    def _validate_fee(self, fee):
        """Validate extracted fee data"""
        try:
            if not all(key in fee for key in ['fee_name', 'amount', 'currency']):
                return False
            
            if not self.validators.validate_fee_amount(fee['amount']):
                return False
            
            if len(fee['fee_name'].strip()) < 3:
                return False
            
            fee_name_lower = fee['fee_name'].lower()
            if any(spam in fee_name_lower for spam in ['lorem ipsum', 'test', 'example', 'placeholder']):
                return False
            
            return True
        except Exception:
            return False
    
    def _parse_swedish_currency(self, amount_str):
        """Parse Swedish currency format to float"""
        if not amount_str:
            return None
        
        try:
            # Remove spaces and normalize
            cleaned = str(amount_str).replace(' ', '')
            # Handle different decimal separators
            cleaned = cleaned.replace(',', '.')
            # Remove any non-digit/dot characters
            cleaned = re.sub(r'[^\d.]', '', cleaned)
            
            # Handle multiple dots (thousand separators)
            parts = cleaned.split('.')
            if len(parts) > 2:
                # Assume last part is decimal, rest are thousands
                cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
            elif len(parts) == 2 and len(parts[1]) == 3:
                # Likely thousand separator, not decimal
                cleaned = ''.join(parts)
            
            return float(cleaned)
        except:
            return None
    
    def _extract_amount_from_text(self, text):
        """Extract amount from text string"""
        if not text:
            return None
        
        # Try each pattern
        for pattern in self.fee_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Find the group that contains the amount
                for group in match.groups():
                    if group and re.search(r'\d', group):
                        amount = self._parse_swedish_currency(group)
                        if amount:
                            return amount
        
        return None
    
    def _extract_service_from_context(self, context, amount_text):
        """Extract service name from context"""
        # Remove the amount from context
        context_clean = context.replace(amount_text, '').strip()
        
        # Split into sentences
        sentences = re.split(r'[.!?\n]', context_clean)
        
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
        score = 0.4  # Lower base score for generic extraction
        
        # Boost for service keywords
        service_keyword_count = sum(1 for keyword in self.service_keywords 
                                  if keyword in context.lower())
        score += min(service_keyword_count * 0.1, 0.3)
        
        # Boost for proper currency format
        if re.search(r'\d{1,3}(?:\s\d{3})*\s*kr', amount_text):
            score += 0.1
        
        # Boost for structured context (tables, lists)
        if any(indicator in context.lower() for indicator in ['table', 'list', '|', '\t']):
            score += 0.1
        
        # Penalty for very short context
        if len(context) < 30:
            score -= 0.1
        
        return min(max(score, 0.1), 1.0)
    
    def _find_amount_column(self, headers):
        """Find column containing amounts"""
        amount_indicators = ['avgift', 'kostnad', 'pris', 'taxa', 'belopp', 'kr', 'kronor', 'cost', 'price', 'fee']
        
        for i, header in enumerate(headers):
            if any(indicator in header for indicator in amount_indicators):
                return i
        
        return None
    
    def _find_service_column(self, headers):
        """Find column containing service descriptions"""
        service_indicators = ['tjänst', 'service', 'beskrivning', 'åtgärd', 'typ', 'ärende', 'description', 'name']
        
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
        cleaned = re.sub(r'_{3,}', '', cleaned)
        
        # Remove HTML entities
        cleaned = re.sub(r'&[a-zA-Z]+;', ' ', cleaned)
        
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
    
    def get_generic_links(self, response):
        """Enhanced generic link extraction"""
        try:
            links = []
            
            # Extract from all content areas
            for selector in self.generic_selectors['content_areas']:
                area_links = response.css(f'{selector} a::attr(href)').getall()
                links.extend(area_links)
            
            # Score and filter links
            fee_links = []
            fee_keywords = [
                'avgift', 'taxa', 'bygglov', 'pris', 'kostnad', 'handläggning',
                'miljötillstånd', 'serveringstillstånd', 'näringstillstånd',
                'licens', 'tillstånd', 'anmälan', 'fee', 'cost', 'price'
            ]
            
            for link in links:
                if link and any(keyword in link.lower() for keyword in fee_keywords):
                    full_url = response.urljoin(link)
                    if full_url not in fee_links:
                        fee_links.append(full_url)
            
            return fee_links[:20]  # Higher limit for generic extraction
        
        except Exception as e:
            self.logger.error(f"Enhanced generic link extraction failed: {e}")
            return [] 