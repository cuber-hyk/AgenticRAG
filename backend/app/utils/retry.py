from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=3, reset_timeout=30)


def with_retry_circuit(fn):
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(0.2))
    def wrapped(*args, **kwargs):
        return breaker.call(fn, *args, **kwargs)

    return wrapped
