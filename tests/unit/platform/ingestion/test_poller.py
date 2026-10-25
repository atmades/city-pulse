"""Poller: content-addressed idempotent storage, disabled sources, graceful stop."""

from __future__ import annotations

import threading
from datetime import UTC, datetime

import httpx
import pytest

from city_pulse.platform.ingestion import Poller, SourceDisabledError
from city_pulse.platform.ingestion.poller import snapshot_key
from city_pulse.platform.sources import SourceSpec

from .conftest import MemoryStore, spec_dict

FIXED_TIME = datetime(2026, 10, 22, 12, 0, tzinfo=UTC)


def constant_client(body: bytes) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, content=body)))


def test_snapshot_key_is_content_addressed(spec: SourceSpec) -> None:
    key_a = snapshot_key(spec, FIXED_TIME, b"same")
    key_b = snapshot_key(spec, FIXED_TIME, b"same")
    key_c = snapshot_key(spec, FIXED_TIME, b"different")

    assert key_a == key_b != key_c
    assert key_a.startswith("raw/test_feed/dt=2026-10-22/")
    assert key_a.endswith(".json")


def test_first_poll_stores_and_identical_poll_is_skipped(
    spec: SourceSpec, store: MemoryStore
) -> None:
    poller = Poller(spec, constant_client(b'{"n": 1}'), store, clock=lambda: FIXED_TIME)

    first = poller.poll_once()
    second = poller.poll_once()

    assert first.stored is True
    assert second.stored is False
    assert first.key == second.key
    assert store.objects == {first.key: b'{"n": 1}'}


def test_disabled_source_is_refused(store: MemoryStore) -> None:
    raw = spec_dict(enabled=False)
    disabled = SourceSpec.model_validate(raw)

    with pytest.raises(SourceDisabledError):
        Poller(disabled, constant_client(b"x"), store)


def test_run_stops_when_stop_event_is_set(spec: SourceSpec) -> None:
    stop = threading.Event()

    class StopAfterFirstPut(MemoryStore):
        def put(self, key: str, data: bytes) -> None:
            super().put(key, data)
            stop.set()

    store = StopAfterFirstPut()
    poller = Poller(spec, constant_client(b"payload"), store)

    poller.run(stop)  # would loop forever if stop were ignored

    assert len(store.objects) == 1
