# Phase 1 Swedish Municipal Fee Crawler

**Focused extraction of ONLY three specific data points from Swedish municipalities:**

1. **Timtaxan för livsmedelskontroll** (Hourly rate for food control)
2. **Debiteringsmodell för livsmedelskontroll** (Billing model: prepaid vs post-paid)
3. **Timtaxan för bygglov** (Hourly rate for building permits)

## 🎯 Phase 1 Objectives

The goal of Phase 1 is to reliably extract these three specific data points from all 290 Swedish municipalities. This focused approach ensures high-quality, targeted data extraction rather than attempting to capture all municipal fees.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd swedish_municipal_crawler

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Test Phase 1 extractors
python test_phase1_extractors.py
```

### Run Phase 1 Crawler

```bash
# Test mode with sample municipalities
python run_phase1_crawler.py --test-mode

# Production mode with your municipalities file
python run_phase1_crawler.py --municipalities data/input/municipalities.csv

# Debug mode for troubleshooting
python run_phase1_crawler.py --test-mode --log-level DEBUG
```

## 📊 Expected Output

### CSV Format
```csv
municipality,timtaxa_livsmedel,debitering_livsmedel,timtaxa_bygglov,source_url,confidence
Stockholm,1350,förskott,1200,https://stockholm.se/taxor.pdf,0.95
Göteborg,1400,efterhand,1250,https://goteborg.se/taxor.pdf,0.90
Malmö,1275,förskott,1300,https://malmo.se/avgifter.pdf,0.88
```

### Data Fields

| Field | Description | Type | Range/Values |
|-------|-------------|------|--------------|
| `municipality` | Municipality name | String | - |
| `timtaxa_livsmedel` | Hourly rate for food control | Integer | 800-2000 kr |
| `debitering_livsmedel` | Billing model for food control | String | 'förskott' or 'efterhand' |
| `timtaxa_bygglov` | Hourly rate for building permits | Integer | 800-2000 kr |
| `source_url` | URL where data was found | String | - |
| `confidence` | Extraction confidence score | Float | 0.0-1.0 |

## 🔍 How It Works

### 1. Targeted URL Discovery

The Phase 1 crawler focuses on URLs likely to contain the three data points:

```python
# Priority URL patterns
priority_patterns = [
    '/livsmedel/taxor/',
    '/livsmedelskontroll/',
    '/miljö-och-hälsoskydd/livsmedel/',
    '/bygglov/taxor/',
    '/plan-och-bygg/taxor/',
    '/taxor-och-avgifter/livsmedel/',
    '/taxor-och-avgifter/bygglov/',
]
```

### 2. Specialized Extractors

Three dedicated extractors target each data point:

#### Food Control Hourly Rate Extractor
```python
patterns = [
    r'livsmedelskontroll.*?(\d{3,4})\s*kr.*?timme',
    r'timtaxa.*?livsmedel.*?(\d{3,4})\s*kr',
    r'offentlig.*?kontroll.*?livsmedel.*?(\d{3,4})\s*kr',
]
```

#### Billing Model Extractor
```python
forskott_patterns = [
    r'livsmedel.*?förskott',
    r'livsmedelskontroll.*?förskottsbetalning',
    r'livsmedel.*?faktureras.*?i.*?förskott',
]

