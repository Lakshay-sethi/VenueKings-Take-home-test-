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


# Concurrency Decision: Use asyncio.Semaphore to limit concurrent requests
# This prevents overwhelming target APIs and respects rate limits
# MAX_CONCURRENT_REQUESTS controls how many requests run simultaneously
circuit_breakers = {}


@retry(
    wait=wait_exponential(
        multiplier=RETRY_MULTIPLIER, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT
    ),
    stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
)
async def fetch_page(url: str, page: int, semaphore: asyncio.Semaphore) -> List[Dict]:
    """
    Fetch a single page of products with concurrency control.

    Concurrency Decision: Each request acquires a semaphore slot before executing.
    This ensures we never exceed MAX_CONCURRENT_REQUESTS simultaneous HTTP calls,
    preventing API rate limit violations and resource exhaustion.
    """
    async with semaphore:  # Acquire semaphore slot - blocks if limit reached
        # Rate limiting
        await asyncio.sleep(RATE_LIMIT_DELAY)

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
    """
    Fetches all products from the paginated endpoint.

    Concurrency Decision: Create semaphore here and pass to all page requests.
    This allows multiple pages to be fetched concurrently while still respecting
    the overall concurrency limit across all endpoints.
    """
    all_products = []
    page = 1
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    # Get or create a circuit breaker for this URL
    cb = circuit_breakers.setdefault(
        url, SimpleCircuitBreaker(fail_threshold=3, reset_timeout=60)
    )
    while True:
        # Circuit breaker check before attempting request
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
