"""HTTP fetching with bounded retries and exponential backoff with jitter."""

from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable

import httpx

from city_pulse.platform.observability import log_event
from city_pulse.platform.sources import Polling

logger = logging.getLogger(__name__)

# Statuses worth retrying: rate limiting and transient server errors.
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


class FetchError(Exception):
    """The source could not be fetched within the retry budget."""


def backoff_delay(attempt: int, base: float = 1.0, cap: float = 30.0) -> float:
    """Delay before retry number ``attempt`` (1-based): exponential, capped, with jitter."""
    exponential = min(cap, base * 2.0 ** (attempt - 1))
    # Jitter spreads retries of many clients over time; not used for security.
    return exponential * random.uniform(0.5, 1.0)  # noqa: S311


def fetch(
    client: httpx.Client,
    url: str,
    polling: Polling,
    sleep: Callable[[float], None] = time.sleep,
) -> bytes:
    """Return the response body, retrying transient failures; raise FetchError otherwise."""
    attempts = polling.max_retries + 1
    last_error = "no attempt made"

    for attempt in range(1, attempts + 1):
        try:
            response = client.get(url, timeout=polling.timeout_seconds)
        except httpx.TransportError as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        else:
            if response.status_code == httpx.codes.OK:
                return response.content
            if response.status_code not in RETRYABLE_STATUS:
                raise FetchError(f"non-retryable HTTP {response.status_code} from {url}")
            last_error = f"HTTP {response.status_code}"

        if attempt < attempts:
            delay = backoff_delay(attempt)
            log_event(
                logger,
                logging.WARNING,
                "fetch_retry",
                url=url,
                attempt=attempt,
                error=last_error,
                delay_s=round(delay, 2),
            )
            sleep(delay)

    raise FetchError(f"giving up on {url} after {attempts} attempts: {last_error}")
