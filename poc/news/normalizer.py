import hashlib
from datetime import datetime,timezone
from .classifier import classify_story
from .geography import infer_geo,relevance_score
from .models import StoryCandidate
def normalize_story(raw,source,retrieved_at=None):
    if not raw.headline.strip() or raw.published_at is None: raise ValueError("headline and published_at required")
    text=" ".join(filter(None,(raw.headline,raw.summary,raw.body_text)))
    counties=raw.county_geoids or infer_geo(text,source.county_geoids); score=relevance_score(counties,source.county_geoids)
    category,tags=classify_story(raw.headline,raw.summary or "",raw.category_hints)
    sid="story1:"+hashlib.sha256(f"{raw.source_id}|{raw.external_id}".encode()).hexdigest()[:24]
    return StoryCandidate(sid,raw.source_id,raw.external_id,raw.headline.strip(),raw.published_at,raw.summary,raw.source_url,counties,raw.localities,category,tags,score,retrieved_at or datetime.now(timezone.utc),raw.raw_sha256)
