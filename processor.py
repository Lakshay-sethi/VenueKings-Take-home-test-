from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from models import Product, Summary
from datetime import datetime
from collections import defaultdict
from threading import Lock
from config import MAX_WORKERS
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
    """Process products using a thread pool."""
    processed = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(normalize_product, p) for p in products]
        for f in as_completed(futures):
            result = f.result()
            if result is not None:
                processed.append(result)
    return processed
