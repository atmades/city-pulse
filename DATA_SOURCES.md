# Data Sources

Every source is added only after its terms are reviewed (see the pull request checklist). Terms change: re-check the links below when adding a source, before any public release, and at least once per quarter.

The author is not a lawyer. This file records how the project interprets and follows each source's terms.

## Sources

- S1. MTA Subway GTFS-realtime (all line groups). Protobuf, no API key. Access: https://api.mta.info/. Status: planned, Sprint 1. Terms reviewed: not yet.
- S2. MTA LIRR and Metro-North GTFS-realtime. Protobuf, no API key. Access: https://api.mta.info/. Status: planned. Terms reviewed: not yet.
- S3. MTA Service Alerts. Protobuf, no API key. Access: https://api.mta.info/. Status: planned. Terms reviewed: not yet.
- S4. MTA Elevator and Escalator status. JSON, no API key. Access: https://api.mta.info/. Status: planned. Terms reviewed: not yet.
- S5. MTA Static GTFS. ZIP/CSV. Access: https://www.mta.info/developers. Status: planned. Terms reviewed: not yet.
- S6. Citi Bike GBFS (Lyft). JSON, no API key. Access: official GBFS feed. Status: planned, Sprint 1. Terms reviewed: not yet.
- S7. NYC TLC Trip Records. Parquet. Access: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page. Status: planned, Sprint 4. Terms reviewed: not yet.
- S8. NOAA weather (GSOD). BigQuery public dataset bigquery-public-data.noaa_gsod. Status: planned. Terms reviewed: not yet.
- S9. Citi Bike trip history (Lyft). Official downloads: https://citibikenyc.com/system-data. Status: planned. Terms reviewed: not yet.

When a source is connected, its "Terms reviewed" field gets the review date and a link to the exact terms page that was read.

## How the project follows the terms

MTA (S1–S5):
- Data is stored and served only from the project's own storage, never proxied directly from MTA servers.
- No claims about the accuracy, completeness or timeliness of MTA data.
- Source data is not altered in the raw layer; using a subset is allowed.
- No MTA logos, maps, line symbols or trademarks anywhere: repository, dashboards, screenshots.

Citi Bike / Lyft (S6, S9):
- Access only through official interfaces (GBFS feed, official downloads); no website scraping.
- Raw data is not redistributed as a standalone dataset; only aggregates are published.
- No attempts to link trips to individuals, including by joining with other sources.
- No claims of affiliation and no Citi Bike or Citi trademarks.

NYC TLC (S7): TLC does not guarantee data accuracy; this is stated here and in dashboards.

NOAA (S8): US federal government data, generally in the public domain; attributed as good practice.

BigQuery public datasets: the original owner's terms apply.

## Technical politeness

- Poll no more often than the feed updates (about 30 seconds for GTFS-realtime, 60 seconds for GBFS).
- Send a descriptive User-Agent with contact information; back off exponentially on errors.
- Never circumvent access limits.

## If a source changes or revokes its terms

Disable its ingestion, delete its data from all layers, and record the change in CHANGELOG.md.

## Attribution

Data: Metropolitan Transportation Authority; Lyft Bikes and Scooters, LLC (Citi Bike); NYC Taxi & Limousine Commission; NOAA National Centers for Environmental Information.
