import re
import logging

class GenericExtractor:
    """Generic extractor for unknown CMS types"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_fees_generic(self, response):
        """Extract fees using generic patterns"""
        fees = []
        
        try:
            # Generic selectors for common content areas
            fee_containers = response.css('main, .content, #content, .main-content, article')
            
            for container in fee_containers:
                text_content = ' '.join(container.css('::text').getall()).strip()
                
                # Look for fee patterns
                fee_matches = re.finditer(r'(\d+(?:[,\.]\d+)?)\s*kr', text_content, re.IGNORECASE)
                
                for match in fee_matches:
                    if any(keyword in text_content.lower() 
                          for keyword in ['avgift', 'taxa', 'kostnad', 'pris']):
                        fee = {
                            'fee_name': text_content[:100],
                            'amount': match.group(1),
                            'currency': 'SEK',
                            'category': 'Generic Fee',
                            'source_url': response.url,
                            'source_type': 'HTML',
                            'description': text_content
                        }
                        fees.append(fee)
        
        except Exception as e:
            self.logger.error(f"Generic extraction failed: {e}")
        
        return fees
    
    def get_generic_links(self, response):
        """Get fee-related links using generic patterns"""
        try:
            links = response.css('a::attr(href)').getall()
            fee_links = []
            
            for link in links:
                if any(keyword in link.lower() 
                      for keyword in ['avgift', 'taxa', 'bygglov', 'pris']):
                    fee_links.append(response.urljoin(link))
            
            return fee_links[:10]
        
        except Exception as e:
            self.logger.error(f"Generic link extraction failed: {e}")
            return [] 