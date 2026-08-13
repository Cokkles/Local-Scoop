# Weather POC

Phase 0.3 normalizes NWS observations/hourly forecasts/alerts and optionally enriches them with Open-Meteo detail. The module is deterministic under fixture transports, keeps source provenance, separates alert and forecast refresh windows, and can serve bounded stale last-known-good data when the authoritative forecast temporarily fails.

Run the deterministic tests with:

```bash
python -m pytest poc/weather/tests
```
