# ADR 0005 — Dynamic source catalog and ingestion boundary

Status: Accepted for Phase 0 POC.

Local Scoop sources are data, not application constants. The effective catalog is assembled from a built-in registry plus server-managed overlays and, later, approved user-added source proposals. Server changes can enable, disable, reconfigure, replace, or add a source without requiring a desktop/mobile client release.

User-added sources are isolated from curated sources. Self-service additions begin with public HTTPS RSS/Atom/iCalendar feeds only, default to authority Tier 4, remain disabled until validation/approval, cannot contain inline credentials, and cannot overwrite curated source IDs. Arbitrary HTML parsers and credentialed APIs remain server-curated because they have higher security, legal, parsing and maintenance risk.

Outbound source retrieval must reject local/private addresses, credentials embedded in URLs, unsafe redirect targets and oversized responses. Credentialed providers reference server-side secret names; secrets are never stored in the catalog.

Phase 0.5 produces source-backed event candidates, not deduplicated canonical events. Cross-source identity resolution remains Phase 0.6.
