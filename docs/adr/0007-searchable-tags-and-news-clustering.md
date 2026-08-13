# ADR 0007 — Searchable tags and news clustering

Status: Accepted for Phase 0 POC.

Categories answer **what kind of record is this?** Tags answer **what properties/topics apply to it?** Local Scoop keeps these dimensions separate. Events may be `arts_culture` with tags such as `museum`, `family_friendly`, `indoor`, `free`, and `accessible`; news may be `traffic_transportation` with tags such as `road_closure`, `construction`, and `service_change`.

Tags use a controlled registry with facets/domains and are designed as searchable filter keys. Relative concepts such as `today` or `this_weekend` remain query-time filters rather than persisted tags.

Local-news ingestion preserves each publisher's story as evidence. Multiple publishers covering the same development are clustered conservatively into a `newscluster1:` topic cluster rather than destructively deduplicated into one article. First-party releases and professional reporting remain independently accessible within the cluster.
