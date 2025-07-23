from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from models import Product
from datetime import datetime
from threading import Lock
from config import MAX_WORKERS, logger
import time

# Enhanced metrics dictionary and lock
metrics = {
    "total_products": 0,
    "successful_products": 0,
    "failed_products": 0,
    "processing_time_seconds": 0.0,
    "success_rate": 1.0,
    "sources": set(),
}
metrics_lock = Lock()


def normalize_product(product: Dict) -> Product:
    """Further normalizes and enriches a product."""
    global metrics

    start_time = time.perf_counter()

    try:
        # Preprocess the data to handle id, source, and processed_at
        product["id"] = str(product.get("id", ""))
        product["title"] = product.get("title", "Unknown")
        if product.get("userId") is not None:
            product["source"] = "https://jsonplaceholder.typicode.com/posts"
        elif product.get("warrantyInformation") is not None:
            product["source"] = "https://dummyjson.com/products"
        else:
            product["source"] = "https://world.openfoodfacts.org/"

        product["price"] = float(product.get("price", 0.0))
        product["category"] = product.get("category", "Unknown")
        product["processed_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        ans = Product(**product)

        end_time = time.perf_counter()
        processing_time = end_time - start_time

        # Update metrics for successful processing
        with metrics_lock:
            metrics["total_products"] += 1
            metrics["successful_products"] += 1
            metrics["sources"].add(product["source"])
            metrics["processing_time_seconds"] += processing_time
            metrics["success_rate"] = (
                metrics["successful_products"] / metrics["total_products"]
            )

        return ans

    except Exception as e:
        end_time = time.perf_counter()
        processing_time = end_time - start_time

        # Update metrics for failed processing
        with metrics_lock:
            metrics["total_products"] += 1
            metrics["failed_products"] += 1
            metrics["processing_time_seconds"] += processing_time
            metrics["success_rate"] = (
                metrics["successful_products"] / metrics["total_products"]
            )

        print(f"Failed to process product: {e}")
        return None


def process_products(
    products: List[Dict], max_workers: int = MAX_WORKERS
) -> List[Product]:
    """
    Process products concurrently using thread pool.

    Concurrency Decision: Use ThreadPoolExecutor instead of asyncio for CPU-bound work.
    Data normalization, validation, and transformation are CPU-intensive operations
    that benefit from true parallelism rather than async concurrency.

    Why threads over async here:
    - normalize_product() is CPU-bound (parsing, validation, transformation)
    - No I/O operations that would benefit from async
    - ThreadPoolExecutor provides true parallelism for CPU work
    - GIL is released during C extensions (like JSON parsing, datetime operations)
    """
    processed_products = []

    # Use ThreadPoolExecutor for CPU-bound product normalization
    # max_workers controls how many products are processed simultaneously
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all products for processing - returns Future objects immediately
        future_to_product = {
            executor.submit(normalize_product, product): product for product in products
        }

        # Process completed futures as they finish (not in submission order)
        # as_completed() yields futures as soon as they complete
        for future in as_completed(future_to_product):
            try:
                result = future.result()  # Get the processed Product or None
                if result:
                    processed_products.append(result)

                    # Thread-safe metrics update using lock
                    with metrics_lock:
                        metrics["successful_products"] += 1

            except Exception as e:
                # Handle individual product processing failures gracefully
                with metrics_lock:
                    metrics["failed_products"] += 1
                logger.error(f"Product processing failed: {e}")

    return processed_products
