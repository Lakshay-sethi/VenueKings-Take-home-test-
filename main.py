from processor import process_products, metrics
from fetcher import fetch_all_products
from config import BATCH_SIZE, URLS, logger
import asyncio
import time


async def main():
    """
    Main pipeline orchestrator.

    Concurrency Decision: Use asyncio for I/O-bound API fetching, then switch to
    thread pools for CPU-bound processing. This hybrid approach maximizes efficiency:
    - Async for network I/O (fetching from multiple APIs concurrently)
    - Threads for CPU work (data processing and normalization)
    """
    urls = URLS
    fetch_success = 0
    fetch_fail = 0
    start_time = time.perf_counter()
    processed_products = []

    # Concurrency Decision: Process URLs sequentially to control memory usage
    for url in urls:
        logger.info(f"Fetching products from {url}")
        try:
            # Async I/O operation
            products = await fetch_all_products(url)
            fetch_success += 1

            # Process in batches to manage memory usage with large datasets
            # Each batch uses ThreadPoolExecutor for CPU-bound processing
            for i in range(0, len(products), BATCH_SIZE):
                batch = products[i : i + BATCH_SIZE]
                batch_processed = process_products(batch)
                processed_products.extend(batch_processed)

                # Clear batch from memory
                del batch, batch_processed

        except Exception as e:
            fetch_fail += 1
            logger.error(f"Error fetching data from {url}: {e}", exc_info=True)
            continue  # Continue to next URL

    total_time = time.perf_counter() - start_time

    # Enhanced metrics reporting
    total_requests = fetch_success + fetch_fail
    fetch_success_rate = fetch_success / total_requests if total_requests > 0 else 0

    logger.info("Processing complete.")
    logger.info(
        "Enhanced Metrics: %s",
        {
            **metrics,
            "fetch_success": fetch_success,
            "fetch_fail": fetch_fail,
            "fetch_success_rate": round(fetch_success_rate, 2),
            "total_processing_time": round(total_time, 2),
            "sources": list(metrics["sources"]),
            "avg_processing_time_per_product": round(
                metrics["processing_time_seconds"] / metrics["total_products"], 4
            )
            if metrics["total_products"] > 0
            else 0,
        },
    )
    if processed_products:
        logger.info("Sample processed product: %s", processed_products[0])
    else:
        logger.warning("No products processed.")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
