from typing import List, Dict
import asyncio
import httpx
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)

MAX_ITEMS_PER_PAGE = 20
MAX_CONCURRENT_REQUESTS = 5
RATE_LIMIT_DELAY = 1.0 / MAX_CONCURRENT_REQUESTS


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(httpx.RequestError),
)
async def fetch_page(url: str, page: int, semaphore: asyncio.Semaphore) -> List[Dict]:
    """Fetches product data from the given URL and returns a list of response dicts."""
    async with semaphore:  # rate limit
        await asyncio.sleep(RATE_LIMIT_DELAY)  # naive throttle
        async with httpx.AsyncClient(timeout=10.0) as client:
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


async def fetch_all_products(url: str) -> List[Dict]:
    """Fetches all products from the paginated endpoint."""
    all_products = []
    page = 1
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    # Fetch products page by page
    while True:
        products = await fetch_page(url, page, semaphore)
        if not products or len(all_products) > 200:
            break  # Stop if no products are returned (end of pagination)
        all_products.extend(products)
        page += 1

    return all_products
