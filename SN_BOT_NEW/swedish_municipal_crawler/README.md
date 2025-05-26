# Swedish Municipal Fee Crawler

Enhanced Swedish municipal fee crawler with CMS-aware architecture, JavaScript rendering, resume capability, **advanced PDF extraction engine**, **🆕 enhanced CMS-specific extractors with validation**, and **🆕 enhanced pipeline components**.

## Features

- **CMS Detection**: Automatically detects and adapts to different CMS types (SiteVision, Municipio, Episerver, Sitecore)
- **JavaScript Rendering**: Uses Playwright for sites requiring JavaScript execution
- **Resume Capability**: Can resume interrupted crawls from where they left off
- **Smart URL Prioritization**: Targets high-value fee-related pages first
- **Comprehensive Validation**: Validates Swedish organization numbers, phone numbers, and postal codes
- **Multiple Output Formats**: Exports data in JSON, CSV, and Excel formats
- **Duplicate Detection**: Filters out duplicate fee entries
- **Caching**: HTTP caching for efficient re-crawling
- **Respectful Crawling**: Auto-throttling and configurable delays
- **ML Page Classifier**: Lightweight model filters irrelevant pages

### 🆕 Enhanced Pipeline Components

The crawler now includes a sophisticated three-stage pipeline system for processing extracted fee data with advanced validation, duplicate detection, and export capabilities.

#### Pipeline Architecture

```
Raw Extracted Data
        ↓
Enhanced Validation Pipeline (Priority: 200)
        ↓
Enhanced Duplicate Detection Pipeline (Priority: 250)
        ↓
Enhanced Data Export Pipeline (Priority: 300)
        ↓
Final Output (JSON, CSV, Excel, SQLite)
```

#### Enhanced Validation Pipeline

Advanced validation with comprehensive quality assessment:

- **Weighted Validation Rules**: Different validation criteria with configurable weights
- **Confidence Scoring**: Assigns confidence scores based on data quality indicators
- **Swedish-Specific Validation**: Validates organization numbers, postal codes, phone numbers
- **Quality Indicators**: Evaluates data completeness, content quality, and source reliability
- **Contextual Validation**: Considers extraction method and source type

```python
# Example validation output
{
    'validation': {
        'confidence_score': 0.87,
        'warnings': ['Missing category information'],
        'validation_version': '2.0',
        'validated_at': '2024-01-15T10:30:00Z'
    },
    'quality': {
        'overall_score': 0.85,
        'data_completeness': 0.9,
        'content_quality': 0.8,
        'source_reliability': 0.9
    }
}
```

#### Enhanced Duplicate Detection Pipeline

Intelligent duplicate detection with quality-based merging:

- **Multiple Detection Strategies**: Exact match, fuzzy match, and semantic matching
- **Swedish Text Normalization**: Handles Swedish prepositions and common variations
- **Quality-Based Replacement**: Keeps higher quality versions of duplicate items
- **Intelligent Merging**: Combines complementary data from duplicate sources
- **Configurable Similarity Thresholds**: Adjustable matching sensitivity

```python
# Configuration example
DUPLICATE_DETECTION = {
    'strategies': ['exact_match', 'fuzzy_match', 'semantic_match'],
    'similarity_threshold': 0.7,
    'quality_weights': {
        'confidence': 0.4,
        'completeness': 0.3,
        'source_reliability': 0.2,
        'extraction_method': 0.1
    }
}
```

#### Enhanced Data Export Pipeline

Multi-format export with comprehensive analytics:

- **SQLite Database**: Structured storage with proper relationships and indexes
- **Excel Export**: Professional formatting with multiple sheets and charts
- **CSV Export**: UTF-8 encoded with standardized formatting
- **JSON Export**: Hierarchical organization suitable for API consumption
- **Comprehensive Statistics**: Detailed analytics and quality metrics

**SQLite Database Features:**
- Optimized schema with proper indexes
- Foreign key relationships
- Full-text search capabilities
- Query-ready structure

