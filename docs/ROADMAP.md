# Roadmap

Capacity: about 15 hours per week, two-week sprints. The project is built in vertical slices: each sprint ends with something that runs end to end and can be demonstrated.

- Sprint 0, Foundation: guardrails, CI, documentation, Terraform for BigQuery datasets and service accounts.
- Sprint 1, Ingestion slice: poller for one subway line group and Citi Bike, raw archive, Pub/Sub emulator, data contracts v1.
- Sprint 2, Streaming slice: Beam pipeline parses, validates, deduplicates and windows the data, with a dead-letter table, loading into BigQuery staging.
- Sprint 3, Delays and all feeds: static GTFS, real delay calculation, all subway line groups, service alerts, late data handling.
- Sprint 4, Batch slice: PySpark backfill of three or more years of TLC trips with one command; partitioning and skew handling.
- Sprint 5, Marts and orchestration: dbt data marts, Airflow DAGs, idempotent backfills.
- Sprint 6, Quality and governance: dbt tests, contract tests in CI, lineage, glossary, catalog.
- Sprint 7, Operations: SLIs and SLOs, platform health mart, runbooks, first chaos day and postmortem.
- Sprints 8–9, AI agent: Google ADK agent over marts and metadata with an evaluation set in CI.
- Later, optional: a validation run on managed services using trial credits, a second city, delay forecasting.

## Sprint 0 checklist

- [x] Repository structure, license, README
- [x] Pre-commit with secret scanning and commit message checks
- [x] CI required to merge; main branch protected
- [x] Data sources, changelog, ADRs, roadmap
- [ ] Google Cloud project with BigQuery sandbox; Terraform creates datasets and service accounts
- [ ] Project board with the first customer request
- [ ] Release v0.1.0
