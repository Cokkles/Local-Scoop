# Product Requirements — Phase 0 Baseline

## Product question
Can Local Scoop reliably answer “what is happening around me?” by combining detailed weather, local events, local news, civic notices, geography, provenance, and a cost-bounded daily AI synthesis?

## Required user outcomes
- See current, hourly, and multi-day weather.
- See severe weather/public-safety alerts without waiting for the Daily Scoop.
- Discover events for today, tonight, tomorrow, and the weekend.
- Filter by event category, attributes, distance, city, county, and surrounding counties.
- See local news and civic notices relevant to the configured region.
- See where every surfaced fact came from and when it was retrieved.
- Understand when cached data is stale or expired.
- Receive one grounded Daily Scoop per region/day/version without repeated user-triggered LLM generation.
- See live changes that happened after the Daily Scoop without rewriting the cached narrative.

## POC success criteria
- Weather retrieval and hourly normalization work reliably.
- Geography resolves a home location into stable city/county/region context.
- At least five useful event sources and three useful local-news sources can be normalized.
- Canonical event/story schemas tolerate heterogeneous sources without silently discarding evidence.
- Duplicate detection becomes measurable in later checkpoints.
- Daily Scoop output can be traced to canonical source-backed records.
- Repeated refreshes do not produce repeated AI calls.
- Source failures remain isolated and visible.

## Non-goals for Phase 0.1
- Production-grade UI.
- Final backend/database selection.
- Full national source coverage.
- Autonomous internet-wide AI browsing for every app open.
- Real-time continuous LLM analysis.
- User-specific recommendation learning.
- Mobile store packaging.

## Trust principle
Traditional ingestion and deterministic processing establish facts. AI operates on that evidence and may summarize or classify; it is never the underlying source of truth.
