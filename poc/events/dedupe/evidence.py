def source_evidence(item, tiers):
    return {"source_id":item.source_id,"external_id":item.external_id,"url":item.source_url,"retrieved_at":item.retrieved_at.isoformat(),"raw_sha256":item.raw_sha256,"candidate_id":item.event_id,"authority_tier":tiers.get(item.source_id,5)}
