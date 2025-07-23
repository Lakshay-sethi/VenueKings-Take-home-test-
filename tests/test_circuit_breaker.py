import time
from circuit_breaker import SimpleCircuitBreaker

# Unit test for SimpleCircuitBreaker


def test_circuit_breaker_opens_and_closes():
    cb = SimpleCircuitBreaker(fail_threshold=2, reset_timeout=1)
    assert cb.allow_request()  # Initially closed

    cb.record_failure()
    assert cb.allow_request()  # Still closed after 1 failure

    cb.record_failure()
    assert not cb.allow_request()  # Should be open now

    # Wait for reset timeout
    time.sleep(1.1)
    assert cb.allow_request()  # Should allow trial (half-open)

    cb.record_success()
    assert cb.allow_request()  # Should be closed again
