def source_quality(candidate, source_tiers):
    tier = source_tiers.get(candidate.source_id, 5)
    fields = (candidate.venue, candidate.address, candidate.city, candidate.latitude, candidate.longitude, candidate.description)
    completeness = sum(value is not None for value in fields)
    return (-tier, completeness, len(candidate.description or ""))


def choose_value(candidates, field, source_tiers):
    rows = [item for item in candidates if getattr(item, field) not in (None, "")]
    if not rows:
        return None
    chosen = max(rows, key=lambda item: source_quality(item, source_tiers))
    return getattr(chosen, field)