**Excel Export Features:**
- Multiple sheets (Fees, Statistics, Municipality Summary)
- Conditional formatting for quality indicators
- Automatic charts and pivot tables
- Pre-configured filters

**Statistics Generation:**
```json
{
    "summary": {
        "total_fees": 1250,
        "municipalities_count": 45,
        "average_fee": 8500.50,
        "extraction_date": "2024-01-15T10:30:00Z"
    },
    "quality_metrics": {
        "average_confidence": 0.85,
        "high_quality_items": 1050,
        "validation_warnings": 25
    },
    "by_category": {
        "bygglov": {
            "count": 450,
            "average_fee": 15000.00,
            "municipalities": 42
        }
    }
}
```

#### Testing Enhanced Pipelines

Test the pipeline components:

```bash
# Test all pipeline logic (no dependencies required)
python test_enhanced_pipelines_simple.py

# Full pipeline test (requires Scrapy)
python test_enhanced_pipelines.py
```

#### Pipeline Configuration

Configure the enhanced pipelines in `settings.py`:

```python
# Pipeline order and priorities
ITEM_PIPELINES = {
    'crawler.pipelines.enhanced_validation_pipeline.EnhancedValidationPipeline': 200,
    'crawler.pipelines.enhanced_duplicate_pipeline.EnhancedDuplicatesPipeline': 250,
    'crawler.pipelines.enhanced_data_pipeline.EnhancedSwedishFeeDataPipeline': 300,
}

# Validation settings
VALIDATION_RULES = {
    'required_fields': {
        'weight': 1.0,
        'fields': ['fee_name', 'amount', 'currency', 'source_url']
    },
    'amount_validation': {
        'weight': 0.9,
        'min_amount': 50,
        'max_amount': 100000
    }
}

# Export settings
EXPORT_FORMATS = ['json', 'csv', 'excel', 'sqlite']
OUTPUT_DIRECTORY = 'data/output'
```

#### Pipeline Performance

The enhanced pipelines are optimized for performance:

- **Batch Processing**: Configurable batch sizes for memory efficiency
- **Connection Pooling**: Efficient database operations
- **Memory Management**: Automatic cleanup and monitoring
- **Parallel Processing**: Multi-threaded duplicate detection
- **Caching**: Validation and duplicate detection caching

#### Pipeline Monitoring

Each pipeline provides detailed statistics:

```python
{
    'validation_pipeline': {
        'items_processed': 1500,
        'items_valid': 1250,
        'items_rejected': 250,
        'average_confidence': 0.85,
        'processing_time': 45.2
    },
    'duplicate_pipeline': {
        'items_processed': 1250,
        'duplicates_found': 125,
        'duplicates_merged': 75,
        'quality_upgrades': 50
    },
    'export_pipeline': {
        'items_exported': 1125,
        'files_created': 4,
        'database_size': '15.2MB'
    }
}
```

For detailed pipeline documentation, see [docs/ENHANCED_PIPELINES.md](docs/ENHANCED_PIPELINES.md).

### 🆕 Enhanced CMS-Specific Extractors with Validation

- **SiteVision Enhanced Extractor**: JavaScript-aware extraction with Playwright support for dynamic content
- **Municipio Enhanced Extractor**: WordPress-specific patterns with AJAX endpoint detection
- **Generic Enhanced Extractor**: Multi-strategy extraction for unknown CMS types
- **Confidence Scoring**: Each extracted fee includes confidence scores and quality indicators
- **Advanced Validation**: Comprehensive validation pipeline with Swedish-specific rules
- **Pattern Recognition**: Enhanced Swedish fee patterns and service categorization

### 🆕 Enhanced PDF Extraction Engine

- **Multi-Method Extraction**: Uses Camelot (lattice/stream), pdfplumber, and custom text patterns
- **Swedish-Optimized**: Specialized patterns for Swedish municipal documents
- **Table Detection**: Automatically identifies and extracts fee tables
- **PDF Caching**: Avoids re-downloading PDFs with intelligent caching
- **Bygglov Specialization**: Advanced extraction for building permit fees with PBL compliance

### 🏗️ Bygglov (Building Permit) Specialization

