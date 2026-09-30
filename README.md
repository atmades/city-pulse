# City Pulse NYC

An educational data platform for New York City urban mobility: subway, bike share, taxi and weather data, processed in real time and in batch, with data contracts, quality checks, lineage, SLOs and an AI agent on top.

Status: Sprint 0 (Foundation). See the [roadmap](docs/ROADMAP.md) and [changelog](CHANGELOG.md).

## About

The project is run like real work in a data team: a backlog of requests from a fictional customer, two-week sprints, architecture decision records, SLOs, incidents and postmortems.

It is designed to run at zero cloud cost. Everything works locally, and Google Cloud is used only within its free limits. Pipelines are written so the same code can run on managed services (Dataflow, Dataproc) by changing one setting. See [ADR-007](docs/adr/007-cost-zero-strategy.md).

## How data flows

1. A poller fetches real-time feeds (MTA subway, service alerts, Citi Bike) and saves every snapshot unchanged.
2. Apache Beam parses and validates the snapshots, removes duplicates, computes metrics over time windows and sends bad records to a dead-letter table.
3. PySpark processes large historical datasets (taxi trips, weather, bike trips) and runs backfills.
4. Data is stored in layers in BigQuery: raw, staging, curated and marts.
5. dbt builds the marts: the final data products for dashboards and the AI agent.
6. Airflow orchestrates batch jobs; quality checks, lineage and SLOs cover every layer.

## Tech stack

Python, Apache Beam, PySpark, BigQuery, dbt, Airflow, Pub/Sub, Terraform, GitHub Actions, Docker, Google ADK.

## Quick start

Requirements: Git, Docker, Python 3.11+, uv, Terraform 1.6+, Google Cloud CLI.

- `make setup` installs dependencies and git hooks
- `make check` runs linters and tests, the same as CI
- `make up` starts local emulators for Pub/Sub and Cloud Storage

## Repository layout

- `docs` — architecture decisions, runbooks, postmortems, roadmap
- `infra/terraform` — infrastructure as code
- `ingestion` — feed pollers
- `pipelines` — streaming (Beam) and batch (Spark) jobs
- `orchestration` — Airflow DAGs
- `contracts` — data contracts and schemas
- `quality` — data quality rules
- `sql/marts` — data products (dbt)
- `agent` — AI agent and its evaluation set
- `tests` — tests; fixtures contain synthetic data only

## Engineering rules

- No data and no secrets in the repository; this is checked automatically.
- Changes go through pull requests; the main branch is protected.
- Commit messages follow Conventional Commits; releases use semantic versioning.
- Every architectural change comes with a decision record in `docs/adr`.

## Data and licensing

All data comes from public sources and is used under each owner's terms, listed in [DATA_SOURCES.md](DATA_SOURCES.md). The [MIT license](LICENSE) applies to the source code only, not to the data.

## Disclaimer

This is a non-commercial educational project. It is not affiliated with, endorsed by, or sponsored by the MTA, Lyft / Citi Bike, Citigroup, the NYC Taxi & Limousine Commission, NOAA, or the City of New York. Data is obtained from publicly available sources and is provided "as is", with no guarantee of accuracy, completeness, or timeliness. Use of each dataset is subject to its owner's terms (see DATA_SOURCES.md). The repository license applies to source code only, not to data.
