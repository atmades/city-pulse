"""Poll one source on its schedule and archive every new snapshot unchanged."""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

from city_pulse.platform.ingestion.fetcher import FetchError, fetch
from city_pulse.platform.ingestion.storage import SnapshotStore
from city_pulse.platform.observability import log_event
from city_pulse.platform.sources import PayloadFormat, Polling, SourceSpec

logger = logging.getLogger(__name__)

_EXTENSIONS = {
    PayloadFormat.GTFS_RT: "pb",
    PayloadFormat.JSON: "json",
    PayloadFormat.PARQUET: "parquet",
}


class SourceDisabledError(Exception):
    """The source is not enabled in its specification."""


@dataclass(frozen=True, slots=True)
class PollResult:
    """Outcome of one poll."""

    key: str
    stored: bool  # False when an identical snapshot was already archived
    size_bytes: int


def snapshot_key(spec: SourceSpec, fetched_at: datetime, payload: bytes) -> str:
    """Content-addressed key: the same payload on the same day always maps to the same key."""
    digest = hashlib.sha256(payload).hexdigest()
    return f"raw/{spec.name}/dt={fetched_at:%Y-%m-%d}/{digest}.{_EXTENSIONS[spec.format]}"


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Poller:
    """Fetches a source and stores new snapshots. Infrastructure is injected, not created."""

    def __init__(
        self,
        spec: SourceSpec,
        client: httpx.Client,
        store: SnapshotStore,
        clock: Callable[[], datetime] = _utc_now,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not spec.enabled:
            raise SourceDisabledError(f"source '{spec.name}' is disabled in its spec")
        if spec.polling is None:
            raise ValueError(f"source '{spec.name}' has no polling policy")
        self._spec = spec
        self._polling: Polling = spec.polling
        self._client = client
        self._store = store
        self._clock = clock
        self._sleep = sleep

    def poll_once(self) -> PollResult:
        """Fetch the source once; store the snapshot unless it is already archived."""
        payload = fetch(self._client, str(self._spec.endpoint), self._polling, self._sleep)
        key = snapshot_key(self._spec, self._clock(), payload)
        if self._store.exists(key):
            return PollResult(key=key, stored=False, size_bytes=len(payload))
        self._store.put(key, payload)
        return PollResult(key=key, stored=True, size_bytes=len(payload))

    def run(self, stop: threading.Event) -> None:
        """Poll on the spec's interval until ``stop`` is set. Failures are logged, not fatal."""
        interval = self._polling.interval_seconds
        log_event(
            logger, logging.INFO, "poller_started", source=self._spec.name, interval_s=interval
        )

        while not stop.is_set():
            started = time.monotonic()
            try:
                result = self.poll_once()
            except FetchError as exc:
                log_event(
                    logger, logging.ERROR, "fetch_failed", source=self._spec.name, error=str(exc)
                )
            else:
                log_event(
                    logger,
                    logging.INFO,
                    "snapshot_stored" if result.stored else "snapshot_duplicate",
                    source=self._spec.name,
                    key=result.key,
                    size_bytes=result.size_bytes,
                )
            # Wait for the rest of the interval, waking up immediately on shutdown.
            stop.wait(max(0.0, interval - (time.monotonic() - started)))

        log_event(logger, logging.INFO, "poller_stopped", source=self._spec.name)
