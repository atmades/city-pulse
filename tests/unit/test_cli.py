"""CLI: spec validation exit codes, as used by CI."""

from __future__ import annotations

from pathlib import Path

import pytest

from city_pulse.cli import main

ROOT = Path(__file__).resolve().parents[2]


def test_all_repository_specs_are_valid() -> None:
    specs = sorted((ROOT / "sources").glob("*.yaml"))
    assert specs, "at least one source spec is expected"
    assert main(["validate", *map(str, specs)]) == 0


def test_invalid_spec_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("name: Bad-Name\n", encoding="utf-8")

    assert main(["validate", str(bad)]) == 1
    assert "FAIL" in capsys.readouterr().err
