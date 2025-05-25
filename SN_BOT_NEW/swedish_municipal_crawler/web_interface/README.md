# Phase 1 Web Interface

A comprehensive web dashboard for viewing and analyzing Phase 1 Swedish municipal data, focusing on three specific data points:

1. **Timtaxan för livsmedelskontroll** (Hourly rate for food control)
2. **Debiteringsmodell för livsmedelskontroll** (Billing model: prepaid vs post-paid)
3. **Timtaxan för bygglov** (Hourly rate for building permits)

## Features

### 📊 Dashboard Overview
- **Real-time Statistics**: Total municipalities, completion rates, data quality metrics
- **Field Coverage Analysis**: Visual progress bars showing data coverage for each field
- **Quality Distribution**: Breakdown of data quality across municipalities
- **Last Updated**: Timestamp of most recent data extraction

### 📈 Data Visualization
- **Timtaxa Comparison Chart**: Interactive bar chart comparing hourly rates across municipalities
- **Billing Model Distribution**: Pie chart showing förskott vs efterhand distribution
- **Top 10 Lists**: Highest and lowest timtaxa rates for both livsmedel and bygglov
- **Responsive Charts**: Built with Chart.js for interactive data exploration

### 📋 Data Management
- **Searchable Data Table**: Filter and sort all municipality data
- **Status Filtering**: View complete, partial, or all data entries
- **Missing Data Analysis**: Identify municipalities lacking specific data points
- **Source Tracking**: Direct links to original data sources

### 📤 Export Capabilities
- **Excel Export**: Multi-sheet workbook with data, summary, and missing data analysis
- **CSV Export**: Clean CSV format for further analysis
- **JSON Export**: Structured data for API integration
- **Real-time Generation**: All exports generated on-demand with current data

## Installation

### Prerequisites
- Python 3.8+
- Phase 1 crawler data (run the crawler first)

### Setup
1. **Install Dependencies**:
   ```bash
   cd web_interface
   pip install -r requirements.txt
   ```

2. **Generate Phase 1 Data** (if not already done):
   ```bash
   cd ..
   python run_phase1_crawler.py --test-mode
   ```

3. **Start Web Interface**:
   ```bash
   cd web_interface
   python run_phase1_web.py
   ```

## Usage

### Starting the Web Interface

#### Basic Usage
```bash
python run_phase1_web.py
```
Access at: http://127.0.0.1:5001

#### Custom Configuration
```bash
# Custom host and port
python run_phase1_web.py --host 0.0.0.0 --port 8080

# Debug mode (for development)
python run_phase1_web.py --debug

# Skip dependency checks
python run_phase1_web.py --skip-checks
```

### Dashboard Sections

#### 1. Overview Cards
- **Total Municipalities**: Number of municipalities processed
- **Complete Data**: Municipalities with all 3 Phase 1 fields
- **Partial Data**: Municipalities with 1-2 Phase 1 fields
- **Last Updated**: Most recent data extraction date

#### 2. Field Coverage Analysis
Visual progress bars showing:
- Timtaxa Livsmedel coverage percentage
- Debitering Model coverage percentage
- Timtaxa Bygglov coverage percentage

#### 3. Interactive Charts
- **Timtaxa Comparison**: Side-by-side comparison of hourly rates
- **Billing Model Distribution**: Pie chart of förskott vs efterhand

#### 4. Top Lists
- Top 10 highest Timtaxa Livsmedel rates
- Top 10 highest Timtaxa Bygglov rates

#### 5. Municipality Data Table
- Searchable and sortable table
- Status filtering (complete/partial)
- Quality indicators and completeness scores
- Direct links to source documents

#### 6. Missing Data Analysis
- Municipalities missing each specific field
- Municipalities missing all data
- Source information for follow-up

### Export Functions

#### Excel Export
- **Main Data Sheet**: All municipality data
- **Summary Sheet**: Coverage statistics and averages
- **Missing Data Sheet**: Analysis of data gaps

