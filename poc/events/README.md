# Event ingestion POC

Phase 0.5 parses heterogeneous source evidence into source-backed event candidates. It intentionally does not merge duplicates.

Run the deterministic Phase 0.5 suite with:

```bash
python -m pytest poc/events/tests poc/sources/tests
```
