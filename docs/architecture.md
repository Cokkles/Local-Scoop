# Architecture — Phase 0 Baseline

## Logical pipeline

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
  |       |       |
  |       |       +--> classification
  |       +----------> geography enrichment
  +------------------> deduplication/entity resolution
      |
      v
Canonical Records
   |            |
   |            +--> Live Data API / cache
   |
   +--> Daily AI Synthesis --> Daily Scoop cache
                         |
                         v
                  Desktop / Mobile clients
```

## System boundaries

### Source adapters
Know how to retrieve one provider and convert its fields into raw evidence. They do not decide cross-source truth.

### Canonical layer
Owns stable Local Scoop IDs, normalized facts, provenance, geography, freshness metadata, and later entity-resolution decisions.

### AI synthesis
Consumes bounded canonical records. It does not browse independently for facts during normal Daily Scoop generation.

### Client applications
Read normalized/cached application data. They do not contain provider API keys or independently crawl local sources.

## Failure principles
- One failed source must not break the region feed.
- Unknown data remains unknown.
- Conflicts remain representable.
- Stale/expired data is labeled rather than silently presented as fresh.
- Daily AI failure does not prevent weather/events/news from loading.
- Live weather/alert updates do not require Daily Scoop regeneration.

## Deployment direction
A shared regional backend/cache can serve Windows, macOS, Linux, Android, and iOS clients. Client technology remains intentionally decoupled from ingestion technology during the POC.
