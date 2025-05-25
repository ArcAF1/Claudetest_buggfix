class MunicipalityClassifier:
    """Classify municipalities by size and adjust crawling strategy"""
    
    def __init__(self):
        # Population thresholds for classification
        self.size_thresholds = {
            'large': 100000,    # Stockholm, Göteborg, Malmö, etc.
            'medium': 50000,    # Regional centers
            'small': 20000,     # Smaller cities
            'tiny': 0           # Rural municipalities
        }
        
        # Known large municipalities that need special handling
        self.large_municipalities = {
            'stockholm', 'göteborg', 'malmö', 'uppsala', 'västerås',
            'örebro', 'linköping', 'helsingborg', 'jönköping', 'norrköping',
            'lund', 'umeå', 'gävle', 'borås', 'eskilstuna'
        }
        
        # Municipalities known to use specific CMS
        self.cms_preferences = {
            'sitevision': ['stockholm', 'göteborg', 'malmö', 'uppsala'],
            'municipio': ['helsingborg', 'lund', 'växjö'],
            'episerver': ['västerås', 'örebro']
        }
    
    def classify_municipality(self, municipality_name, population=None):
        """Classify municipality by size and characteristics"""
        name_lower = municipality_name.lower()
        
        # Check if it's a known large municipality
        if name_lower in self.large_municipalities:
            return 'large'
        
        # Classify by population if available
        if population:
            for size, threshold in self.size_thresholds.items():
                if population >= threshold:
                    return size
        
        # Default classification based on name patterns
        if any(keyword in name_lower for keyword in ['stad', 'city']):
            return 'medium'
        
        return 'small'
    
    def get_crawl_config(self, municipality_type):
        """Get crawling configuration based on municipality type"""
        configs = {
            'large': {
                'download_delay': 3,
                'max_pages': 50,
                'max_pdfs': 10,
                'timeout': 60,
                'retry_times': 3,
                'js_rendering': True
            },
            'medium': {
                'download_delay': 2,
                'max_pages': 30,
                'max_pdfs': 8,
                'timeout': 45,
                'retry_times': 2,
                'js_rendering': True
            },
            'small': {
                'download_delay': 1,
                'max_pages': 20,
                'max_pdfs': 5,
                'timeout': 30,
                'retry_times': 2,
                'js_rendering': False
            },
            'tiny': {
                'download_delay': 1,
                'max_pages': 10,
                'max_pdfs': 3,
                'timeout': 20,
                'retry_times': 1,
                'js_rendering': False
            }
        }
        
        return configs.get(municipality_type, configs['small'])
    
    def get_expected_cms(self, municipality_name):
        """Get expected CMS type for municipality"""
        name_lower = municipality_name.lower()
        
        for cms, municipalities in self.cms_preferences.items():
            if name_lower in municipalities:
                return cms
        
        return None
    
    def get_priority_keywords(self, municipality_type):
        """Get priority keywords based on municipality type"""
        base_keywords = ['avgift', 'taxa', 'bygglov', 'miljö']
        
        if municipality_type in ['large', 'medium']:
            return base_keywords + [
                'näringsverksamhet', 'serveringstillstånd', 
                'livsmedel', 'handläggningsavgift'
            ]
        else:
            return base_keywords + ['prislista', 'timtaxa'] 