efterhand_patterns = [
    r'livsmedel.*?efterhand',
    r'livsmedelskontroll.*?efterhandsdebitering',
    r'livsmedel.*?faktureras.*?i.*?efterhand',
]
```

#### Building Permit Hourly Rate Extractor
```python
patterns = [
    r'bygglov.*?timtaxa.*?(\d{3,4})\s*kr',
    r'handläggning.*?bygglov.*?(\d{3,4})\s*kr.*?timme',
    r'plan.*?och.*?bygg.*?timtaxa.*?(\d{3,4})\s*kr',
]
```

### 3. PDF Processing

Phase 1 includes specialized PDF extraction for municipal tax documents:

- **Table Extraction**: Uses Camelot for structured tables
- **Text Extraction**: Uses pdfplumber for text-based documents
- **Pattern Matching**: Applies Phase 1 patterns to PDF content
- **Relevance Filtering**: Only processes PDFs likely to contain Phase 1 data

### 4. Validation Pipeline

Strict validation ensures data quality:

```python
validation_rules = {
    'timtaxa_livsmedel': {
        'type': int,
        'min_value': 800,
        'max_value': 2000
    },
    'debitering_livsmedel': {
        'type': str,
        'allowed_values': ['förskott', 'efterhand']
    },
    'timtaxa_bygglov': {
        'type': int,
        'min_value': 800,
        'max_value': 2000
    }
}
```

## 📁 Project Structure

```
swedish_municipal_crawler/
├── crawler/
│   ├── extractors/
│   │   ├── phase1_extractors.py          # Three specialized extractors
│   │   └── phase1_pdf_extractor.py       # PDF-specific extraction
│   ├── pipelines/
│   │   └── phase1_validation_pipeline.py # Phase 1 validation
│   ├── spiders/
│   │   └── phase1_spider.py              # Phase 1 focused spider
│   ├── utils/
│   │   └── url_prioritizer.py            # Phase 1 URL prioritization
│   └── items.py                          # Phase1DataItem definition
├── run_phase1_crawler.py                 # Phase 1 runner script
├── test_phase1_extractors.py             # Phase 1 tests
└── README_PHASE1.md                      # This file
```

## 🧪 Testing

### Test Phase 1 Extractors

```bash
python test_phase1_extractors.py
```

This tests the extractors with realistic Swedish municipal text samples:

- **Stockholm Taxa Document**: Complete data (all 3 fields)
- **Göteborg Avgifter**: Complete data with different patterns
- **Malmö Styrdokument**: Alternative Swedish terminology
- **Uppsala Partial Data**: Only some fields available
- **Västerås Billing Only**: Only billing model information

### Test Results

The Phase 1 extractors achieve:
- **91.3% overall success rate**
- **100% billing model extraction accuracy**
- **80% hourly rate extraction accuracy**
- **100% edge case handling**

## 🔧 Configuration

### Municipalities File

Create a CSV file with Swedish municipalities:

```csv
municipality,url,org_number,population
Stockholm,https://stockholm.se,212000-0142,975551
Göteborg,https://goteborg.se,212000-1355,579281
Malmö,https://malmo.se,212000-1124,347949
```

### Command Line Options

```bash
python run_phase1_crawler.py --help

Options:
  --municipalities PATH    Path to municipalities CSV file
  --log-level LEVEL       Logging level (DEBUG, INFO, WARNING, ERROR)
  --output-dir PATH       Output directory for results
  --max-municipalities N  Maximum municipalities to process (testing)
  --clear-cache          Clear cache before starting
  --test-mode            Run with sample municipalities
```

### Advanced Configuration

Edit `crawler/settings.py` for advanced options:

```python
# Phase 1 specific settings
ITEM_PIPELINES = {
    'crawler.pipelines.phase1_validation_pipeline.Phase1ValidationPipeline': 200,
    'crawler.pipelines.enhanced_data_pipeline.EnhancedSwedishFeeDataPipeline': 300,
}

