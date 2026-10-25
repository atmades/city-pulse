"""Logging and metrics shared by all platform components."""

from city_pulse.platform.observability.logging import configure_logging, log_event

__all__ = ["configure_logging", "log_event"]
