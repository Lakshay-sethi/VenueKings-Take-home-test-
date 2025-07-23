"""
Configuration file for the VenueKings application.
Centralized configuration for tuning concurrency parameters and other settings.
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Processing Configuration
BATCH_SIZE = 100  # Process in batches for memory efficiency
MAX_WORKERS = 8  # Thread pool max workers for product processing

# Fetcher Configuration
MAX_ITEMS_PER_PAGE = 20
MAX_CONCURRENT_REQUESTS = 5
RATE_LIMIT_DELAY = 1.0 / MAX_CONCURRENT_REQUESTS
REQUEST_TIMEOUT = 10.0
MAX_RETRY_ATTEMPTS = 3
RETRY_MIN_WAIT = 1
RETRY_MAX_WAIT = 10
RETRY_MULTIPLIER = 1
MAX_PRODUCTS_LIMIT = 200  # Limit total products fetched per source

# API URLs
URLS = [
    "https://dummyjson.com/products",
    "https://jsonplaceholder.typicode.com/posts",
    "https://world.openfoodfacts.org/cgi/search.pl?action=process&json=true",
]

logger.info("Configuration loaded successfully")
