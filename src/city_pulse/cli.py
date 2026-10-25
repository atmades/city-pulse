"""Command-line entry point: ``city-pulse validate`` and ``city-pulse poll``."""

from __future__ import annotations

import argparse
import logging
import os
import signal
import sys
import threading
from collections.abc import Sequence
from pathlib import Path
from types import FrameType

import httpx

from city_pulse.platform.ingestion import (
    FetchError,
    LocalFileStore,
    Poller,
    SourceDisabledError,
)
from city_pulse.platform.observability import configure_logging, log_event
from city_pulse.platform.sources import SpecLoadError, load_spec

logger = logging.getLogger("city_pulse.cli")

DEFAULT_USER_AGENT = "city-pulse/0.1 (educational, non-commercial; github.com/atmades/city-pulse)"


def _validate(paths: Sequence[Path]) -> int:
    failures = 0
    for path in paths:
        try:
            spec = load_spec(path)
        except SpecLoadError as exc:
            failures += 1
            print(f"FAIL {exc}", file=sys.stderr)
        else:
            state = "enabled" if spec.enabled else "disabled"
            print(f"OK   {path} ({spec.name}, {state})")
    return 1 if failures else 0


def _poll(spec_path: Path, data_dir: Path, once: bool) -> int:
    try:
        spec = load_spec(spec_path)
    except SpecLoadError as exc:
        log_event(logger, logging.ERROR, "spec_invalid", error=str(exc))
        return 2

    user_agent = os.environ.get("CITY_PULSE_USER_AGENT", DEFAULT_USER_AGENT)
    with httpx.Client(headers={"User-Agent": user_agent}, follow_redirects=True) as client:
        try:
            poller = Poller(spec, client, LocalFileStore(data_dir))
        except SourceDisabledError as exc:
            log_event(logger, logging.ERROR, "source_disabled", error=str(exc))
            return 2

        if once:
            try:
                result = poller.poll_once()
            except FetchError as exc:
                log_event(logger, logging.ERROR, "fetch_failed", error=str(exc))
                return 1
            log_event(logger, logging.INFO, "snapshot_polled", key=result.key, stored=result.stored)
            return 0

        stop = threading.Event()

        def _request_stop(signum: int, _frame: FrameType | None) -> None:
            log_event(
                logger, logging.INFO, "shutdown_requested", signal=signal.Signals(signum).name
            )
            stop.set()

        # Kubernetes sends SIGTERM before killing a pod: finish the current poll and exit cleanly.
        signal.signal(signal.SIGTERM, _request_stop)
        signal.signal(signal.SIGINT, _request_stop)
        poller.run(stop)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="city-pulse", description="City Pulse data platform")
    parser.add_argument("--log-level", default=os.environ.get("CITY_PULSE_LOG_LEVEL", "INFO"))
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="Validate source specification files")
    validate.add_argument("specs", nargs="+", type=Path)

    poll = commands.add_parser("poll", help="Poll one source and archive raw snapshots")
    poll.add_argument("spec", type=Path)
    poll.add_argument(
        "--data-dir", type=Path, default=Path(os.environ.get("CITY_PULSE_DATA_DIR", "data"))
    )
    poll.add_argument("--once", action="store_true", help="Poll a single time and exit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure_logging(args.log_level)
    if args.command == "validate":
        return _validate(args.specs)
    return _poll(args.spec, args.data_dir, args.once)


if __name__ == "__main__":
    sys.exit(main())
