# Scrapy settings for swedish_municipal_crawler project

BOT_NAME = 'swedish_municipal_crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure pipelines in correct order
ITEM_PIPELINES = {
    # 1. Enhanced validation with confidence scoring (existing)
    'crawler.pipelines.enhanced_validation_pipeline.EnhancedValidationPipeline': 200,
    
    # 2. Enhanced duplicate detection with intelligent merging (new)
    'crawler.pipelines.enhanced_duplicate_pipeline.EnhancedDuplicatesPipeline': 250,
    
    # 3. Enhanced data export with SQLite and Excel (new)
    'crawler.pipelines.enhanced_data_pipeline.EnhancedSwedishFeeDataPipeline': 300,
}

# Enhanced validation settings
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        },
        'fee_name_validation': {
            'min_length': 3,
            'max_length': 500
        }
    }
}

# Enhanced duplicate detection settings
ENHANCED_DUPLICATE_SETTINGS = {
    'detection_strategies': ['exact_match', 'fuzzy_match', 'semantic_match'],
    'quality_threshold': 0.15,
    'enable_merging': True,
    'quality_weights': {
        'confidence': 0.3,
        'validation_score': 0.25,
        'extraction_method': 0.2,
        'data_completeness': 0.15,
        'source_reliability': 0.1
    }
}

# Enhanced data pipeline settings
ENHANCED_DATA_PIPELINE_SETTINGS = {
    'enable_excel_export': True,
    'enable_sqlite_storage': True,
    'enable_comprehensive_stats': True,
    'excel_sheets': [
        'Municipal_Fees',
        'Municipality_Summary', 
        'Category_Breakdown',
        'Bygglov_Analysis',
        'Quality_Metrics'
    ]
}

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 1

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'sv,en',
    'User-Agent': 'SwedishMunicipalResearch/1.0 (+https://example.com/research)',
}

# Enable autothrottling
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 24 hours
HTTPCACHE_DIR = 'data/cache'
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Configure Playwright for JavaScript rendering
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_LAUNCH_OPTIONS = {
    'headless': True,
    'timeout': 30000,
    'args': ['--no-sandbox', '--disable-dev-shm-usage']
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000

# Resume capability
JOBDIR = 'crawls/swedish_municipalities'

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'crawler.log'

# Request timeout
DOWNLOAD_TIMEOUT = 60

# Retry settings
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Memory usage optimization
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 2048
MEMUSAGE_WARNING_MB = 1024

# Enhanced statistics tracking
STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'

# Custom extensions for enhanced monitoring
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.memusage.MemoryUsage': 500,
    'scrapy.extensions.closespider.CloseSpider': 500,
}

# Close spider settings
CLOSESPIDER_TIMEOUT = 3600  # 1 hour timeout
CLOSESPIDER_ITEMCOUNT = 10000  # Max items per spider run 