- **PBL-Compliant**: Based on Plan- och bygglagen (Swedish Planning and Building Act)
- **Area-Based Fees**: Extracts fees based on square meters (kvm/m²)
- **PBB Integration**: Handles Prisbasbelopp (Price Base Amount) calculations
- **Type Classification**: Identifies nybyggnad, tillbyggnad, ändring, rivning, etc.
- **Comprehensive Patterns**: Covers all major bygglov fee structures

## Installation

### Quick Setup (Recommended)

```bash
git clone <repository-url>
cd swedish_municipal_crawler
python setup_crawler.py
```

The setup script will automatically:
- Install system dependencies (Ghostscript, Poppler, Tesseract, Redis)
- Install Python dependencies
- Configure Playwright browsers
- Test PDF extraction capabilities
- Create necessary directories

### Testing Enhanced Extractors

```bash
# Test all enhanced extractors and validation
python test_enhanced_extractors.py

# This will test:
# - Enhanced SiteVision extractor with JavaScript support
# - Enhanced Municipio extractor with AJAX capabilities
# - Enhanced Generic extractor with multiple strategies
# - Validation pipeline with confidence scoring
# - Swedish validators
```

### Manual Installation

1. **System Dependencies**:

   **macOS (with Homebrew):**
   ```bash
   brew install ghostscript poppler tesseract redis
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y ghostscript poppler-utils tesseract-ocr redis-server python3-tk libgl1-mesa-glx
   ```

   **CentOS/RHEL/Fedora:**
   ```bash
   sudo yum install -y ghostscript poppler-utils tesseract redis tkinter
   ```

2. **Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Start Redis** (optional but recommended):
   ```bash
   # macOS
   brew services start redis
   
   # Linux
   sudo systemctl start redis-server
   ```

## Usage

### Basic Usage

Run the crawler with default settings:
```bash
python run_crawler.py
```

### Advanced Usage

```bash
# Custom municipalities file
python run_crawler.py --municipalities data/input/my_municipalities.csv

# Resume previous crawl
python run_crawler.py --resume

# Clear cache and start fresh
python run_crawler.py --clear-cache

# Debug mode with detailed PDF extraction logs
python run_crawler.py --log-level DEBUG
```

### Using Scrapy directly

```bash
# Run with Scrapy command
scrapy crawl swedish_municipal_fees

# With custom settings
scrapy crawl swedish_municipal_fees -s LOG_LEVEL=DEBUG
```

## Configuration

### Municipalities File

Create a CSV file with the following columns:
- `municipality`: Municipality name
- `url`: Official website URL
- `org_number`: Swedish organization number (optional)
- `population`: Population count (optional)

Example:
```csv
municipality,url,org_number,population
Stockholm,https://stockholm.se,212000-0142,975551
Göteborg,https://goteborg.se,212000-1355,579281
```

### Crawler Configuration

Edit `config/crawler_config.json` to customize:
- Download delays and timeouts
- CMS detection settings
- Municipality classification thresholds
- Extraction limits
- Priority URL patterns
- Fee keywords and weights

## Architecture

### Core Components

- **CMS Detector** (`extractors/cms_detector.py`): Identifies website CMS type
- **URL Prioritizer** (`utils/url_prioritizer.py`): Scores and prioritizes URLs
- **Municipality Classifier** (`utils/municipality_classifier.py`): Classifies municipalities by size
- **Page Classifier** (`crawler/ml/page_classifier.py`): ML model filtering irrelevant pages
- **Validators** (`utils/validators.py`): Validates Swedish data formats
- **Pipelines**: Data processing, validation, and export

### 🆕 Enhanced PDF Extraction Components

- **SwedishPDFExtractor** (`extractors/pdf_extractor.py`): Multi-method PDF extraction engine
- **BygglovExtractor** (`extractors/bygglov_extractor.py`): Specialized building permit extraction
- **Swedish Parser** (`utils/swedish_parser.py`): Advanced Swedish text analysis

### Machine Learning Classifier

`crawler/ml/page_classifier.py` implements a simple logistic regression model
that filters out pages unlikely to contain fee information. Train the model with:

