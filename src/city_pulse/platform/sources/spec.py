"""Declarative specification of a data source.

A source is onboarded to the platform by adding one YAML file that validates against
``SourceSpec``. The platform derives everything else (polling, storage keys, metrics,
documentation) from this spec, so adding a source requires no new code.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

SourceName = Annotated[
    str,
    Field(
        pattern=r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$",
        min_length=3,
        max_length=63,
        description="Unique snake_case identifier; used in storage paths and table names.",
    ),
]


class SourceKind(StrEnum):
    """How the platform receives data from the source."""

    REALTIME_FEED = "realtime_feed"  # HTTP endpoint polled on a schedule
    BATCH_FILE = "batch_file"  # files published periodically (e.g. monthly Parquet)


class PayloadFormat(StrEnum):
    """Wire format of the payload returned by the source."""

    GTFS_RT = "gtfs_rt"  # GTFS-realtime protobuf
    JSON = "json"
    PARQUET = "parquet"


class _StrictModel(BaseModel):
    """Base for all spec models: immutable, and unknown keys are errors, not silently ignored."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class License(_StrictModel):
    """Terms under which the platform may use the source."""

    terms_url: HttpUrl
    reviewed_on: date | None = Field(
        default=None,
        description="Date the terms were last read; required before the source is enabled.",
    )
    attribution: str = Field(min_length=1)
    redistribution_allowed: bool = Field(
        description="Whether raw data may be published. False means aggregates only.",
    )


class Polling(_StrictModel):
    """Polling policy for real-time feeds."""

    interval_seconds: int = Field(
        ge=15,
        le=3600,
        description="Never poll faster than the source updates.",
    )
    timeout_seconds: float = Field(default=10.0, gt=0, le=60)
    max_retries: int = Field(default=3, ge=0, le=10)

    @model_validator(mode="after")
    def _timeout_shorter_than_interval(self) -> Self:
        if self.timeout_seconds >= self.interval_seconds:
            raise ValueError("timeout_seconds must be shorter than interval_seconds")
        return self


class SourceSpec(_StrictModel):
    """Everything the platform needs to know to ingest one source."""

    name: SourceName
    description: str = Field(min_length=10)
    owner: str = Field(min_length=1, description="Team or person accountable for the source.")
    kind: SourceKind
    format: PayloadFormat
    endpoint: HttpUrl
    license: License
    contract: str = Field(
        pattern=r"^contracts/.+\.ya?ml$",
        description="Path to the data contract, relative to the repository root.",
    )
    polling: Polling | None = None
    enabled: bool = False
    tags: frozenset[str] = frozenset()

    @model_validator(mode="after")
    def _realtime_feeds_need_polling(self) -> Self:
        if self.kind is SourceKind.REALTIME_FEED and self.polling is None:
            raise ValueError("realtime_feed sources must define a polling policy")
        if self.kind is not SourceKind.REALTIME_FEED and self.polling is not None:
            raise ValueError("polling is only valid for realtime_feed sources")
        return self

    @model_validator(mode="after")
    def _enabled_sources_need_reviewed_terms(self) -> Self:
        if self.enabled and self.license.reviewed_on is None:
            raise ValueError(
                f"source '{self.name}' cannot be enabled before its terms are reviewed "
                "(set license.reviewed_on)"
            )
        return self
