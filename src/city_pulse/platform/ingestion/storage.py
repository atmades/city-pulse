"""Snapshot storage port and its local filesystem adapter.

The poller depends only on the ``SnapshotStore`` protocol; S3 and GCS adapters
implement the same two methods, so the core never imports a cloud SDK.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Protocol


class SnapshotStore(Protocol):
    """Write-once object storage for raw snapshots."""

    def exists(self, key: str) -> bool:
        """Return True if an object with this key is already stored."""
        ...

    def put(self, key: str, data: bytes) -> None:
        """Store an object under this key."""
        ...


class LocalFileStore:
    """Store snapshots as files under a root directory (local runs, tests, containers)."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def _path(self, key: str) -> Path:
        path = (self._root / key).resolve()
        if not path.is_relative_to(self._root):
            raise ValueError(f"key escapes the storage root: {key!r}")
        return path

    def exists(self, key: str) -> bool:
        return self._path(key).is_file()

    def put(self, key: str, data: bytes) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Write to a temporary file, then rename: readers never see a half-written snapshot.
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            os.replace(tmp, path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise
