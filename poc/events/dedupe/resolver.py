from .canonical import make_canonical
from .grouping import build_groups
from .matcher import EventMatcher

class EventResolver:
    def __init__(self, matcher=None):
        self.matcher = matcher or EventMatcher()
    def resolve(self, candidates, source_tiers):
        groups, pending = build_groups(candidates, self.matcher)
        canonical = []
        for group in groups:
            evidence = [self.matcher.compare(group[0], item) for item in group[1:]]
            canonical.append(make_canonical(group, evidence, source_tiers))
        return tuple(canonical), tuple(pending)
