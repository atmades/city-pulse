## What and why

Closes #

## Checklist

- [ ] CI is green
- [ ] Docs updated where relevant (README, runbook, catalog)
- [ ] ADR added if this is an architectural change
- [ ] No real data, secrets or project IDs committed
- [ ] Cost impact considered (stays within free limits)

### New data source?

- [ ] Terms reviewed and linked in DATA_SOURCES.md
- [ ] Attribution added
- [ ] Polling interval not faster than the source updates; User-Agent and backoff set
- [ ] Data contract added under contracts/
