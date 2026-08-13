# Phase 0.4 Event Source Discovery

This package owns the source registry, deterministic readiness scoring, adapter-family grouping, county coverage audit, and optional HTTP health probe.

Run:

```bash
python -m poc.sources.demo
```

The registry deliberately distinguishes **source authority** from **ingestion readiness**. A source can be authoritative yet hard to ingest, or highly structured yet incomplete for local discovery.
