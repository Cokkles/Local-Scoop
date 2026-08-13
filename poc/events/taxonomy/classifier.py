from dataclasses import dataclass
from .rules import ATTRIBUTE_RULES, CATEGORY_RULES, SUBCATEGORY_RULES

VALID = set(CATEGORY_RULES) | {"nightlife","community","other"}

@dataclass(frozen=True, slots=True)
class TaxonomyResult:
    category: str
    subcategories: tuple[str,...]
    attributes: tuple[str,...]
    confidence: float
    evidence: tuple[str,...]
    taxonomy_version: str = "tax1"

def _hits(text, phrases):
    return [phrase for phrase in phrases if phrase in text]

def classify_many(candidates):
    rows=tuple(candidates)
    if not rows: raise ValueError("at least one candidate is required")
    titles=" | ".join(dict.fromkeys(item.title for item in rows)).lower()
    descriptions=" | ".join(dict.fromkeys(item.description or "" for item in rows if item.description)).lower()
    hints=tuple(dict.fromkeys(h.lower().strip() for item in rows for h in item.category_hints))
    scores={}; evidence=[]
    for hint in hints:
        if hint in VALID: scores[hint]=scores.get(hint,0)+4; evidence.append("source_hint:"+hint)
    for category,phrases in CATEGORY_RULES.items():
        title_hits=_hits(titles,phrases); desc_hits=_hits(descriptions,phrases)
        if title_hits or desc_hits:
            scores[category]=scores.get(category,0)+len(title_hits)*3+len(desc_hits)
            evidence += ["keyword:"+hit for hit in (title_hits+desc_hits)[:3]]
    category=max(scores,key=lambda key:(scores[key],key)) if scores else "community"
    confidence=min(.98,.55+.08*scores.get(category,0)) if scores else .45
    combined=titles+" "+descriptions
    subs=tuple(name for name,phrases in SUBCATEGORY_RULES.items() if _hits(combined,phrases))
    attrs=tuple(name for name,phrases in ATTRIBUTE_RULES.items() if _hits(combined,phrases))
    return TaxonomyResult(category,subs,attrs,round(confidence,2),tuple(dict.fromkeys(evidence)))

def classify(candidate):
    return classify_many((candidate,))
