from models import Product
from typing import List
import asyncio
import httpx
from datetime import datetime


async def fetch_page(url: str) -> List[Product]:
    """Fetches product data from the given URL and returns a list of Product models."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
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


async def main():
    url = "https://dummyjson.com/products?limit=20"
    try:
        products = await fetch_page(url)
        for product in products:
            print(product.model_dump())
    except Exception as e:
        print(f"Error fetching data: {e}")


if __name__ == "__main__":
    asyncio.run(main())
