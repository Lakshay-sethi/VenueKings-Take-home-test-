# VenueKings Product Data Pipeline

A robust, async Python pipeline for fetching, processing, and normalizing product data from multiple APIs with built-in resilience patterns.

## Architecture Overview

This pipeline fetches product data from multiple APIs concurrently using `asyncio` for network I/O and applies a circuit breaker to each endpoint for resilience. Data is processed in batches using a thread pool for efficient CPU-bound normalization and validation. The system is modular, with separate components for fetching, processing, and error handling, and includes robust logging, metrics, and test coverage. Partial failures are isolated, and the pipeline continues processing remaining data sources

## Library's

**pytest & pytest-asyncio** are the defacto standard for python testing, have more experince in it.

**httpx** because it has a UX similar to requests, can handle sync and async mode both, no need to segregate logic between sync and async.
Had to implement my own circuit breaker logic (very basic)

**tenacity** because it allows for granular control then backoff, great for defining custom rules.
It give me ready to use logic for retrying.

**concurrent.futures** because its very good for parallel execution of CPU heavy task of this scale, considered multiprocessing, but it has a higher overhead, not suitable for this task.

## Assumptions

From the dummy api's given only 2 worked so, had to use an outside API for as the 3rd one.

I am assuming that the api's have entries more than 100 but less than 300

## Project Structure

```
VenueKings-Take-home-test-/
├── main.py              # Main pipeline entry point
├── fetcher.py           # Async API fetching logic
├── processor.py         # Data processing and normalization
├── circuit_breaker.py   # Circuit breaker implementation
├── models.py            # Data models (Pydantic)
├── config.py            # Configuration settings
├── tests/               # Test suite
│   ├── conftest.py
│   ├── test_circuit_breaker.py
│   ├── test_processor.py
│   ├── test_fetcher.py
│   └── test_integration.py
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
└── README.md           # This file
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- pip

### Local Setup

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd VenueKings-Take-home-test-
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Running Tests

### Run all tests:

```bash
pytest
```

### Run specific test files:

```bash
pytest tests/test_circuit_breaker.py
pytest tests/test_processor.py
pytest tests/test_fetcher.py
pytest tests/test_integration.py
```

### Run tests with verbose output:

```bash
pytest -v
```

### Run tests with coverage:

```bash
pip install pytest-cov
pytest --cov=. --cov-report=html
```

## Configuration

Edit `config.py` to customize:

- **API endpoints** (`URLS`)
- **Rate limiting** (`RATE_LIMIT_DELAY`, `MAX_CONCURRENT_REQUESTS`)
- **Retry settings** (`MAX_RETRY_ATTEMPTS`, `RETRY_MIN_WAIT`)
- **Circuit breaker** thresholds
- **Batch processing** size (`BATCH_SIZE`)

## Pipeline Flow

1. **Fetch** data from multiple APIs concurrently
2. **Apply circuit breaker** logic for failing endpoints
3. **Process in batches** to manage memory usage
4. **Normalize** product data to common schema
5. **Generate metrics** and performance reports

## Error Handling

- **Network failures**: Automatic retries with exponential backoff
- **API rate limits**: Built-in rate limiting and delays
- **Malformed data**: Graceful handling with detailed logging
- **Circuit breaker**: Prevents overwhelming failing services
- **Partial failures**: Pipeline continues despite individual endpoint failures

## Monitoring & Metrics

The pipeline provides detailed metrics including:

- Success/failure rates
- Processing times
- Data source distribution
- Circuit breaker states

## Troubleshooting

### Common Issues

1. **Import errors when running tests:**

   ```bash
   # Run from project root with PYTHONPATH
   PYTHONPATH=. pytest  # Linux/Mac
   set PYTHONPATH=. && pytest  # Windows CMD
   $env:PYTHONPATH="."; pytest  # Windows PowerShell
   ```

2. **Network timeouts:**

   - Increase `REQUEST_TIMEOUT` in `config.py`
   - Adjust retry settings

3. **Memory issues with large datasets:**
   - Reduce `BATCH_SIZE` in `config.py`
   - Lower `MAX_PRODUCTS_LIMIT`
