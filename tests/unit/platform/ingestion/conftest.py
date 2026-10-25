"""Shared fixtures for ingestion tests: a valid enabled spec and in-memory fakes."""

from __future__ import annotations

from typing import Any

import pytest

from city_pulse.platform.sources import SourceSpec


def spec_dict(**overrides: Any) -> dict[str, Any]:
    spec: dict[str, Any] = {
        "name": "test_feed",
        "description": "Synthetic feed used in unit tests.",
        "owner": "platform-team",
        "kind": "realtime_feed",
        "format": "json",
        "endpoint": "https://example.com/feed.json",
        "license": {
            "terms_url": "https://example.com/terms",
            "reviewed_on": "2026-10-01",
            "attribution": "Example Org",
            "redistribution_allowed": False,
        },
        "contract": "contracts/test_feed.yaml",
        "polling": {"interval_seconds": 60, "timeout_seconds": 5, "max_retries": 2},
        "enabled": True,
    }
    spec.update(overrides)
    return spec


@pytest.fixture
def spec() -> SourceSpec:
    return SourceSpec.model_validate(spec_dict())


class MemoryStore:
    """In-memory SnapshotStore: a fake adapter, so tests need no filesystem or cloud."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def exists(self, key: str) -> bool:
        return key in self.objects

    def put(self, key: str, data: bytes) -> None:
        self.objects[key] = data


@pytest.fixture
def store() -> MemoryStore:
    return MemoryStore()
