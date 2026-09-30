"""Repository rules turned into tests: no real data in the repo, required docs present."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_DATA_SUFFIXES = {".parquet", ".pb", ".avro", ".orc", ".duckdb", ".zip", ".gz"}
SKIP_DIRS = {".git", ".venv", ".terraform", "data"}


def _repo_files():
    for path in ROOT.rglob("*"):
        if path.is_file() and not SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
            yield path


@pytest.mark.parametrize(
    "required",
    ["README.md", "LICENSE", ".gitignore", "DATA_SOURCES.md", "CHANGELOG.md", "docs/ROADMAP.md"],
)
def test_required_files_exist(required):
    assert (ROOT / required).is_file(), f"{required} is required by the engineering rules"


def test_readme_contains_disclaimer():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "non-commercial educational project" in readme
    assert "DATA_SOURCES.md" in readme


@pytest.mark.parametrize("pattern", ["data/", "*.parquet", "*.pb", "*.tfstate", ".env", "*.tfvars"])
def test_gitignore_blocks_data_and_secrets(pattern):
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert pattern in lines, f".gitignore must contain '{pattern}'"


def test_no_data_files_in_repo():
    offenders = [
        str(p.relative_to(ROOT))
        for p in _repo_files()
        if p.suffix.lower() in FORBIDDEN_DATA_SUFFIXES
    ]
    assert not offenders, f"Data files must not live in the repo: {offenders}"


def test_every_adr_has_status_and_decision():
    adrs = sorted((ROOT / "docs" / "adr").glob("[0-9][0-9][0-9]-*.md"))
    decisions = [adr for adr in adrs if not adr.name.startswith("000-")]
    assert decisions, "at least one ADR is expected"
    for adr in decisions:
        text = adr.read_text(encoding="utf-8")
        assert "**Status:**" in text, f"{adr.name} has no status"
        assert "## Decision" in text, f"{adr.name} has no Decision section"
