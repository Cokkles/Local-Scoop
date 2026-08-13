# Geography POC

Run from repository root:

```bash
python -m pytest poc/geography/tests poc/contracts
```

The unit suite is deterministic and does not require network access. `CensusGeocoder` has a real HTTPS transport for integration testing, but tests inject a representative Raleigh/Wake Census response fixture.

The 2025 Wake County adjacency fixture is extracted from the U.S. Census Bureau national County Adjacency File and retains GEOIDs plus shared-boundary lengths.
