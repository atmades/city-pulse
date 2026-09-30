# ADR-007: Zero-cost strategy — local-first engines, cloud within free limits

- **Status:** Accepted
- **Date:** 2026-09-30

## Context

This is a personal educational project with a zero budget. The original design uses managed Google Cloud services, several of which have no free tier and are billed from the first minute: Dataflow, Dataproc, Cloud Composer, Dataplex data quality scans.

Google Cloud's Always Free tier includes, per month: 1 TiB of BigQuery queries and 10 GB of BigQuery storage, 10 GiB of Pub/Sub messages, 2 million Cloud Run requests, 5 GB of Cloud Storage and one e2-micro VM (the last two in us-east1, us-central1 or us-west1 only). The BigQuery sandbox allows BigQuery use without any billing account; its tables expire after 60 days.

Budget alerts only notify; they never stop spending.

## Options considered

1. **Managed services running continuously, as in the original design.** Demonstrates every service, but Cloud Composer alone costs hundreds of dollars per month. Rejected.
2. **Everything local, no cloud.** Zero cost, but the portfolio would lack evidence of cloud, infrastructure as code and access management skills.
3. **Local-first engines, Google Cloud only within free limits.** Zero cost; real engines; real BigQuery, Terraform and IAM; managed-service specifics are designed for but not exercised.

## Decision

Option 3.

- Dataflow is replaced by Apache Beam on the DirectRunner; the same code runs on Dataflow with a different runner option.
- Dataproc is replaced by PySpark in Docker; the same job can be submitted to Dataproc Serverless.
- Cloud Composer is replaced by Airflow in Docker; the DAGs are the same.
- Pub/Sub and Cloud Storage use the official emulator and fake-gcs-server locally.
- Dataplex data quality and lineage are replaced by dbt tests and OpenLineage (Marquez).
- BigQuery is real, in the sandbox.
- Terraform state is local until a billing account exists; the remote backend configuration is prepared.

Rules:

1. Load data into BigQuery with batch load jobs, which are free, not streaming inserts, which are billed.
2. Every BigQuery table is partitioned and clustered; queries filter on partition columns.
3. Large history (TLC trips) is processed locally; only aggregates are loaded into BigQuery.
4. If billing is ever enabled: a 1 USD budget with 50/80/100% and forecast alerts, labels on every resource, and an automatic kill switch before any paid service is used.
5. Any validation run on managed services uses free trial credits only, is scripted, and is time-boxed.

## Consequences

- Positive: zero spend; every processing engine is real; the project gains a documented FinOps story.
- Negative: sandbox tables expire after 60 days, which is acceptable because all data can be rebuilt from the sources; real-time runs happen in sessions, not continuously; managed-service features such as autoscaling and job draining are designed for but not exercised.
- Revisit when: credits or a funded account become available, or a feature requires a paid service.
