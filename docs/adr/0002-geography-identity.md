# ADR 0002 — Geography identity uses stable government GEOIDs plus coverage hashes

**Status:** Accepted for Phase 0.2 POC

## Decision
Use Census county GEOIDs for stable US county identity (`us:county:<GEOID>`). Use a separate deterministic `geo1:<hash>` identifier for a user's effective coverage region.

## Rationale
City names are ambiguous and mutable, while a Scoop region can differ even for users in the same county due to adjacent-county, radius, custom include, or exclusion settings. A canonical coverage hash lets caching and once-per-day AI synthesis key on the actual region definition rather than presentation labels.

## Consequences
- source/event records can retain authoritative county identity;
- region configuration order cannot create duplicate Scoop keys;
- changing coverage intentionally changes the region key;
- schema/hash version must change if canonicalization semantics change;
- non-US identity requires a later namespace strategy.