#### CSV Export
- Clean, structured data suitable for analysis
- All Phase 1 fields included

#### JSON Export
- Structured data for API integration
- Maintains data types and relationships

## API Endpoints

The web interface provides several API endpoints for programmatic access:

### Overview Data
```
GET /api/phase1/overview
```
Returns summary statistics and coverage information.

### Municipality Data
```
GET /api/phase1/municipalities
GET /api/phase1/municipalities?status=complete
GET /api/phase1/municipalities?search=stockholm
```
Returns municipality data with optional filtering.

### Comparison Data
```
GET /api/phase1/comparison
```
Returns data formatted for charts and visualizations.

### Missing Data Analysis
```
GET /api/phase1/missing-data
```
Returns municipalities missing specific data points.

### Data Export
```
GET /api/phase1/export/excel
GET /api/phase1/export/csv
GET /api/phase1/export/json
```
Downloads data in specified format.

### Municipality Details
```
GET /api/phase1/municipality/<municipality_name>
```
Returns detailed information for a specific municipality.

## Technical Details

### Architecture
- **Backend**: Flask web framework
- **Database**: SQLite (from Phase 1 pipeline)
- **Frontend**: Bootstrap 5 + Chart.js + DataTables
- **Data Processing**: Pandas for analysis and export

### File Structure
```
web_interface/
├── phase1_app.py              # Main Flask application
├── run_phase1_web.py          # Startup script
├── requirements.txt           # Python dependencies
├── templates/
│   └── phase1_dashboard.html  # Main dashboard template
└── README.md                  # This file
```

### Data Sources
The web interface automatically detects and uses the most recent:
- Phase 1 database file (`phase1_municipal_data_*.db`)
- Phase 1 statistics file (`phase1_statistics_*.json`)

### Performance Considerations
- **Caching**: Database connections are opened per request
- **Pagination**: DataTables handles large datasets efficiently
- **Responsive Design**: Works on desktop and mobile devices
- **Lazy Loading**: Charts and data load asynchronously

## Troubleshooting

### Common Issues

#### "No Phase 1 data found"
**Solution**: Run the Phase 1 crawler first:
```bash
python run_phase1_crawler.py --test-mode
```

#### Missing Dependencies
**Solution**: Install required packages:
```bash
pip install -r web_interface/requirements.txt
```

#### Port Already in Use
**Solution**: Use a different port:
```bash
python run_phase1_web.py --port 8080
```

#### Database Connection Errors
**Solution**: Ensure the database file exists and is readable:
```bash
ls -la ../data/output/phase1_municipal_data_*.db
```

### Debug Mode
For development and troubleshooting:
```bash
python run_phase1_web.py --debug
```

This enables:
- Detailed error messages
- Automatic reloading on code changes
- Flask debug toolbar

## Development

### Adding New Features

#### New API Endpoint
1. Add route to `phase1_app.py`
2. Implement data processing logic
3. Return JSON response

#### New Dashboard Section
1. Add HTML section to `phase1_dashboard.html`
2. Create JavaScript function to load data
3. Style with CSS classes

#### New Export Format
1. Add format handling to `export_data()` function
2. Implement format-specific processing
3. Add export button to dashboard

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for functions
- Handle errors gracefully

## Security Considerations

### Production Deployment
- **Secret Key**: Change the Flask secret key
- **HTTPS**: Use HTTPS in production
- **Access Control**: Implement authentication if needed
- **Input Validation**: All user inputs are validated

### Data Privacy
- No personal data is stored or displayed
- Only municipal fee information is processed
- Source URLs are preserved for transparency

## License

This web interface is part of the Swedish Municipal Fee Crawler project and follows the same license terms.

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section above
2. Review the main project documentation
3. Create an issue with detailed information about the problem

---

**Phase 1 Web Interface** - Professional visualization and analysis of Swedish municipal fee data. 