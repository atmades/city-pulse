"""Ingestion capability: poll sources and archive raw snapshots."""

from city_pulse.platform.ingestion.fetcher import FetchError, fetch
from city_pulse.platform.ingestion.poller import Poller, PollResult, SourceDisabledError
from city_pulse.platform.ingestion.storage import LocalFileStore, SnapshotStore

__all__ = [
    "FetchError",
    "LocalFileStore",
    "PollResult",
    "Poller",
    "SnapshotStore",
    "SourceDisabledError",
    "fetch",
]
