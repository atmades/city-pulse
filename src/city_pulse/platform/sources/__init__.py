"""Source specifications: the declarative contract between a data source and the platform."""

from city_pulse.platform.sources.loader import SpecLoadError, load_spec
from city_pulse.platform.sources.spec import (
    License,
    PayloadFormat,
    Polling,
    SourceKind,
    SourceSpec,
)

__all__ = [
    "License",
    "PayloadFormat",
    "Polling",
    "SourceKind",
    "SourceSpec",
    "SpecLoadError",
    "load_spec",
]
