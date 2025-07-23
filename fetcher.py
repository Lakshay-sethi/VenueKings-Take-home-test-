from models import Product
from typing import List
import asyncio
import httpx
from datetime import datetime
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
async def fetch_page(
    url: str, page: int, semaphore: asyncio.Semaphore
) -> List[Product]:
    """Fetches product data from the given URL and returns a list of Product models."""
    async with semaphore:  # rate limit
        await asyncio.sleep(RATE_LIMIT_DELAY)  # naive throttle
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{url}?limit={MAX_ITEMS_PER_PAGE}&skip={(page - 1) * MAX_ITEMS_PER_PAGE}"
            )
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()
            products_data = data.get("products", [])

            # Preprocess the data to handle id, source, and processed_at
            for product in products_data:
                product["id"] = str(product.get("id", ""))
                product["source"] = url
                product["processed_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            # Validate and parse the product data using the Product model
            return [Product(**product) for product in products_data]


async def fetch_all_products(url: str) -> List[Product]:
    """Fetches all products from the paginated endpoint."""
    all_products = []
    page = 1
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    # Fetch products page by page
    while True:
        products = await fetch_page(url, page, semaphore)
        if not products:
            break  # Stop if no products are returned (end of pagination)
        all_products.extend(products)
        page += 1

    return all_products


async def main():
    url = "https://dummyjson.com/products"
    try:
        products = await fetch_all_products(url)
        for product in products:
            print(product.model_dump())
    except Exception as e:
        print(f"Error fetching data: {e}")


if __name__ == "__main__":
    asyncio.run(main())
