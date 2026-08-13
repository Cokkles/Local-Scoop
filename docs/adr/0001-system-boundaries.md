# ADR 0001 — System boundaries

Status: Accepted for Phase 0 POC.

Clients consume normalized/cached application data instead of crawling providers directly. Source adapters ingest evidence; normalization, geography, classification, and later deduplication produce canonical records; AI synthesis consumes canonical records; clients render live/cached results.

This keeps API keys and provider parsing outside clients, centralizes provenance, allows one regional pull to serve many clients, and deduplicates Daily Scoop generation by region/day.

Backend language, production database, queue, and LLM provider remain intentionally deferred until POC evidence exists.
