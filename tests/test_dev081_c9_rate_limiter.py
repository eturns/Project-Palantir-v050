"""DEV-081-C9 — Public BETA rate-limiting tests.

Author: Edward Turns (Project Lead)
"""

from web.backend.rate_limit import SlidingWindowRateLimiter


def test_allows_ten_requests_per_minute():
    limiter = SlidingWindowRateLimiter(limit=10, window_seconds=60)

    for _ in range(10):
        assert limiter.allow("192.0.2.10", now=100.0)


def test_eleventh_request_is_rejected():
    limiter = SlidingWindowRateLimiter(limit=10, window_seconds=60)

    for _ in range(10):
        assert limiter.allow("192.0.2.10", now=100.0)

    assert not limiter.allow("192.0.2.10", now=100.0)


def test_different_visitors_have_separate_limits():
    limiter = SlidingWindowRateLimiter(limit=10, window_seconds=60)

    for _ in range(10):
        assert limiter.allow("192.0.2.10", now=100.0)

    assert limiter.allow("192.0.2.20", now=100.0)


def test_limit_resets_after_sixty_seconds():
    limiter = SlidingWindowRateLimiter(limit=10, window_seconds=60)

    for _ in range(10):
        assert limiter.allow("192.0.2.10", now=100.0)

    assert limiter.allow("192.0.2.10", now=160.0)


def test_rejected_requests_do_not_consume_extra_slots():
    limiter = SlidingWindowRateLimiter(limit=1, window_seconds=60)

    assert limiter.allow("192.0.2.10", now=100.0)
    assert not limiter.allow("192.0.2.10", now=101.0)
    assert limiter.allow("192.0.2.10", now=160.0)

def test_expired_visitors_are_removed_from_memory():
    limiter = SlidingWindowRateLimiter(limit=10, window_seconds=60)

    for index in range(100):
        assert limiter.allow(f"visitor-{index}", now=100.0)

    assert len(limiter._requests) == 100

    # A later request should trigger cleanup of expired visitors.
    assert limiter.allow("new-visitor", now=200.0)

    assert len(limiter._requests) == 1