"""Fetcher: success, retry on transient failures, fail fast on permanent ones."""

from __future__ import annotations

from collections.abc import Callable

import httpx
import pytest

from city_pulse.platform.ingestion import FetchError, fetch
from city_pulse.platform.ingestion.fetcher import backoff_delay
from city_pulse.platform.sources import Polling

POLLING = Polling(interval_seconds=60, timeout_seconds=5, max_retries=2)
URL = "https://example.com/feed.json"


def client_returning(*responses: httpx.Response | Exception) -> tuple[httpx.Client, list[int]]:
    """A client whose transport replays the given responses; also returns a call counter."""
    calls: list[int] = []
    queue = list(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    return httpx.Client(transport=httpx.MockTransport(handler)), calls


def no_sleep() -> tuple[Callable[[float], None], list[float]]:
    delays: list[float] = []
    return delays.append, delays


def test_returns_body_on_success() -> None:
    client, calls = client_returning(httpx.Response(200, content=b"payload"))

    assert fetch(client, URL, POLLING) == b"payload"
    assert len(calls) == 1


def test_retries_transient_errors_then_succeeds() -> None:
    client, calls = client_returning(
        httpx.Response(503),
        httpx.ConnectError("connection refused"),
        httpx.Response(200, content=b"ok"),
    )
    sleep, delays = no_sleep()

    assert fetch(client, URL, POLLING, sleep=sleep) == b"ok"
    assert len(calls) == 3
    assert len(delays) == 2


def test_does_not_retry_permanent_errors() -> None:
    client, calls = client_returning(httpx.Response(404))
    sleep, delays = no_sleep()

    with pytest.raises(FetchError, match="non-retryable HTTP 404"):
        fetch(client, URL, POLLING, sleep=sleep)
    assert len(calls) == 1
    assert delays == []


def test_gives_up_after_retry_budget() -> None:
    client, calls = client_returning(httpx.Response(500), httpx.Response(502), httpx.Response(503))
    sleep, _ = no_sleep()

    with pytest.raises(FetchError, match="after 3 attempts"):
        fetch(client, URL, POLLING, sleep=sleep)
    assert len(calls) == 3


@pytest.mark.parametrize(("attempt", "upper"), [(1, 1.0), (2, 2.0), (3, 4.0), (10, 30.0)])
def test_backoff_grows_exponentially_and_is_capped(attempt: int, upper: float) -> None:
    for _ in range(50):
        assert upper / 2 <= backoff_delay(attempt) <= upper
