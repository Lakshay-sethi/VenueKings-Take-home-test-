import time


class SimpleCircuitBreaker:
    def __init__(self, fail_threshold=3, reset_timeout=60):
        """
        Initialize the circuit breaker.
        Params:
            fail_threshold: Number of consecutive failures before opening the circuit.
            reset_timeout: Time (in seconds) to wait before allowing a trial request after opening.
        """
        self.fail_threshold = fail_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # Possible states: CLOSED, OPEN, HALF_OPEN
        self.opened_since = None

    def allow_request(self):
        """
        Determine if a request should be allowed based on the circuit state.
        return: True if request is allowed, False otherwise.
        """
        if self.state == "OPEN":
            # If enough time has passed, allow a trial request (half-open state)
            if (time.time() - self.opened_since) > self.reset_timeout:
                self.state = "HALF_OPEN"
                return True
            # Otherwise, still open, do not allow
            return False
        # If closed or half-open, allow request
        return True

    def record_success(self):
        """
        Call this when a request succeeds.
        Resets failure count and closes the circuit.
        """
        self.failure_count = 0
        self.state = "CLOSED"
        self.opened_since = None

    def record_failure(self):
        """
        Call this when a request fails.
        Increments failure count and opens the circuit if threshold is reached.
        """
        self.failure_count += 1
        if self.failure_count >= self.fail_threshold:
            self.state = "OPEN"
            self.opened_since = time.time()
