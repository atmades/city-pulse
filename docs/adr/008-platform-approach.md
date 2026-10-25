# ADR-008: Build platform capabilities, onboard sources by configuration

- **Status:** Accepted
- **Date:** 2026-10-25

## Context

The project will ingest at least nine sources and, later, a second city. Writing a dedicated poller, storage logic, retries and metrics for each source duplicates code, makes behavior inconsistent between sources, and makes every new source a code change that needs review of its internals.

## Options considered

1. **One pipeline per source.** Fastest for the first source; each next source repeats retries, idempotency, storage layout and metrics, and they drift apart.
2. **Platform capabilities plus declarative source specifications.** A source is described by a YAML file validated against a typed model; the platform provides polling, retries, idempotent raw storage, publishing and metrics uniformly. More design up front.
3. **Adopt a full ingestion product** (for example Airbyte). Many connectors out of the box, but heavy to run locally, does not support GTFS-realtime polling patterns well, and hides the engineering this project is meant to demonstrate.

## Decision

Option 2. The platform core (`src/city_pulse/platform`) contains reusable capabilities and knows nothing about specific sources. Each source is a file in `sources/` validated against `SourceSpec`. Contracts live in `contracts/`.

The core does not depend on infrastructure: storage, messaging and HTTP access are defined as interfaces and implemented by adapters (local filesystem, Amazon S3, Google Cloud), so the core is tested without network access.

Platform policies are enforced in the model itself, for example: a source cannot be enabled before its license terms are reviewed; a feed cannot be polled more often than every 15 seconds.

## Consequences

- Positive: a new real-time source requires only a YAML spec and a data contract; every source gets the same reliability and observability; policies are checked in CI rather than remembered.
- Negative: more abstraction early; a source with unusual behavior may need an extension point in the platform rather than a quick special case.
- Success criterion: the second city is onboarded without changes to platform code.
