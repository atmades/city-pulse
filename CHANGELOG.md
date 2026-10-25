# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Source specification model (Pydantic): declarative onboarding of data sources with policies enforced in code (ADR-008).
- Strict static type checking (mypy) in CI.
- Ingestion poller: retries with exponential backoff and jitter, content-addressed idempotent raw storage, structured JSON logs, graceful shutdown on SIGTERM; `city-pulse` CLI.
- First live source: Citi Bike station status (S6), terms reviewed.
- Ingestion architecture diagrams (docs/architecture/ingestion.md).

## [0.1.0] - 2026-10-02

### Added
- Repository structure, license, README with disclaimer.
- Python tooling: uv, ruff, pytest; repository hygiene tests.
- Pre-commit hooks: formatting, secret scanning (gitleaks), Conventional Commits.
- CI on GitHub Actions: lint, tests, secret scanning; required to merge into main.
- Branch protection for main as a repository ruleset.
- Pull request template with a data source licensing checklist.
- DATA_SOURCES.md, roadmap, ADR template, ADR-001 and ADR-007.
- Terraform dev environment: BigQuery datasets per layer, least-privilege service accounts; fmt and validate in CI.
- direnv project environment (.envrc) isolating credentials and project settings.
