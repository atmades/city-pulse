# Ingestion architecture

How a real-time source gets from a URL to the raw layer. Decisions: [ADR-001](../adr/001-poller-plus-pubsub-ingestion.md), [ADR-008](../adr/008-platform-approach.md).

## Poll cycle

One poller runs per source. The top row runs once at startup; the rest repeats every `polling.interval_seconds`.

```mermaid
flowchart TD
    spec["Source spec<br/>sources/*.yaml"] --> validate["Validate<br/>Pydantic model and policies"]
    validate --> poller["Poller<br/>dependencies injected"]
    poller --> fetch["Fetch feed<br/>retries, backoff, jitter"]
    fetch -- "retry budget exhausted" --> failed["Log fetch_failed<br/>poller keeps running"]
    fetch --> key["Compute key<br/>raw/name/dt=day/sha256"]
    key --> exists{"Key already stored?"}
    exists -- yes --> skip["Skip duplicate<br/>idempotent"]
    exists -- no --> write["Atomic write<br/>temp file, then rename"]
    skip --> log["JSON log event"]
    write --> log
    failed --> wait
    log --> wait["Wait for the rest of the interval<br/>SIGTERM interrupts immediately"]
    wait --> fetch
```

- Only transient errors are retried (429, 5xx, network); 403 and 404 fail fast.
- A source outage is logged and does not stop the poller; unexpected exceptions (bugs) are not caught, so the process exits and the orchestrator restarts it.
- The same payload on the same day maps to the same key, so duplicates are never stored twice.

## Code structure: ports and adapters

The platform core depends only on the `SnapshotStore` port. Storage backends implement it, so adding one does not change the core.

```mermaid
flowchart TB
    cli["cli.py<br/>signals, env vars, exit codes"] --> core

    subgraph core["Platform core: src/city_pulse/platform"]
        sources["sources<br/>SourceSpec, load_spec"]
        ingestion["ingestion<br/>Poller, fetch, SnapshotStore port"]
        observability["observability<br/>JSON logs"]
    end

    local["LocalFileStore<br/>implemented"] -. implements .-> ingestion
    s3["S3Store<br/>planned"] -. implements .-> ingestion
    gcs["GCSStore<br/>planned"] -. implements .-> ingestion
```

## Storage layout

```
raw/<source_name>/dt=<YYYY-MM-DD>/<sha256>.<ext>
```

Hive-style `dt=` partitions let Spark, BigQuery and Athena read only the days a query needs.
