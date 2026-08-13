from __future__ import annotations
from dataclasses import dataclass,field
from datetime import datetime
import hashlib
@dataclass(frozen=True, slots=True)
class RawStory:
    source_id:str; external_id:str; headline:str; published_at:datetime|None; summary:str|None=None; source_url:str|None=None
    body_text:str|None=None; county_geoids:tuple[str,...]=(); localities:tuple[str,...]=(); category_hints:tuple[str,...]=(); raw_payload:str=""
    @property
    def raw_sha256(self): return hashlib.sha256(self.raw_payload.encode()).hexdigest()
@dataclass(frozen=True, slots=True)
class StoryCandidate:
    story_id:str; source_id:str; external_id:str; headline:str; published_at:datetime; summary:str|None; source_url:str|None
    county_geoids:tuple[str,...]; localities:tuple[str,...]; category:str; tags:tuple[str,...]; relevance_score:float
    retrieved_at:datetime; raw_sha256:str
    def to_contract(self):
        return {"story_id":self.story_id,"headline":self.headline,"published_at":self.published_at.isoformat(),"summary":self.summary,"category":self.category,"tags":list(self.tags),"county_geoids":list(self.county_geoids),"relevance_score":self.relevance_score,"provenance":[{"source_id":self.source_id,"external_id":self.external_id,"url":self.source_url,"retrieved_at":self.retrieved_at.isoformat(),"raw_sha256":self.raw_sha256}]}
@dataclass(frozen=True, slots=True)
class StoryCluster:
    cluster_id:str; story_ids:tuple[str,...]; headline:str; category:str; tags:tuple[str,...]; county_geoids:tuple[str,...]; published_at:datetime; updated_at:datetime
    def to_contract(self):
        return {"cluster_id":self.cluster_id,"story_ids":list(self.story_ids),"headline":self.headline,"category":self.category,"tags":list(self.tags),"county_geoids":list(self.county_geoids),"published_at":self.published_at.isoformat(),"updated_at":self.updated_at.isoformat()}
@dataclass(frozen=True, slots=True)
class NewsSourceMetrics:
    source_id:str; fetched_items:int=0; accepted_items:int=0; rejected_items:int=0; nonlocal_items:int=0; errors:tuple[str,...]=field(default_factory=tuple)
