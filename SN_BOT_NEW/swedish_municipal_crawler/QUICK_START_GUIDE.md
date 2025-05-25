# Phase 1 System - Quick Start Guide

## 🚀 One-Command Deployment

The Phase 1 Swedish Municipal Fee Crawler system can be deployed with a single command using the comprehensive starter script.

## 📋 Prerequisites

- **Python 3.8+**
- **Required packages** (will be checked automatically)

## ⚡ Quick Start (Recommended)

For first-time users, start with test data:

```bash
python start_phase1_system.py --quick-start
```

This will:
1. ✅ Check system requirements
2. 🧪 Test all pipeline components
3. 🕷️ Run crawler with sample municipalities
4. 🌐 Launch web interface at http://127.0.0.1:5001
5. 🌐 Open browser automatically

## 🎯 Available Commands

### Quick Start (Test Data)
```bash
python start_phase1_system.py --quick-start
```
Perfect for testing and demonstration.

### Full Crawl (Real Data)
```bash
# Full crawl (all municipalities)
python start_phase1_system.py --full-crawl

# Limited crawl (for testing)
python start_phase1_system.py --full-crawl --max-municipalities 50
```

### Web Interface Only
```bash
# Start web interface with existing data
python start_phase1_system.py --web-only

# Custom configuration
python start_phase1_system.py --web-only --host 0.0.0.0 --port 8080 --debug
```

## 🎨 Web Interface Features

Once running, the web interface provides:

- **📊 Overview Dashboard** - Key metrics and completion rates
- **📈 Interactive Charts** - Timtaxa comparison and billing distribution
- **📋 Data Table** - Searchable, sortable municipality data
- **📤 Export Options** - Excel, CSV, and JSON downloads
- **🔍 Missing Data Analysis** - Identify gaps for follow-up

## 🛠️ Manual Components

If you prefer to run components separately:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Phase 1 Crawler
```bash
python run_phase1_crawler.py --test-mode
```

### 3. Start Web Interface
```bash
cd web_interface
python run_phase1_web.py
```

## 📊 What You'll See

### Dashboard Overview
- **Total Municipalities**: Number processed
- **Complete Data**: Municipalities with all 3 Phase 1 fields
- **Partial Data**: Municipalities with 1-2 fields
- **Field Coverage**: Visual progress bars

### Interactive Visualizations
- **Timtaxa Comparison Chart**: Bar chart comparing hourly rates
- **Billing Model Distribution**: Pie chart (förskott vs efterhand)
- **Top 10 Lists**: Highest rates by category

### Data Management
- **Search & Filter**: Find specific municipalities
- **Export Functions**: Download data in multiple formats
- **Missing Data Analysis**: See what needs follow-up

## 🎯 Phase 1 Data Points

The system focuses exclusively on three specific data points:

1. **Timtaxan för livsmedelskontroll** (Hourly rate for food control)
2. **Debiteringsmodell för livsmedelskontroll** (Billing model: prepaid vs post-paid)
3. **Timtaxan för bygglov** (Hourly rate for building permits)

## 🔧 Troubleshooting

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
python start_phase1_system.py --quick-start --port 8080
```

### No Data Found
Run the crawler first:
```bash
python start_phase1_system.py --quick-start
```

### Permission Issues
Ensure you have write permissions in the project directory.

## 🛑 Stopping the System

Press **Ctrl+C** to gracefully stop all services. The system will:
1. Stop the web interface
2. Clean up running processes
3. Save any pending data

## 📈 Success Metrics

After running, you'll see:
- **Total municipalities processed**
- **Data completion rates**
- **Quality distribution**
- **Field coverage statistics**

## 🎉 Next Steps

1. **Explore the Dashboard** - Navigate through different sections
2. **Export Data** - Download results for analysis
3. **Review Missing Data** - Identify municipalities needing follow-up
4. **Run Full Crawl** - Process all Swedish municipalities

## 💡 Tips

- **Start with Quick Start** for first-time use
- **Use Limited Crawl** for testing (--max-municipalities 50)
- **Check System Status** regularly in the logs
- **Export Data** regularly for backup

---

**🎯 Phase 1 System** - Professional Swedish municipal data extraction and analysis. 