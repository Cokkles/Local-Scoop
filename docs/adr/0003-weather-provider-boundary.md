# ADR 0003 — Weather provider boundary

Status: Accepted for Phase 0 POC.

For the U.S. POC, National Weather Service data is the authoritative weather/public-alert source. The weather service discovers point-specific NWS endpoints through `/points`, uses the nearest returned observation station for current measured conditions, uses the NWS hourly forecast for authoritative hourly temperature/precipitation-probability/wind/text fields, and uses active NWS alerts for watches/warnings/advisories.

Open-Meteo is an optional supplemental detail source. It may enrich current/hourly records with model-derived feels-like temperature, humidity/dew point, precipitation amount, cloud cover, visibility, wind gusts, and UV. Supplemental values must not silently override available NWS observation/forecast values for fields where NWS is designated primary.

Provider failure is isolated. Open-Meteo failure must not suppress usable NWS weather. Alert failure must not suppress the forecast. A temporary NWS forecast failure may serve a clearly stale last-known-good cache within a bounded stale-if-error window; expired cache data must not masquerade as current.
