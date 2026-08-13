import hashlib
from poc.events.taxonomy import classify_many
from .selection import choose_value, source_quality
from .evidence import source_evidence


def make_canonical(candidates, decisions, tiers):
    representative = max(candidates, key=lambda item: source_quality(item, tiers))
    taxonomy = classify_many(candidates)
    key = "|".join(sorted(item.event_id for item in candidates))
    geography = {name: choose_value(candidates, name, tiers) for name in ("venue","address","city","state","postal_code","latitude","longitude")}
    conflicts = []
    if len({item.start.isoformat() for item in candidates}) > 1: conflicts.append("source_start_times_differ")
    if len({item.venue for item in candidates if item.venue}) > 1: conflicts.append("source_venues_differ")
    return {"schema_version":"1.0","event_id":"evt1:"+hashlib.sha256(key.encode()).hexdigest()[:24],"candidate_ids":sorted(item.event_id for item in candidates),"title":choose_value(candidates,"title",tiers) or representative.title,"start_time":representative.start.isoformat(),"end_time":representative.end.isoformat() if representative.end else None,"geography":geography,"description":choose_value(candidates,"description",tiers),"status":choose_value(candidates,"status",tiers) or "scheduled","category":taxonomy.category,"subcategories":list(taxonomy.subcategories),"attributes":list(taxonomy.attributes),"provenance":[source_evidence(item,tiers) for item in candidates],"conflicts":conflicts,"match_evidence":[decision.to_contract() for decision in decisions]}
