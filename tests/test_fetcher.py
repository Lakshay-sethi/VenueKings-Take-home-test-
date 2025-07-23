import pytest
from fetcher import fetch_all_products, circuit_breakers
from circuit_breaker import SimpleCircuitBreaker


@pytest.mark.asyncio
async def test_circuit_breaker_on_network_failure(monkeypatch):
    url = "https://fake-url.com/products"

    # Always raise an exception to simulate network failure
    async def always_fail(*args, **kwargs):
        raise Exception("Network error")

    monkeypatch.setattr("fetcher.fetch_page", always_fail)
    # Create a new circuit breaker for this test
    circuit_breakers[url] = SimpleCircuitBreaker(fail_threshold=2, reset_timeout=1)
    await fetch_all_products(url)
    cb = circuit_breakers[url]
    assert cb.state == "CLOSED"
