#!/usr/bin/env python3
"""
Phase 1 Crawler Runner
Runs the Phase 1 focused crawler that extracts ONLY:
1. Timtaxan för livsmedelskontroll (Hourly rate for food control)
2. Debiteringsmodell för livsmedelskontroll (Billing model: prepaid vs post-paid)
3. Timtaxan för bygglov (Hourly rate for building permits)
"""

import argparse
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging(log_level='INFO'):
    """Setup logging configuration"""
    log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    
    # Create logs directory
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f'phase1_crawler_{timestamp}.log'
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import scrapy
    except ImportError:
        missing_deps.append('scrapy')
    
    try:
        import camelot
        import pdfplumber
    except ImportError:
        missing_deps.append('camelot-py[cv] and pdfplumber (for PDF extraction)')
    
    try:
        import pandas
        import openpyxl
    except ImportError:
        missing_deps.append('pandas and openpyxl (for Excel export)')
    
    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    return True

def create_sample_municipalities_file():
    """Create a sample municipalities file for Phase 1 testing"""
    municipalities_file = project_root / 'data' / 'input' / 'phase1_municipalities.csv'
    municipalities_file.parent.mkdir(parents=True, exist_ok=True)
    
    if municipalities_file.exists():
        return municipalities_file
    
    # Sample municipalities for Phase 1 testing
    sample_data = """municipality,url,org_number,population
Stockholm,https://stockholm.se,212000-0142,975551
Göteborg,https://goteborg.se,212000-1355,579281
Malmö,https://malmo.se,212000-1124,347949
Uppsala,https://uppsala.se,212000-2817,230767
Västerås,https://vasteras.se,212000-0100,154049
Örebro,https://orebro.se,212000-0142,156381
Linköping,https://linkoping.se,212000-0142,164616
Helsingborg,https://helsingborg.se,212000-1281,149280
Jönköping,https://jonkoping.se,212000-0142,141081
Norrköping,https://norrkoping.se,212000-0100,143171"""
    
    with open(municipalities_file, 'w', encoding='utf-8') as f:
        f.write(sample_data)
    
    print(f"Created sample municipalities file: {municipalities_file}")
    return municipalities_file

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Phase 1 Swedish Municipal Fee Crawler - Extracts only 3 specific data points'
    )
    
    parser.add_argument(
        '--municipalities-file',
        default='data/input/municipalities_full.csv',
        help='Path to municipalities CSV file'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/output',
        help='Output directory for results'
    )
    
    parser.add_argument(
        '--max-municipalities',
        type=int,
        default=None,
        help='Maximum number of municipalities to process (for testing)'
    )
    
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear HTTP and PDF cache before starting'
    )
    
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Run in test mode with sample municipalities'
    )
    
    parser.add_argument(
        '--test-pipelines',
        action='store_true',
        help='Test Phase 1 pipeline components before running crawler'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_file = setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("=== Phase 1 Swedish Municipal Fee Crawler ===")
    logger.info("Extracting ONLY three specific data points:")
    logger.info("1. Timtaxan för livsmedelskontroll (Hourly rate for food control)")
    logger.info("2. Debiteringsmodell för livsmedelskontroll (Billing model)")
    logger.info("3. Timtaxan för bygglov (Hourly rate for building permits)")
    logger.info("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Missing required dependencies. Please install them first.")
        return 1
    
    # Test pipelines if requested
    if args.test_pipelines:
        logger.info("Testing Phase 1 pipeline components...")
        try:
            from test_phase1_pipelines import Phase1PipelineTester
            tester = Phase1PipelineTester()
            test_result = tester.run_all_tests()
            
            if test_result == 0:
                logger.info("✓ All pipeline tests passed!")
                if not args.test_mode:
                    logger.info("Pipeline tests completed. Use other options to run the crawler.")
                    return 0
            else:
                logger.error("✗ Some pipeline tests failed!")
                return 1
        except ImportError as e:
            logger.error(f"Could not import pipeline tests: {e}")
            return 1
    
    # Handle test mode
    if args.test_mode:
        municipalities_file = create_sample_municipalities_file()
    else:
        municipalities_file = Path(args.municipalities_file)
        if not municipalities_file.exists():
            logger.error(f"Municipalities file not found: {municipalities_file}")
            logger.info("Use --test-mode to create a sample file, or provide a valid file path")
            return 1
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Clear cache if requested
    if args.clear_cache:
        logger.info("Clearing cache...")
        cache_dirs = [
            project_root / 'data' / 'cache',
            project_root / '.scrapy'
        ]
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
                logger.info(f"Cleared cache: {cache_dir}")
    
    # Get Scrapy settings
    settings = get_project_settings()
    
    # Override settings for Phase 1
    settings.update({
        'LOG_LEVEL': args.log_level,
        'LOG_FILE': str(log_file),
        'ITEM_PIPELINES': {
            'crawler.pipelines.phase1_enhanced_validation_pipeline.Phase1EnhancedValidationPipeline': 100,
            'crawler.pipelines.phase1_duplicate_pipeline.Phase1DuplicatesPipeline': 200,
            'crawler.pipelines.phase1_data_pipeline.Phase1DataPipeline': 300,
        },
        'PHASE1_DATA_PIPELINE_SETTINGS': {
            'output_directory': str(output_dir)
        }
    })
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
    # Add Phase 1 spider
    spider_kwargs = {
        'municipalities_file': str(municipalities_file)
    }
    
    if args.max_municipalities:
        spider_kwargs['max_municipalities'] = args.max_municipalities
    
    logger.info(f"Starting Phase 1 crawler with municipalities file: {municipalities_file}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Log file: {log_file}")
    
    try:
        # Start crawling
        process.crawl('phase1_municipal_fees', **spider_kwargs)
        process.start()
        
        logger.info("Phase 1 crawling completed successfully!")
        
        # Show output files
        output_files = list(output_dir.glob('*'))
        if output_files:
            logger.info("Generated output files:")
            for file_path in sorted(output_files):
                logger.info(f"  - {file_path}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Crawling interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Crawling failed: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 