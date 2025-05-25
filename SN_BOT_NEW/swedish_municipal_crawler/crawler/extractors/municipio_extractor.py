import re
import logging

class MunicipioExtractor:
    """Extractor for Municipio CMS sites (WordPress-based)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_fees_from_municipio(self, response):
        """Extract fees from Municipio-based sites"""
        fees = []
        
        try:
            # Municipio/WordPress-specific selectors
            fee_containers = response.css('.entry-content, .wp-content, .municipio-content')
            
            for container in fee_containers:
                text_content = ' '.join(container.css('::text').getall()).strip()
                
                # Look for fee patterns
                fee_matches = re.finditer(r'(\d+(?:[,\.]\d+)?)\s*kr', text_content, re.IGNORECASE)
                
                for match in fee_matches:
                    if any(keyword in text_content.lower() 
                          for keyword in ['avgift', 'taxa', 'kostnad']):
                        fee = {
                            'fee_name': text_content[:100],
                            'amount': match.group(1),
                            'currency': 'SEK',
                            'category': 'Municipio Fee',
                            'source_url': response.url,
                            'source_type': 'HTML',
                            'description': text_content
                        }
                        fees.append(fee)
        
        except Exception as e:
            self.logger.error(f"Municipio extraction failed: {e}")
        
        return fees
    
    def get_priority_links_municipio(self, response):
        """Get priority links from Municipio sites"""
        try:
            links = response.css('.entry-content a::attr(href), .wp-content a::attr(href)').getall()
            fee_links = []
            
            for link in links:
                if any(keyword in link.lower() 
                      for keyword in ['avgift', 'taxa', 'bygglov']):
                    fee_links.append(response.urljoin(link))
            
            return fee_links[:10]
        
        except Exception as e:
            self.logger.error(f"Municipio link extraction failed: {e}")
            return [] 