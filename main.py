from processor import process_products, metrics
from fetcher import fetch_all_products
import asyncio


async def main():
    urls = [
        "https://dummyjson.com/products",
        "https://jsonplaceholder.typicode.com/posts",
        "https://world.openfoodfacts.org/cgi/search.pl?action=process&json=true",
    ]
    all_products = []
    for url in urls:
        print(f"Fetching products from {url}")
        try:
            products = await fetch_all_products(url)
            all_products.extend(products)
        except Exception as e:
            print(f"Error fetching data: {e}")

    # === New: Data Processing Stage ===
    processed_products = process_products(all_products)
    # print(processed_products[:5])  # Print first 5 processed products for brevity
    print("Processing complete.\n")
    print("Metrics:", metrics)
    print(
        "Sample processed product:",
        processed_products[0] if processed_products else "None",
    )


if __name__ == "__main__":
    asyncio.run(main())
