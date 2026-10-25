"""Tests for SourceSpec: valid specs load, invalid specs fail with a clear reason."""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from city_pulse.platform.sources import SourceKind, SourceSpec


def make_spec(**overrides: Any) -> dict[str, Any]:
    """Return a valid spec as a dict; tests override one field to probe one rule."""
    spec: dict[str, Any] = {
        "name": "test_feed",
        "description": "Synthetic feed used in unit tests.",
        "owner": "platform-team",
        "kind": "realtime_feed",
        "format": "json",
        "endpoint": "https://example.com/feed.json",
        "license": {
            "terms_url": "https://example.com/terms",
            "attribution": "Example Org",
            "redistribution_allowed": False,
        },
        "contract": "contracts/test_feed.yaml",
        "polling": {"interval_seconds": 60},
    }
    spec.update(overrides)
    return spec


def test_valid_spec_loads_with_defaults() -> None:
    spec = SourceSpec.model_validate(make_spec())

    assert spec.kind is SourceKind.REALTIME_FEED
    assert spec.enabled is False
    assert spec.polling is not None
    assert spec.polling.timeout_seconds == 10.0


def test_spec_is_immutable() -> None:
    spec = SourceSpec.model_validate(make_spec())

    with pytest.raises(ValidationError):
        spec.name = "renamed"  # type: ignore[misc]


@pytest.mark.parametrize("name", ["Test", "1feed", "my-feed", "a", "double__underscore"])
def test_invalid_names_are_rejected(name: str) -> None:
    with pytest.raises(ValidationError, match="name"):
        SourceSpec.model_validate(make_spec(name=name))


def test_unknown_field_is_an_error_not_ignored() -> None:
    with pytest.raises(ValidationError, match="extra"):
        SourceSpec.model_validate(make_spec(intervl_seconds=30))


def test_polling_faster_than_15_seconds_is_rejected() -> None:
    with pytest.raises(ValidationError, match="interval_seconds"):
        SourceSpec.model_validate(make_spec(polling={"interval_seconds": 5}))


def test_timeout_must_be_shorter_than_interval() -> None:
    with pytest.raises(ValidationError, match="timeout_seconds must be shorter"):
        SourceSpec.model_validate(
            make_spec(polling={"interval_seconds": 20, "timeout_seconds": 30})
        )


def test_realtime_feed_requires_polling() -> None:
    with pytest.raises(ValidationError, match="must define a polling policy"):
        SourceSpec.model_validate(make_spec(polling=None))


def test_batch_source_must_not_define_polling() -> None:
    with pytest.raises(ValidationError, match="only valid for realtime_feed"):
        SourceSpec.model_validate(make_spec(kind="batch_file", format="parquet"))


def test_source_cannot_be_enabled_before_terms_review() -> None:
    with pytest.raises(ValidationError, match="before its terms are reviewed"):
        SourceSpec.model_validate(make_spec(enabled=True))


def test_source_can_be_enabled_after_terms_review() -> None:
    raw = make_spec(enabled=True)
    raw["license"]["reviewed_on"] = "2026-10-04"

    spec = SourceSpec.model_validate(raw)

    assert spec.enabled is True
    assert spec.license.reviewed_on == date(2026, 10, 4)
