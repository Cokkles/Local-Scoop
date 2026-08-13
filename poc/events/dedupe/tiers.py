def source_tiers_from_registry(payload):
    return {str(row["source_id"]): int(row["authority_tier"]) for row in payload.get("sources", [])}