```bash
python -m crawler.ml.train_page_classifier
```

### Data Flow

1. Load municipalities from CSV
2. Detect CMS type (with JavaScript if needed)
3. **Select appropriate enhanced extractor based on CMS**
4. Classify municipality size
5. Get priority URLs using patterns and sitemap
6. **Apply CMS-specific extraction strategies**
7. **Use JavaScript/AJAX extraction if needed**
8. Extract fees from HTML and PDFs using multiple methods
9. Apply specialized Bygglov extraction for building permits
10. **Run enhanced validation with confidence scoring**
11. **Calculate quality indicators**
12. Validate and deduplicate data
13. Export to multiple formats with enhanced metadata

## PDF Extraction Details

### Extraction Methods

1. **Camelot Lattice**: Best for tables with visible borders
2. **Camelot Stream**: For tables without borders
3. **pdfplumber**: Text extraction and table detection
4. **Custom Patterns**: Swedish-specific regex patterns

### Supported PDF Types

- **Fee Schedules**: Structured tables with services and amounts
- **Bygglov Documents**: Building permit fee schedules
- **Municipal Regulations**: Text-based fee information
- **Price Lists**: Various municipal service pricing

### Swedish-Specific Features

- **Currency Parsing**: Handles "1 250 kr", "1.250,50 kr", "SEK 1250"
- **Area Recognition**: Extracts kvm, m², BTA, BYA measurements
- **PBB Calculations**: Automatic Prisbasbelopp conversions
- **Category Classification**: Automatic fee categorization

## Output

The crawler generates several output files in `data/output/`:

- `swedish_municipal_fees_YYYYMMDD_HHMMSS.json`: Raw JSON data
- `swedish_municipal_fees_YYYYMMDD_HHMMSS.csv`: CSV format
- `swedish_municipal_fees_YYYYMMDD_HHMMSS.xlsx`: Excel with multiple sheets
- `crawl_statistics_YYYYMMDD_HHMMSS.json`: Crawl statistics
- `failed_municipalities.json`: Failed municipalities for retry
- `crawler.log`: Detailed crawl logs

### Excel Output Sheets

1. **Municipal_Fees**: All extracted fee data with enhanced metadata
2. **Municipality_Summary**: Aggregated statistics per municipality
3. **Category_Breakdown**: Fee categories and counts
4. **🆕 Bygglov_Analysis**: Building permit specific analysis

### Enhanced Data Fields

Each extracted fee now includes comprehensive metadata:

```json
{
    "fee_name": "Bygglov för enbostadshus",
    "amount": 15000,
    "currency": "SEK",
    "category": "bygglov",
    "source_url": "https://stockholm.se/avgifter",
    "source_type": "HTML",
    "extraction_method": "sitevision_enhanced",
    "extraction_date": "2024-01-15T10:30:00",
    "cms_type": "sitevision",
    "municipality": "Stockholm",
    
    // Enhanced validation metadata
    "validation": {
        "confidence_score": 0.87,
        "validation_date": "2024-01-15T10:30:00",
        "validation_version": "2.0",
        "warnings": [],
        "validation_scores": {...}
    },
    
    // Quality indicators
    "quality": {
        "overall_score": 0.85,
        "data_completeness": 0.9,
        "content_quality": 0.8,
        "source_reliability": 0.9
    },
    
    // Bygglov-specific fields (if applicable)
    "bygglov_type": "nybyggnad_enbostadshus",
    "area_based": true,
    "pbb_based": false,
    "area_range": {"type": "threshold", "value": 120}
}
```

### Enhanced Statistics

The crawler now tracks detailed extraction statistics:

```json
{
    "extraction_stats": {
        "sitevision": {
            "pages": 45,
            "fees": 234,
            "js_used": 12
        },
        "municipio": {
            "pages": 38,
            "fees": 189,
            "ajax_used": 8
        },
        "generic": {
            "pages": 67,
            "fees": 156,
            "strategies_used": 23
        },
        "pdf": {
            "processed": 89,
            "fees": 445
        },
        "bygglov": {
            "processed": 34,
            "fees": 178
        }
    },
    "validation_stats": {
        "total_processed": 1202,
        "total_valid": 1089,
        "confidence_distribution": {
            "high": 756,
            "medium": 333,
            "low": 113
        }
    }
}
```

