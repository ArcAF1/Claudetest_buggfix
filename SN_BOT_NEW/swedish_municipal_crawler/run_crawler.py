#!/usr/bin/env python3
"""
Swedish Municipal Fee Crawler Runner
Enhanced crawler with CMS detection, JavaScript rendering, and resume capability
"""

import os
import sys
import argparse
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.spiders.municipal_spider import SwedishMunicipalSpider

def setup_logging(log_level='INFO'):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('data/output/crawler.log')
        ]
    )

def main():
    """Main function to run the crawler"""
    parser = argparse.ArgumentParser(description='Swedish Municipal Fee Crawler')
    parser.add_argument('--municipalities', 
                       default='data/input/municipalities.csv',
                       help='Path to municipalities CSV file')
    parser.add_argument('--log-level', 
                       default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--resume', 
                       action='store_true',
                       help='Resume previous crawl')
    parser.add_argument('--clear-cache', 
                       action='store_true',
                       help='Clear HTTP cache before starting')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Clear cache if requested
    if args.clear_cache:
        import shutil
        cache_dir = 'data/cache'
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            logger.info("Cleared HTTP cache")
    
    # Check if municipalities file exists
    if not os.path.exists(args.municipalities):
        logger.error(f"Municipalities file not found: {args.municipalities}")
        sys.exit(1)
    
    # Get project settings
    settings = get_project_settings()
    
    # Override settings based on arguments
    if args.log_level:
        settings.set('LOG_LEVEL', args.log_level)
    
    if not args.resume:
        # Clear job directory for fresh start
        jobdir = settings.get('JOBDIR')
        if jobdir and os.path.exists(jobdir):
            import shutil
            shutil.rmtree(jobdir)
            logger.info("Cleared job directory for fresh start")
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
    # Add spider with custom arguments
    process.crawl(SwedishMunicipalSpider, municipalities_file=args.municipalities)
    
    logger.info("Starting Swedish Municipal Fee Crawler...")
    logger.info(f"Municipalities file: {args.municipalities}")
    logger.info(f"Resume mode: {args.resume}")
    logger.info(f"Log level: {args.log_level}")
    
    # Start crawling
    process.start()

if __name__ == '__main__':
    main() 