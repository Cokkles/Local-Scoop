# ADR 0006 — Conservative event entity resolution

Status: Accepted for Phase 0 POC.

Local Scoop treats source records as `EventCandidate` evidence until entity resolution creates a canonical event. Automatic merging is intentionally conservative: contradictory dates/times or incompatible geography block automatic merging, and only high multi-field similarity produces `auto_merge`. Lower-confidence `probable_duplicate` and `review` outcomes remain separate records for later adjudication rather than being silently collapsed.

Canonical events retain every contributing candidate/source record, the pairwise match evidence used for automatic merges, and any surviving source conflicts. Source authority controls which value is displayed when merged sources disagree; it never deletes the lower-authority evidence.

Clustering is representative-based rather than transitive union-find. This avoids a chain where A resembles B and B resembles C causing A and C to be auto-merged despite insufficient direct evidence.

Taxonomy is deterministic and versioned (`tax1`) in Phase 0.6. Source-provided canonical category hints and title/description rules produce the primary category, subcategories, and independent attributes. AI classification remains a future fallback for low-confidence/ambiguous cases, not the default taxonomy engine.
