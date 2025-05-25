# Phase 1 Swedish Municipal Crawler - GUI Version

## 🎯 Quick Start

**Just double-click `START_PHASE1_GUI.command` and you're ready to go!**

The GUI version provides a beautiful web interface where you can:
- ✅ **Start crawling with one click**
- 📊 **Monitor progress in real-time**
- 📝 **View live logs**
- 📈 **Visualize data with charts**
- 💾 **Export results in multiple formats**

## 🚀 How to Use

### 1. Launch the GUI
```bash
# On macOS/Linux - just double-click:
./START_PHASE1_GUI.command

# Or run manually:
chmod +x START_PHASE1_GUI.command
./START_PHASE1_GUI.command
```

### 2. Open Your Browser
The script will automatically tell you the URL, typically:
```
http://127.0.0.1:5001
```

### 3. Start Crawling
1. **Choose your mode:**
   - **Test Mode**: 10 municipalities (quick test)
   - **Quick Mode**: 50 municipalities (medium run)
   - **Full Mode**: All municipalities (complete crawl)

2. **Click "Start Crawling"**

3. **Watch the magic happen:**
   - Real-time progress bar
   - Live log messages
   - Status updates

### 4. View Results
- **Interactive charts** showing timtaxa comparisons
- **Data table** with sorting and filtering
- **Missing data analysis**
- **Export options** (Excel, CSV, JSON)

## 🎛️ Dashboard Features

### Crawler Control Panel
- **Start/Stop buttons** with real-time status
- **Progress monitoring** with percentage and status
- **Live log viewer** with color-coded messages
- **Mode selection** (test/quick/full)

### Data Visualization
- **Overview cards** with key metrics
- **Field coverage bars** showing data completeness
- **Comparison charts** for timtaxa analysis
- **Top 10 lists** for highest rates
- **Missing data analysis** by field

### Export & Analysis
- **Excel export** with multiple sheets and statistics
- **CSV export** for data analysis
- **JSON export** for developers
- **Interactive data table** with search and filters

## 🔧 Technical Details

### What It Crawls
The Phase 1 system focuses on three specific data points:
1. **Timtaxa Livsmedel** (Hourly rate for food control)
2. **Debitering Model** (Billing model: prepaid vs post-paid)
3. **Timtaxa Bygglov** (Hourly rate for building permits)

### Architecture
- **Frontend**: Bootstrap 5 + Chart.js + DataTables
- **Backend**: Flask REST API
- **Crawler**: Scrapy with specialized extractors
- **Database**: SQLite with multiple tables
- **Export**: Pandas + OpenPyXL

### Data Quality
- **Confidence scoring** for each extracted value
- **Completeness tracking** per municipality
- **Duplicate detection** and quality-based deduplication
- **Source validation** and URL tracking

## 🛠️ Troubleshooting

### Port Already in Use
If you see "Port 5001 is already in use":
```bash
# Kill any existing process on port 5001
lsof -ti:5001 | xargs kill -9
```

### Missing Dependencies
If you get import errors:
```bash
# Install dependencies
python3 install_dependencies.py
# Or manually:
pip install -r requirements.txt
```

### Browser Not Opening
The script doesn't auto-open your browser. Manually navigate to:
```
http://127.0.0.1:5001
```

## 📊 Sample Output

After running, you'll see:
- **10 municipalities** in test mode with realistic demo data
- **70% completion rate** (7 complete, 3 partial)
- **Interactive visualizations** of the data
- **Professional export files** ready for analysis

## 🎉 Why This is Better

**Before**: Complex command-line interfaces, multiple scripts, manual data handling

**Now**: 
- ✅ **One-click startup**
- ✅ **Beautiful web interface**
- ✅ **Real-time monitoring**
- ✅ **Professional visualizations**
- ✅ **Easy data export**
- ✅ **No technical knowledge required**

Just click and crawl! 🕷️✨ 