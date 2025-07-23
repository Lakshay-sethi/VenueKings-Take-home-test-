I used claude sonnet 4, gpt 4o models in windsurf.

Used sonnet 4 for planning this tasks in to smaller chunks.
used 4o for regular questions, due to its context window.

In all honesty, I used AI to help me make most of the design decisions for this assignment, and it helped create the basic code for all the files, which was then understood and tested by me.

Prompt: keeping in mind the main objective of the asesment can i use semaphores for rate limiting

AI Response:
Yes, you can use semaphores for rate limiting, but with an important caveat about the assessment's objectives.
Why Semaphores Work for This Assessment:

Demonstrates Concurrency Understanding: Shows you know how to control concurrent access to resources
Simple and Effective: Easy to implement and reason about
Async-Native: Works well with asyncio patterns
Recommended Hybrid Approach:
python# This demonstrates both concepts
semaphore = asyncio.Semaphore(5) # Max 5 concurrent
last_request_time = 0
min_interval = 0.2 # 5 req/sec = 200ms between requests

async with semaphore: # Simple time-based rate limiting
now = time.time()
if now - last_request_time < min_interval:
await asyncio.sleep(min_interval - (now - last_request_time))
last_request_time = time.time()

My Analysis:

Th AI suggestion was quite good and afger understand ing how it works, i used it in the code

Prompt: Show me how tenacity and backoff differ for exponential backoff and gives pros and cons

AI Response:
Tenacity
API: Decorator-based, highly configurable.

Features:

Supports sync/async functions.
Customizable retry conditions, stop conditions, wait strategies (including exponential backoff).
Built-in logging and hooks.
Example:

Pros:

Very flexible and powerful.
Good async support.
Fine-grained control over retry logic.
Cons:

Slightly heavier and more complex for simple use cases.
backoff
API: Decorator-based, simpler and more lightweight.

Features:

Supports sync/async functions.
Built-in exponential, constant, and Fibonacci backoff.
Simple event hooks.
Example:

Pros:

Very easy to use for common retry patterns.
Lightweight, minimal dependencies.
Cons:

Less flexible for complex retry logic.
Fewer customization options than tenacity.
Summary:

Use tenacity for advanced, customizable retry logic.
Use backoff for simple, quick exponential backoff needs.

My Analysis:
After understanding both, went forward with tenacity as it is more customizable and gives me ability to create complex logic.

Prompt: lets write pytests for the code base that will provide max coverage

AI Response:
Plan (pseudocode):

Identify the main code to test: the SimpleCircuitBreaker class.
Write tests for:
Initial state (should be CLOSED).
Allowing requests in CLOSED state.
Transition to OPEN after enough failures.
Not allowing requests in OPEN state before timeout.
Allowing requests in HALF_OPEN after timeout.
Resetting to CLOSED after a success in HALF_OPEN.
Resetting failure count and state after success.
Use pytest and monkeypatch to control time for timeout tests.
import time
from circuit_breaker import SimpleCircuitBreaker

# Unit test for SimpleCircuitBreaker

def test_circuit_breaker_opens_and_closes():
cb = SimpleCircuitBreaker(fail_threshold=2, reset_timeout=1)
assert cb.allow_request() # Initially closed

    cb.record_failure()
    assert cb.allow_request()  # Still closed after 1 failure

    cb.record_failure()
    assert not cb.allow_request()  # Should be open now

    # Wait for reset timeout
    time.sleep(1.1)
    assert cb.allow_request()  # Should allow trial (half-open)

    cb.record_success()
    assert cb.allow_request()  # Should be closed again

My Analysis:
AI allowed me to create a basic structure to test all the functions

Final Implementation:
All the code in pytest, double checked my me.

Prompt: explain ciruit breakers and how to use them, please give code

AI Response:
The circuit breaker pattern is a resilience design pattern used to prevent an application from repeatedly trying to execute an operation that's likely to fail—such as calling an unreliable API endpoint. It works like an electrical circuit breaker:

If failures reach a threshold, the "circuit" opens and further calls fail fast (without trying the operation).
After a timeout, the circuit allows a "trial" call to see if the service has recovered.
If the trial succeeds, the circuit closes and normal operation resumes.
Why use it?

Prevents overwhelming a failing service.
Improves system stability and responsiveness.
Allows for graceful degradation.
How to implement in Python
You can use libraries like pybreaker or implement a simple version yourself.

Example with pybreaker
Install pybreaker

Wrap your API call with a circuit breaker:

How it works:
If fetch_with_breaker fails 5 times in a row, the circuit opens.
For the next 60 seconds, all calls raise CircuitBreakerError immediately.
After 60 seconds, one call is allowed through ("half-open"). If it succeeds, the circuit closes; if not, it stays open.

My Analysis:

This healped me understand the pattern, but wanted to implement my own to fully understand it. Told AI to generate boilerplate circuit breaker code.

Final Implementation:
import time

class SimpleCircuitBreaker:
def **init**(self, fail_threshold=3, reset_timeout=60):
self.fail_threshold = fail_threshold
self.reset_timeout = reset_timeout
self.failure_count = 0
self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN
self.opened_since = None

    def allow_request(self):
        if self.state == "OPEN":
            if (time.time() - self.opened_since) > self.reset_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
        self.opened_since = None

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.fail_threshold:
            self.state = "OPEN"
            self.opened_since = time.time()