## Resume Capability

The crawler supports resuming interrupted crawls:

```bash
# Resume previous crawl
python run_crawler.py --resume
```

Resume data is stored in `crawls/swedish_municipalities/` and includes:
- Request queue state
- Duplicate filter state
- Spider statistics
- **PDF cache state**

## Update Detection

Use the `update_checker.py` helper to find municipalities that may have
changed their fee information since the last crawl. This allows targeted
recrawling so the dataset stays fresh.

```bash
python crawler/utils/update_checker.py --db data/output/phase1_municipal_data_YYYYMMDD_HHMM.db
```

The script sends lightweight HTTP `HEAD` requests to the previously collected
source URLs and lists the pages where a newer `Last-Modified` timestamp is
observed.

## Monitoring and Logging

### Log Levels

- `DEBUG`: Detailed debugging information including PDF extraction details
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only

### Statistics

The crawler tracks:
- Total fees extracted
- Municipalities processed
- Success/failure rates
- CMS type distribution
- Category breakdown
- Validation statistics
- **PDF extraction statistics**
- **Bygglov-specific metrics**

## Troubleshooting

### Common Issues

1. **PDF Extraction Failures**:
   ```bash
   # Test PDF dependencies
   python -c "import camelot, pdfplumber, cv2; print('All PDF dependencies OK')"
   
   # Check Ghostscript installation
   gs --version
   ```

2. **Camelot Issues**:
   - Ensure Ghostscript is installed and in PATH
   - Install OpenCV: `pip install opencv-python`
   - For Linux: Install `libgl1-mesa-glx`

3. **Memory Issues with Large PDFs**:
   - PDFs over 10MB are automatically skipped
   - Increase system memory or reduce concurrent processing

4. **Swedish Character Encoding**:
   - Ensure UTF-8 encoding in all text processing
   - Check locale settings: `locale`

### Debug Mode

Run with debug logging to troubleshoot PDF extraction:
```bash
python run_crawler.py --log-level DEBUG
```

This will show detailed information about:
- PDF download and caching
- Table detection results
- Extraction method selection
- Pattern matching details

## Performance Optimization

### Recommended Settings

For large-scale crawling:
- Enable Redis caching for URL prioritization
- Use PDF caching to avoid re-downloads
- Monitor system resources during PDF processing
- Use resume capability for long crawls

### PDF Processing Optimization

- **Parallel Processing**: Multiple PDFs processed concurrently
- **Smart Caching**: PDFs cached by content hash
- **Method Selection**: Automatic fallback between extraction methods
- **Size Limits**: Large PDFs automatically skipped

## Legal and Ethical Considerations

- Respects robots.txt files
- Implements polite crawling delays
- Caches responses to minimize server load
- Provides clear user agent identification
- Follows Swedish data protection regulations
- **Respects PDF copyright and usage terms**

## Dependencies

### System Dependencies
- **Ghostscript**: PDF processing backend
- **Poppler**: PDF utilities
- **Tesseract**: OCR capabilities (future use)
- **Redis**: Caching (optional)

### Python Dependencies
- **camelot-py[cv]**: Advanced table extraction
- **pdfplumber**: PDF text and table extraction
- **opencv-python**: Image processing for Camelot
- **pandas**: Data manipulation
- **scrapy-playwright**: JavaScript rendering

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support contact information here]

## 🆕 Enhanced Extraction Architecture

### CMS-Specific Extractors

#### Enhanced SiteVision Extractor
- **JavaScript Support**: Uses Playwright for dynamic content extraction
- **Portlet Detection**: Specialized selectors for SiteVision portlets
- **Table Parsing**: Advanced table structure recognition
- **Confidence Scoring**: Calculates extraction confidence based on context
- **Validation**: Built-in Swedish content validation

