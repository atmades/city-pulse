# ADR-001: Ingest real-time feeds with a standalone poller and Pub/Sub

- **Status:** Accepted
- **Date:** 2026-09-30

## Context

Real-time sources (MTA GTFS-realtime, service alerts, Citi Bike GBFS) are pull-based HTTP feeds that refresh every 30–60 seconds. The streaming layer (Apache Beam) needs an unbounded stream of events. Something must turn "a URL that changes every 30 seconds" into "a stream of snapshots".

Requirements: every snapshot is archived unmodified in the raw layer; re-ingesting the same snapshot creates no duplicates; a source outage is a normal situation, not a platform failure; polling is polite (no faster than the feed updates, with backoff). Budget: zero (ADR-007).

## Options considered

1. **Poller container writes raw snapshots and publishes to Pub/Sub; Beam consumes from Pub/Sub.** Clear separation of concerns. The raw archive exists even when streaming is down. The streaming job can be stopped, redeployed or replayed from raw. Pub/Sub decouples speeds and buffers bursts. Cost: one more small component to run and monitor.
2. **Poll HTTP from inside Beam** (custom unbounded source or periodic impulse). One component instead of two, but polling is tied to the pipeline lifecycle: a restart loses snapshots, the raw archive depends on the pipeline, and pipeline workers scale for compute, not for polite fixed-rate requests.
3. **Scheduled micro-batches** (cron writes files, a scheduled job loads them). Simplest and cheapest, but cannot meet the 2-minute freshness target and demonstrates no streaming skills.

## Decision

Option 1. A small stateless poller fetches each feed on a schedule, stores the snapshot in the raw layer under a key derived from its content hash, and publishes a message with source, feed, fetch time, object path and hash to a per-source Pub/Sub topic. Beam consumes from Pub/Sub.

Locally the poller runs in Docker against the Pub/Sub and Cloud Storage emulators; the same container can run on Cloud Run.

## Consequences

- Positive: idempotency comes naturally (same hash, same key, skip the write); the raw archive enables replays and backfills of the streaming layer; poller failures and pipeline failures are isolated; source availability becomes a simple metric: successful fetches divided by expected fetches.
- Negative: two components to operate; message order is not guaranteed, which Beam handles with event-time processing.
- Revisit if: a source offers push or websocket delivery, or polling volume outgrows a single small container.
