
import asyncio
import logging
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper.log", encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """
    Run only the scraping module
    """
    logger.info("Starting scraping module...")
    
    try:
        # Import the scraping utilities
        from app.scraping.utils import run_spider
        
        # Run the spider with a test query
        search_query = "lenovo thinkbook"
        logger.info(f"Running spider with search query: {search_query}")
        
        results = await run_spider(search_query)
        
        logger.info(f"Scraping completed. Found {len(results)} items.")
        
        # Print first few results as a sample
        if results:
            logger.info("Sample results:")
            for i, item in enumerate(results[:5]):
                logger.info(f"{i+1}. {item.get('title', 'N/A')} - {item.get('price', 'N/A')} - {item.get('link', 'N/A')}")
        else:
            logger.info("No results found.")
            
    except Exception as e:
        logger.error(f"Error running scraper: {e}", exc_info=True)
        return False
    
    logger.info("Scraping module finished.")
    return True

if __name__ == "__main__":
    # For Windows, set the event loop policy for asyncio
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the main function