```python
# Example usage
extractor = EnhancedSitevisionExtractor()

# Standard HTML extraction
fees = extractor.extract_fees_from_sitevision(response)

# JavaScript-enhanced extraction
js_fees = await extractor.extract_with_playwright(url)
```

#### Enhanced Municipio Extractor
- **WordPress Integration**: Specialized for Municipio/WordPress sites
- **Shortcode Support**: Extracts fees from WordPress shortcodes
- **AJAX Detection**: Intercepts and processes AJAX responses
- **Widget Parsing**: Extracts fees from WordPress widgets
- **Multi-format Support**: Handles various WordPress content formats

```python
# Example usage
extractor = EnhancedMunicipioExtractor()

# Standard extraction
fees = extractor.extract_fees_from_municipio(response)

# AJAX extraction
ajax_fees = await extractor.extract_with_ajax(url)
```

#### Enhanced Generic Extractor
- **Multi-Strategy Approach**: Uses multiple extraction strategies
- **Fallback Patterns**: Comprehensive fallback for unknown CMS types
- **Playwright Integration**: JavaScript support for dynamic sites
- **Adaptive Selectors**: Automatically adapts to different site structures
- **Quality Assessment**: Evaluates extraction quality and adjusts methods

```python
# Example usage
extractor = EnhancedGenericExtractor()

# Standard extraction
fees = extractor.extract_fees_generic(response)

# Multi-strategy extraction
strategy_fees = await extractor.extract_with_multiple_strategies(url)
```

### 🆕 Enhanced Validation Pipeline

The enhanced validation pipeline provides comprehensive validation with confidence scoring:

#### Validation Features
- **Multi-Rule Validation**: Weighted validation rules with configurable thresholds
- **Swedish-Specific Checks**: Validates Swedish content patterns and characteristics
- **Confidence Scoring**: Calculates overall confidence scores for extracted data
- **Quality Indicators**: Provides data completeness, content quality, and source reliability scores
- **Detailed Statistics**: Tracks validation success rates and error patterns

#### Validation Rules
1. **Required Fields**: Ensures all mandatory fields are present
2. **Amount Validation**: Validates fee amounts within reasonable ranges
3. **Fee Name Validation**: Checks for meaningful Swedish fee descriptions
4. **Currency Validation**: Validates Swedish currency formats
5. **URL Validation**: Ensures Swedish domain sources
6. **Category Validation**: Validates fee categories
7. **Swedish Content**: Validates Swedish language characteristics

```python
# Example validation result
{
    'validation': {
        'confidence_score': 0.87,
        'validation_date': '2024-01-15T10:30:00',
        'warnings': ['Content lacks Swedish characters'],
        'validation_scores': {
            'required_fields': {'is_valid': True, 'score': 1.0},
            'amount_validation': {'is_valid': True, 'score': 0.9},
            'fee_name_validation': {'is_valid': True, 'score': 0.8}
        }
    },
    'quality': {
        'overall_score': 0.85,
        'data_completeness': 0.9,
        'content_quality': 0.8,
        'source_reliability': 0.9
    }
}
```

### 🆕 Enhanced Data Flow

1. Load municipalities from CSV
2. Detect CMS type (with JavaScript if needed)
3. **Select appropriate enhanced extractor based on CMS**
4. Classify municipality size
5. Get priority URLs using patterns and sitemap
6. **Apply CMS-specific extraction strategies**
7. **Use JavaScript/AJAX extraction if needed**
8. Extract fees from HTML and PDFs using multiple methods
9. Apply specialized Bygglov extraction for building permits
10. **Run enhanced validation with confidence scoring**
11. **Calculate quality indicators**
12. Validate and deduplicate data
13. Export to multiple formats with enhanced metadata

## 🆕 Enhanced Output

### Enhanced Data Fields

Each extracted fee now includes comprehensive metadata:

