from dataclasses import dataclass
from collections import defaultdict
@dataclass(frozen=True, slots=True)
class SearchDocument:
    document_id:str; domain:str; category:str; subcategories:tuple[str,...]=(); tags:tuple[str,...]=(); text:str=""
class TagIndex:
    def __init__(self,documents=()):
        self.docs={}; self.by_tag=defaultdict(set); self.by_category=defaultdict(set)
        for d in documents: self.add(d)
    def add(self,d):
        self.docs[d.document_id]=d; self.by_category[(d.domain,d.category)].add(d.document_id)
        for tag in d.tags: self.by_tag[(d.domain,tag)].add(d.document_id)
    def search(self,*,domain,category=None,tags=(),match_all=True):
        ids={i for i,d in self.docs.items() if d.domain==domain}
        if category is not None: ids &= self.by_category.get((domain,category),set())
        sets=[self.by_tag.get((domain,t),set()) for t in tags]
        if sets:
            selected=set.intersection(*map(set,sets)) if match_all else set.union(*map(set,sets))
            ids &= selected
        return tuple(self.docs[i] for i in sorted(ids))