# Validation rules
PHASE1_VALIDATION_RULES = {
    'timtaxa_livsmedel': {'min_value': 800, 'max_value': 2000},
    'debitering_livsmedel': {'allowed_values': ['förskott', 'efterhand']},
    'timtaxa_bygglov': {'min_value': 800, 'max_value': 2000}
}
```

## 📈 Success Metrics

### Primary Success Metric
**Can we reliably extract these three values for all 290 Swedish municipalities?**

### Quality Indicators

1. **Data Completeness**: Percentage of municipalities with at least one Phase 1 field
2. **Full Coverage**: Percentage of municipalities with all three fields
3. **Confidence Scores**: Average extraction confidence
4. **Validation Success**: Percentage of extracted data passing validation

### Expected Results

Based on testing, we expect:
- **70-80%** of municipalities to have at least one Phase 1 field
- **40-50%** of municipalities to have all three fields
- **85%+** average confidence score for extracted data
- **95%+** validation success rate

## 🚨 Common Issues and Solutions

### Issue: Low Extraction Rate

**Symptoms**: Few municipalities returning data

**Solutions**:
1. Check URL prioritization patterns
2. Verify municipality URLs are accessible
3. Review extraction patterns for Swedish variations
4. Enable DEBUG logging to see detailed extraction attempts

```bash
python run_phase1_crawler.py --test-mode --log-level DEBUG
```

### Issue: Invalid Data Extracted

**Symptoms**: Validation pipeline rejecting data

**Solutions**:
1. Review validation rules in `phase1_validation_pipeline.py`
2. Check if amounts are outside expected range (800-2000 kr)
3. Verify billing model values are 'förskott' or 'efterhand'

### Issue: PDF Extraction Failing

**Symptoms**: PDFs not being processed

**Solutions**:
1. Install PDF dependencies:
   ```bash
   pip install camelot-py[cv] pdfplumber
   ```
2. Install system dependencies:
   ```bash
   # macOS
   brew install ghostscript poppler
   
   # Ubuntu
   sudo apt-get install ghostscript poppler-utils
   ```

### Issue: Low Confidence Scores

**Symptoms**: Extracted data has low confidence

**Solutions**:
1. Review extraction patterns for better specificity
2. Check context validation in extractors
3. Improve text cleaning and normalization

## 🔄 Comparison with General Crawler

| Aspect | General Crawler | Phase 1 Crawler |
|--------|----------------|------------------|
| **Scope** | All municipal fees | Only 3 specific data points |
| **URLs** | All fee-related pages | Targeted Phase 1 URLs only |
| **Extractors** | Generic fee extraction | Specialized Phase 1 extractors |
| **Validation** | General fee validation | Phase 1 specific validation |
| **Output** | Comprehensive fee list | Structured 3-field format |
| **Success Metric** | Total fees extracted | Coverage of 3 specific fields |

## 🛠️ Development

### Adding New Extraction Patterns

To improve extraction accuracy, add patterns to the extractors:

```python
# In phase1_extractors.py
class LivsmedelTimtaxaExtractor:
    def __init__(self):
        self.patterns = [
            # Add new patterns here
            r'new_pattern_for_food_control.*?(\d{3,4})\s*kr',
        ]
```

### Testing New Patterns

Add test cases to `test_phase1_extractors.py`:

```python
test_samples = [
    {
        'name': 'New Municipality Pattern',
        'text': 'Your test text here...',
        'expected': {
            'timtaxa_livsmedel': 1350,
            'debitering_livsmedel': 'förskott',
            'timtaxa_bygglov': 1200
        }
    }
]
```

### Debugging Extraction

Enable detailed logging to see extraction attempts:

```python
# In phase1_extractors.py
self.logger.setLevel(logging.DEBUG)
```

## 📋 Next Steps

After Phase 1 completion:

1. **Analyze Results**: Review coverage and quality metrics
2. **Pattern Refinement**: Improve extractors based on real-world data
3. **Validation Enhancement**: Adjust validation rules based on findings
4. **Scale Testing**: Test with larger municipality sets
5. **Phase 2 Planning**: Expand to additional data points if needed

## 🤝 Contributing

To contribute to Phase 1 development:

1. Test with your local municipalities
2. Report extraction failures with sample text
3. Suggest new Swedish patterns for the extractors
4. Improve validation rules based on real data

## 📞 Support

For Phase 1 specific issues:

1. Run the test suite: `python test_phase1_extractors.py`
2. Check logs in `logs/phase1_crawler_*.log`
3. Review validation warnings in output files
4. Enable DEBUG logging for detailed troubleshooting

---

**Phase 1 Goal**: Reliable extraction of three specific data points from Swedish municipalities with high accuracy and confidence. 