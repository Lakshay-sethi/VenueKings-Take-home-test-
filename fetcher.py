from typing import List, Dict
import asyncio
import httpx
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)
from config import (
    MAX_ITEMS_PER_PAGE,
    MAX_CONCURRENT_REQUESTS,
    RATE_LIMIT_DELAY,
    REQUEST_TIMEOUT,
    MAX_RETRY_ATTEMPTS,
    RETRY_MIN_WAIT,
    RETRY_MAX_WAIT,
    RETRY_MULTIPLIER,
    MAX_PRODUCTS_LIMIT,
    logger,
)
from circuit_breaker import SimpleCircuitBreaker


@retry(
    wait=wait_exponential(
        multiplier=RETRY_MULTIPLIER, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT
    ),
    stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
    retry=retry_if_exception_type(httpx.RequestError),
)
async def fetch_page(url: str, page: int, semaphore: asyncio.Semaphore) -> List[Dict]:
    """Fetches product data from the given URL and returns a list of response dicts."""
    async with semaphore:  # rate limit
        await asyncio.sleep(RATE_LIMIT_DELAY)  # naive throttle
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(
                f"{url}?limit={MAX_ITEMS_PER_PAGE}&skip={(page - 1) * MAX_ITEMS_PER_PAGE}"
            )
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()
            if "products" in data:
                products_data = data.get("products", [])
            else:
                products_data = data

            return products_data


# Maintain a circuit breaker per URL
circuit_breakers = {}


async def fetch_all_products(url: str) -> List[Dict]:
    """Fetches all products from the paginated endpoint."""
    all_products = []
    page = 1
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    # Get or create a circuit breaker for this URL
    cb = circuit_breakers.setdefault(
        url, SimpleCircuitBreaker(fail_threshold=3, reset_timeout=60)
    )
    while True:
        if not cb.allow_request():
            logger.warning(f"Circuit breaker OPEN for {url}. Skipping fetch.")
            break
        try:
            products = await fetch_page(url, page, semaphore)
            cb.record_success()
        except Exception as e:
            cb.record_failure()
            logger.error(f"Failed to fetch page {page} from {url}: {e}", exc_info=True)
            break  # Stop fetching further pages for this URL
        if not products or len(all_products) > MAX_PRODUCTS_LIMIT:
            break
        all_products.extend(products)
        page += 1

    return all_products
