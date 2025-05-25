import re
import logging
import asyncio
import json
from datetime import datetime
from .municipio_extractor import MunicipioExtractor
from ..utils.validators import SwedishValidators

class EnhancedMunicipioExtractor(MunicipioExtractor):
    """Enhanced Municipio extractor with WordPress-specific patterns and AJAX support"""
    
    def __init__(self):
        super().__init__()
        self.validators = SwedishValidators()
        
        # Enhanced Municipio/WordPress-specific selectors
        self.municipio_selectors = {
            'content_areas': [
                '.entry-content',
                '.wp-content',
                '.municipio-content',
                '.post-content',
                '.page-content',
                '.article-content',
                '.main-content',
                '.content-area'
            ],
            'fee_tables': [
                '.wp-table',
                '.municipio-table',
                'table.fee-table',
                '.entry-content table',
                '.wp-block-table'
            ],
            'widgets': [
                '.widget',
                '.sidebar-widget',
                '.municipio-widget',
                '.wp-widget'
            ],
            'navigation': [
                '.main-navigation',
                '.primary-navigation',
                '.municipio-nav',
                '.wp-nav-menu'
            ]
        }
        
        # WordPress/Municipio-specific patterns
        self.municipio_patterns = [
            # Standard WordPress shortcode patterns
            r'\[fee[^\]]*\]([^[]*)\[/fee\]',
            # Municipio-specific fee blocks
            r'<div[^>]*class="[^"]*fee[^"]*"[^>]*>([^<]*)</div>',
            # WordPress custom fields
            r'<meta[^>]*name="fee[^"]*"[^>]*content="([^"]*)"[^>]*>',
        ]
        
        # Enhanced Swedish fee patterns for WordPress content
        self.fee_patterns = [
            # Standard format with WordPress formatting
            r'(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr(?:\s*/\s*(\w+))?',
            # WordPress table cell format
            r'<td[^>]*>.*?(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr.*?</td>',
            # Municipio fee widget format
            r'class="fee-amount"[^>]*>(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr',
            # WordPress list format
            r'<li[^>]*>.*?(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr.*?</li>',
        ]
        
        # WordPress/Municipio service keywords
        self.service_keywords = [
            'avgift', 'taxa', 'kostnad', 'pris', 'handläggning', 'prövning',
            'ansökan', 'tillsyn', 'kontroll', 'besiktning', 'granskning',
            'bygglov', 'miljötillstånd', 'serveringstillstånd', 'näringstillstånd',
            'licens', 'tillstånd', 'anmälan', 'registrering'
        ]
        
        # WordPress AJAX endpoints for dynamic content
        self.ajax_endpoints = [
            '/wp-admin/admin-ajax.php',
            '/wp-json/wp/v2/',
            '/api/municipio/fees/',
            '/ajax/get-fees/'
        ]
    
    async def extract_with_ajax(self, base_url):
        """Extract fees from WordPress AJAX endpoints"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set up request interception to catch AJAX calls
                ajax_responses = []
                
                async def handle_response(response):
                    if any(endpoint in response.url for endpoint in self.ajax_endpoints):
                        try:
                            content = await response.text()
                            ajax_responses.append({
                                'url': response.url,
                                'content': content,
                                'status': response.status
                            })
                        except:
                            pass
                
                page.on('response', handle_response)
                
                try:
                    # Navigate to the page
                    await page.goto(base_url, wait_until='networkidle', timeout=30000)
                    
                    # Wait for potential AJAX calls
                    await page.wait_for_timeout(3000)
                    
                    # Try to trigger fee-related AJAX calls
                    await page.evaluate('''
                        () => {
                            // Look for fee-related buttons or links that might trigger AJAX
                            const triggers = document.querySelectorAll(
                                'button[data-action*="fee"], a[data-action*="fee"], ' +
                                '.fee-toggle, .load-fees, .show-fees'
                            );
                            
                            triggers.forEach(trigger => {
                                try {
                                    trigger.click();
                                } catch (e) {
                                    console.log('Failed to click trigger:', e);
                                }
                            });
                        }
                    ''')
                    
                    # Wait for additional AJAX responses
                    await page.wait_for_timeout(2000)
                    
                    await browser.close()
                    
                    # Process AJAX responses
                    fees = []
                    for response in ajax_responses:
                        ajax_fees = self._extract_fees_from_ajax_response(response, base_url)
                        fees.extend(ajax_fees)
                    
                    return self._deduplicate_fees(fees)
                    
                except Exception as e:
                    self.logger.error(f"AJAX extraction failed: {e}")
                    return []
                finally:
                    await browser.close()
                    
        except ImportError:
            self.logger.error("Playwright not available for AJAX extraction")
            return []
        except Exception as e:
            self.logger.error(f"AJAX extraction setup failed: {e}")
            return []
    
    def extract_fees_from_municipio(self, response):
        """Enhanced extraction from Municipio-based sites"""
        fees = []
        
        try:
            # Extract from content areas
            for selector in self.municipio_selectors['content_areas']:
                containers = response.css(selector)
                for container in containers:
                    container_fees = self._extract_from_container(container, response.url)
                    fees.extend(container_fees)
            
            # Extract from tables
            for selector in self.municipio_selectors['fee_tables']:
                tables = response.css(selector)
                for table in tables:
                    table_fees = self._extract_from_table(table, response.url)
                    fees.extend(table_fees)
            
            # Extract from widgets
            for selector in self.municipio_selectors['widgets']:
                widgets = response.css(selector)
                for widget in widgets:
                    widget_fees = self._extract_from_widget(widget, response.url)
                    fees.extend(widget_fees)
            
            # Extract from WordPress shortcodes and custom patterns
            shortcode_fees = self._extract_from_shortcodes(response)
            fees.extend(shortcode_fees)
            
            # Validate and deduplicate
            validated_fees = [fee for fee in fees if self._validate_fee(fee)]
            return self._deduplicate_fees(validated_fees)
        
        except Exception as e:
            self.logger.error(f"Enhanced Municipio extraction failed: {e}")
            return []
    
    def _extract_from_container(self, container, source_url):
        """Extract fees from a content container"""
        fees = []
        
        # Get both text and HTML content
        text_content = ' '.join(container.css('::text').getall()).strip()
        html_content = container.get()
        
        if not text_content or len(text_content) < 10:
            return fees
        
        # Apply text patterns
        for pattern in self.fee_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                context = self._get_context_around_match(text_content, match)
                
                if any(keyword in context.lower() for keyword in self.service_keywords):
                    amount = self._parse_swedish_currency(match.group(1))
                    
                    if amount and 50 <= amount <= 100000:
                        fee = {
                            'fee_name': self._extract_service_name(context, match.group(0)),
                            'amount': amount,
                            'currency': 'SEK',
                            'unit': match.group(2) if match.lastindex >= 2 else '',
                            'category': self._categorize_service(context),
                            'source_url': source_url,
                            'source_type': 'HTML',
                            'extraction_method': 'municipio_enhanced',
                            'confidence': self._calculate_confidence(context, match.group(0)),
                            'description': context[:200],
                            'extraction_date': datetime.now().isoformat()
                        }
                        fees.append(fee)
        
        # Apply HTML patterns for WordPress-specific markup
        for pattern in self.municipio_patterns:
            matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                content = match.group(1) if match.groups() else match.group(0)
                amount = self._extract_amount_from_text(content)
                
                if amount and 50 <= amount <= 100000:
                    fee = {
                        'fee_name': self._clean_text(content),
                        'amount': amount,
                        'currency': 'SEK',
                        'category': self._categorize_service(content),
                        'source_url': source_url,
                        'source_type': 'HTML',
                        'extraction_method': 'municipio_shortcode',
                        'confidence': 0.8,
                        'description': content[:200],
                        'extraction_date': datetime.now().isoformat()
                    }
                    fees.append(fee)
        
        return fees
    
    def _extract_from_table(self, table, source_url):
        """Extract fees from WordPress/Municipio table structures"""
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
            for row in rows[1:]:
                cells = row.css('td')
                if len(cells) < 2:
                    continue
                
                try:
                    service_text = ""
                    amount_text = ""
                    
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
                            if len(cell_text) > 10 and not re.search(r'\d+\s*kr', cell_text):
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
                            'extraction_method': 'municipio_table',
                            'confidence': 0.9,
                            'description': f"{service_text} - {amount_text}",
                            'extraction_date': datetime.now().isoformat()
                        }
                        fees.append(fee)
                
                except Exception as e:
                    self.logger.debug(f"Failed to process table row: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Municipio table extraction failed: {e}")
        
        return fees
    
    def _extract_from_widget(self, widget, source_url):
        """Extract fees from WordPress widgets"""
        fees = []
        
        try:
            widget_content = ' '.join(widget.css('::text').getall()).strip()
            
            # Check if widget contains fee information
            if not any(keyword in widget_content.lower() for keyword in self.service_keywords):
                return fees
            
            # Look for fee patterns in widget
            for pattern in self.fee_patterns:
                matches = re.finditer(pattern, widget_content, re.IGNORECASE)
                
                for match in matches:
                    amount = self._parse_swedish_currency(match.group(1))
                    
                    if amount and 50 <= amount <= 100000:
                        context = self._get_context_around_match(widget_content, match)
                        
                        fee = {
                            'fee_name': self._extract_service_name(context, match.group(0)),
                            'amount': amount,
                            'currency': 'SEK',
                            'category': self._categorize_service(context),
                            'source_url': source_url,
                            'source_type': 'HTML',
                            'extraction_method': 'municipio_widget',
                            'confidence': 0.7,
                            'description': context[:200],
                            'extraction_date': datetime.now().isoformat()
                        }
                        fees.append(fee)
        
        except Exception as e:
            self.logger.debug(f"Widget extraction failed: {e}")
        
        return fees
    
    def _extract_from_shortcodes(self, response):
        """Extract fees from WordPress shortcodes"""
        fees = []
        
        try:
            html_content = response.text
            
            # WordPress shortcode patterns
            shortcode_patterns = [
                r'\[fee[^\]]*amount="([^"]*)"[^\]]*\]([^[]*)\[/fee\]',
                r'\[price[^\]]*\]([^[]*?)(\d{1,3}(?:\s\d{3})*(?:,\d{1,2})?)\s*kr[^[]*\[/price\]',
                r'\[municipio_fee[^\]]*\]([^[]*)\[/municipio_fee\]',
            ]
            
            for pattern in shortcode_patterns:
                matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
                
                for match in matches:
                    if len(match.groups()) >= 2:
                        amount_str = match.group(1)
                        service_text = match.group(2)
                    else:
                        content = match.group(1) if match.groups() else match.group(0)
                        amount_str = self._extract_amount_from_text(content)
                        service_text = content
                    
                    amount = self._parse_swedish_currency(amount_str) if isinstance(amount_str, str) else amount_str
                    
                    if amount and 50 <= amount <= 100000:
                        fee = {
                            'fee_name': self._clean_text(service_text),
                            'amount': amount,
                            'currency': 'SEK',
                            'category': self._categorize_service(service_text),
                            'source_url': response.url,
                            'source_type': 'HTML',
                            'extraction_method': 'municipio_shortcode',
                            'confidence': 0.85,
                            'description': service_text[:200],
                            'extraction_date': datetime.now().isoformat()
                        }
                        fees.append(fee)
        
        except Exception as e:
            self.logger.error(f"Shortcode extraction failed: {e}")
        
        return fees
    
    def _extract_fees_from_ajax_response(self, ajax_response, base_url):
        """Extract fees from AJAX response data"""
        fees = []
        
        try:
            content = ajax_response['content']
            
            # Try to parse as JSON first
            try:
                data = json.loads(content)
                if isinstance(data, dict) and 'fees' in data:
                    for fee_data in data['fees']:
                        if isinstance(fee_data, dict):
                            fee = self._process_ajax_fee_data(fee_data, base_url)
                            if fee and self._validate_fee(fee):
                                fees.append(fee)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            fee = self._process_ajax_fee_data(item, base_url)
                            if fee and self._validate_fee(fee):
                                fees.append(fee)
            except json.JSONDecodeError:
                # Not JSON, treat as HTML/text
                text_fees = self._extract_fees_from_text(content, base_url)
                fees.extend(text_fees)
        
        except Exception as e:
            self.logger.error(f"AJAX response processing failed: {e}")
        
        return fees
    
    def _process_ajax_fee_data(self, fee_data, base_url):
        """Process fee data from AJAX response"""
        try:
            # Common field mappings for WordPress/Municipio AJAX responses
            field_mappings = {
                'name': ['name', 'title', 'service', 'description', 'fee_name'],
                'amount': ['amount', 'price', 'cost', 'fee', 'value'],
                'category': ['category', 'type', 'group', 'class'],
                'unit': ['unit', 'per', 'interval']
            }
            
            fee = {
                'source_url': base_url,
                'source_type': 'AJAX',
                'extraction_method': 'municipio_ajax',
                'confidence': 0.8,
                'extraction_date': datetime.now().isoformat()
            }
            
            # Map fields
            for target_field, possible_fields in field_mappings.items():
                for field in possible_fields:
                    if field in fee_data:
                        if target_field == 'amount':
                            amount = self._parse_swedish_currency(str(fee_data[field]))
                            if amount:
                                fee['amount'] = amount
                                fee['currency'] = 'SEK'
                        else:
                            fee[f'fee_{target_field}' if target_field == 'name' else target_field] = str(fee_data[field])
                        break
            
            # Validate required fields
            if 'fee_name' in fee and 'amount' in fee:
                return fee
            
        except Exception as e:
            self.logger.debug(f"Failed to process AJAX fee data: {e}")
        
        return None
    
    def _extract_fees_from_text(self, text, source_url):
        """Extract fees from plain text (AJAX response)"""
        fees = []
        
        for pattern in self.fee_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                context = self._get_context_around_match(text, match)
                
                if any(keyword in context.lower() for keyword in self.service_keywords):
                    amount = self._parse_swedish_currency(match.group(1))
                    
                    if amount and 50 <= amount <= 100000:
                        fee = {
                            'fee_name': self._extract_service_name(context, match.group(0)),
                            'amount': amount,
                            'currency': 'SEK',
                            'category': self._categorize_service(context),
                            'source_url': source_url,
                            'source_type': 'AJAX',
                            'extraction_method': 'municipio_ajax_text',
                            'confidence': 0.7,
                            'description': context[:200],
                            'extraction_date': datetime.now().isoformat()
                        }
                        fees.append(fee)
        
        return fees
    
    # Utility methods (similar to enhanced Sitevision extractor)
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
            cleaned = str(amount_str).replace(' ', '').replace(',', '.')
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
    
    def _get_context_around_match(self, text, match):
        """Get context around a regex match"""
        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 100)
        return text[start:end].strip()
    
    def _extract_service_name(self, context, amount_text):
        """Extract service name from context"""
        context_clean = context.replace(amount_text, '').strip()
        sentences = re.split(r'[.!?]', context_clean)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and any(keyword in sentence.lower() 
                                        for keyword in self.service_keywords):
                return self._clean_text(sentence)
        
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
        score = 0.5
        
        service_keyword_count = sum(1 for keyword in self.service_keywords 
                                  if keyword in context.lower())
        score += min(service_keyword_count * 0.1, 0.3)
        
        if re.search(r'\d{1,3}(?:\s\d{3})*\s*kr', amount_text):
            score += 0.1
        
        if 'table' in context.lower() or '|' in context:
            score += 0.1
        
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
        
        return 0 if headers else None
    
    def _clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        
        cleaned = re.sub(r'\s+', ' ', text).strip()
        cleaned = re.sub(r'[●•▪▫◦‣⁃]', '', cleaned)
        cleaned = re.sub(r'\.{3,}', '', cleaned)
        cleaned = re.sub(r'-{3,}', '', cleaned)
        
        return cleaned[:200]
    
    def _deduplicate_fees(self, fees):
        """Remove duplicate fees"""
        seen = set()
        unique_fees = []
        
        for fee in fees:
            key = f"{fee.get('fee_name', '')[:50]}_{fee.get('amount', 0)}"
            
            if key not in seen:
                seen.add(key)
                unique_fees.append(fee)
            else:
                for i, existing_fee in enumerate(unique_fees):
                    existing_key = f"{existing_fee.get('fee_name', '')[:50]}_{existing_fee.get('amount', 0)}"
                    if existing_key == key and fee.get('confidence', 0) > existing_fee.get('confidence', 0):
                        unique_fees[i] = fee
                        break
        
        return unique_fees
    
    def get_priority_links_municipio(self, response):
        """Enhanced priority link extraction for Municipio sites"""
        try:
            links = []
            
            # Extract from navigation areas
            for selector in self.municipio_selectors['navigation']:
                nav_links = response.css(f'{selector} a::attr(href)').getall()
                links.extend(nav_links)
            
            # Extract from content areas
            for selector in self.municipio_selectors['content_areas']:
                content_links = response.css(f'{selector} a::attr(href)').getall()
                links.extend(content_links)
            
            # Extract from widgets
            for selector in self.municipio_selectors['widgets']:
                widget_links = response.css(f'{selector} a::attr(href)').getall()
                links.extend(widget_links)
            
            # Score and filter links
            fee_links = []
            fee_keywords = [
                'avgift', 'taxa', 'bygglov', 'pris', 'kostnad', 'handläggning',
                'miljötillstånd', 'serveringstillstånd', 'näringstillstånd',
                'licens', 'tillstånd', 'anmälan'
            ]
            
            for link in links:
                if link and any(keyword in link.lower() for keyword in fee_keywords):
                    full_url = response.urljoin(link)
                    if full_url not in fee_links:
                        fee_links.append(full_url)
            
            return fee_links[:15]
        
        except Exception as e:
            self.logger.error(f"Enhanced Municipio link extraction failed: {e}")
            return [] 