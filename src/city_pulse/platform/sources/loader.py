"""Load source specifications from YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from city_pulse.platform.sources.spec import SourceSpec


class SpecLoadError(Exception):
    """A source specification file is missing, malformed or invalid."""


def load_spec(path: Path) -> SourceSpec:
    """Parse and validate one source specification file."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SpecLoadError(f"{path}: cannot read YAML: {exc}") from exc

    if not isinstance(raw, dict):
        raise SpecLoadError(f"{path}: expected a mapping at the top level")

    try:
        return SourceSpec.model_validate(raw)
    except ValidationError as exc:
        raise SpecLoadError(f"{path}: invalid source spec:\n{exc}") from exc
