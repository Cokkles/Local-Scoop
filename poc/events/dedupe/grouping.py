from .matcher import EventMatcher
from .match_models import MatchDisposition

def build_groups(candidates, matcher=None):
    matcher=matcher or EventMatcher(); groups=[]; pending=[]
    for candidate in sorted(candidates,key=lambda x:(x.start,x.event_id)):
        target=None
        for i,group in enumerate(groups):
            decision=matcher.compare(group[0],candidate)
            if decision.disposition==MatchDisposition.AUTO_MERGE:
                target=i; break
            if decision.disposition in (MatchDisposition.PROBABLE_DUPLICATE,MatchDisposition.REVIEW): pending.append(decision)
        if target is None: groups.append([candidate])
        else: groups[target].append(candidate)
    return groups,pending
