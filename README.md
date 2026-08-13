# Local Scoop

Local Scoop is a cross-platform “What’s happening around me?” application concept that combines detailed weather, local events, local news, civic information, and a grounded AI-generated Daily Scoop.

The project is currently in **Phase 0 — Feasibility / POC**. Phase 0 is intentionally proving the difficult data, trust, geography, caching, and synthesis problems before committing to the final production stack or polished UI.

## Product Goal

Local Scoop should help answer:

- What is the weather doing now?
- What will the weather look like hour-by-hour?
- Are there active weather or public-safety alerts?
- What is happening today, tonight, tomorrow, and this weekend?
- What events are nearby?
- What is happening in my county and surrounding counties?
- What local news and civic notices matter?
- Where did each piece of information come from?
- When was it last checked?
- What changed after today’s Daily Scoop was generated?

## Core Design Principle

Traditional ingestion and deterministic processing establish facts.

AI may summarize, classify, rank, or synthesize those facts, but **AI is not treated as a source of truth**.

Canonical records retain provenance so surfaced information remains traceable to its underlying source.

## Current Phase

### Phase 0.1 — Requirements & Canonical Schemas

Implemented:

- product requirements and non-goals;
- logical system architecture;
- source, AI, and caching policies;
- event/news taxonomy;
- canonical schema contracts;
- provenance requirements;
- Daily Scoop grounding requirements;
- freshness concepts;
- POC package/test scaffold.

Canonical entities currently include:

- Geography Context
- Source
- Event
- Story
- Weather
- Daily Scoop

### Phase 0.2 — Geography POC

Implemented and validated:

- WGS84 coordinate validation;
- U.S. Census coordinate-to-geography resolution;
- stable county identity using Census GEOIDs;
- county adjacency parsing;
- county, adjacent-county, radius, and custom coverage modes;
- explicit county exclusions;
- deterministic Local Scoop region IDs;
- Haversine distance calculations;
- offline deterministic fixtures;
- real Census HTTPS transport;
- Raleigh / Wake County as the initial POC market.

Representative POC location:

- Raleigh, North Carolina
- Coordinates: `35.7796, -78.6382`
- Home county: Wake County
- Census GEOID: `37183`
- Stable county ID: `us:county:37183`
- Timezone: `America/New_York`

Wake County’s Census-defined adjacent counties used by the POC are:

- Chatham
- Durham
- Franklin
- Granville
- Harnett
- Johnston
- Nash

The deterministic adjacent-county Local Scoop region ID for the current fixture is:

`geo1:4b213a0b9c466697fbd3`

## Phase 0 Validation

Current deterministic suite:

`18 / 18 tests passing`

The tests cover both canonical Phase 0.1 contracts and Phase 0.2 geography behavior.

## Architecture

```text
External Sources
        |
        v
Source Adapters
        |
        v
Raw Evidence
        |
        v
Validation / Normalization
   |         |         |
   |         |         +--> Classification
   |         +------------> Geography Enrichment
   +----------------------> Deduplication / Entity Resolution
        |
        v
Canonical Records
     |             |
     |             +--> Live Data / Cache
     |
     +--> Daily AI Synthesis
                    |
                    v
               Daily Scoop
                    |
                    v
          Desktop / Mobile Clients
