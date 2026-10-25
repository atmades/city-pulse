"""LocalFileStore: write-once semantics and protection against path traversal."""

from __future__ import annotations

from pathlib import Path

import pytest

from city_pulse.platform.ingestion import LocalFileStore


def test_put_then_exists(tmp_path: Path) -> None:
    store = LocalFileStore(tmp_path)
    key = "raw/feed/dt=2026-10-22/abc.json"

    assert store.exists(key) is False
    store.put(key, b"data")

    assert store.exists(key) is True
    assert (tmp_path / key).read_bytes() == b"data"


def test_no_temporary_files_left_behind(tmp_path: Path) -> None:
    LocalFileStore(tmp_path).put("raw/a.json", b"x")

    assert [p.name for p in (tmp_path / "raw").iterdir()] == ["a.json"]


@pytest.mark.parametrize("key", ["../outside.json", "raw/../../outside.json"])
def test_keys_cannot_escape_root(tmp_path: Path, key: str) -> None:
    with pytest.raises(ValueError, match="escapes the storage root"):
        LocalFileStore(tmp_path / "root").put(key, b"x")