```json
{
    "fee_name": "Bygglov för enbostadshus",
    "amount": 15000,
    "currency": "SEK",
    "category": "bygglov",
    "source_url": "https://stockholm.se/avgifter",
    "source_type": "HTML",
    "extraction_method": "sitevision_enhanced",
    "extraction_date": "2024-01-15T10:30:00",
    "cms_type": "sitevision",
    "municipality": "Stockholm",
    
    // Enhanced validation metadata
    "validation": {
        "confidence_score": 0.87,
        "validation_date": "2024-01-15T10:30:00",
        "validation_version": "2.0",
        "warnings": [],
        "validation_scores": {...}
    },
    
    // Quality indicators
    "quality": {
        "overall_score": 0.85,
        "data_completeness": 0.9,
        "content_quality": 0.8,
        "source_reliability": 0.9
    },
    
    // Bygglov-specific fields (if applicable)
    "bygglov_type": "nybyggnad_enbostadshus",
    "area_based": true,
    "pbb_based": false,
    "area_range": {"type": "threshold", "value": 120}
}
```

### Enhanced Statistics

The crawler now tracks detailed extraction statistics:

```json
{
    "extraction_stats": {
        "sitevision": {
            "pages": 45,
            "fees": 234,
            "js_used": 12
        },
        "municipio": {
            "pages": 38,
            "fees": 189,
            "ajax_used": 8
        },
        "generic": {
            "pages": 67,
            "fees": 156,
            "strategies_used": 23
        },
        "pdf": {
            "processed": 89,
            "fees": 445
        },
        "bygglov": {
            "processed": 34,
            "fees": 178
        }
    },
    "validation_stats": {
        "total_processed": 1202,
        "total_valid": 1089,
        "confidence_distribution": {
            "high": 756,
            "medium": 333,
            "low": 113
        }
    }
}
```

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

## 🆕 Troubleshooting Enhanced Features

### JavaScript Extraction Issues

1. **Playwright Installation**:
   ```bash
   # Ensure Playwright is properly installed
   playwright install chromium
   
   # Test Playwright
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

2. **JavaScript Timeout Issues**:
   - Increase timeout in settings: `PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT`
   - Check network connectivity
   - Monitor memory usage during extraction

### Validation Issues

1. **Low Confidence Scores**:
   - Check Swedish content patterns
   - Verify fee amount ranges
   - Review extraction method effectiveness

2. **High Validation Failure Rate**:
   - Adjust validation thresholds
   - Review Swedish-specific patterns
   - Check source URL validation rules

### Performance Optimization

1. **JavaScript Extraction**:
   - Use selectively based on CMS detection
   - Cache JavaScript results
   - Monitor browser resource usage

2. **Validation Pipeline**:
   - Adjust validation rule weights
   - Optimize Swedish pattern matching
   - Use confidence thresholds to filter low-quality data

## 🆕 Advanced Usage

### Enhanced Extraction with JavaScript

```bash
# Run with enhanced JavaScript extraction
python run_crawler.py --enable-js --log-level DEBUG

# Test specific extractor
python test_enhanced_extractors.py
```

### Validation Configuration

The validation pipeline can be configured through settings:

```python
# In settings.py
ENHANCED_VALIDATION_SETTINGS = {
    'confidence_threshold': 0.6,
    'strict_swedish_validation': True,
    'enable_quality_scoring': True,
    'validation_rules': {
        'amount_validation': {
            'min_amount': 50,
            'max_amount': 100000
        }
    }
}
```

## 🆕 Monitoring and Quality Assurance

### Enhanced Logging

The enhanced extractors provide detailed logging:

```bash
# Enable detailed extraction logging
python run_crawler.py --log-level DEBUG

# This shows:
# - CMS detection results
# - JavaScript extraction attempts
# - AJAX endpoint discoveries
# - Validation rule applications
# - Confidence score calculations
# - Quality indicator assessments
```

### Quality Metrics

Monitor extraction quality with built-in metrics:

- **Extraction Efficiency**: Fees per page by CMS type
- **Confidence Distribution**: High/medium/low confidence breakdown
- **Validation Success Rate**: Percentage of fees passing validation
- **Method Effectiveness**: Success rates by extraction method
- **JavaScript Usage**: When and how often JS extraction is used

##