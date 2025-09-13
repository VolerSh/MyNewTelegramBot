import logging
from ..database.models import Product

logger = logging.getLogger(__name__)

def find_best_deals(products: list[Product]) -> list[Product]:
    """
    Analyzes a list of products and returns the best deals.
    
    The current logic is a placeholder. It just returns the products sorted by price.
    """
    logger.info(f"Analyzing {len(products)} products to find the best deals...")
    
    if not products:
        return []
        
    # Placeholder logic: sort by price, ascending.
    sorted_products = sorted(products, key=lambda p: p.price)
    
    logger.info(f"Found {len(sorted_products)} deals, sorted by price.")
    return sorted_products