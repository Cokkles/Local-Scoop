from dataclasses import dataclass
@dataclass(frozen=True, slots=True)
class TagDefinition:
    tag:str; facet:str; domains:tuple[str,...]; label:str

_ROWS={
"family_friendly":("audience",("event",),"Family Friendly"),"kids":("audience",("event",),"Kids"),
"teens":("audience",("event",),"Teens"),"age_21_plus":("audience",("event",),"21+"),
"free":("cost",("event",),"Free"),"paid":("cost",("event",),"Paid"),
"indoor":("setting",("event",),"Indoor"),"outdoor":("setting",("event",),"Outdoor"),
"accessible":("access",("event",),"Accessible"),"reservation_required":("access",("event",),"Reservation Required"),
"pet_friendly":("access",("event",),"Pet Friendly"),"museum":("venue_type",("event",),"Museum"),
"library":("venue_type",("event","news"),"Library"),"park":("venue_type",("event","news"),"Park"),
"road_closure":("topic",("news",),"Road Closure"),"traffic":("topic",("news",),"Traffic"),
"development":("topic",("news",),"Development"),"housing":("topic",("news",),"Housing"),
"restaurant_opening":("topic",("news",),"Restaurant Opening"),"business_opening":("topic",("news",),"Business Opening"),
"business_closure":("topic",("news",),"Business Closure"),"public_safety":("topic",("news",),"Public Safety"),
"police":("topic",("news",),"Police"),"fire":("topic",("news",),"Fire"),"crime":("topic",("news",),"Crime"),
"schools":("topic",("news",),"Schools"),"elections":("topic",("news",),"Elections"),"utilities":("topic",("news",),"Utilities"),
"water":("topic",("news",),"Water"),"health":("topic",("news",),"Health"),"weather":("topic",("news",),"Weather"),
"transit":("topic",("news",),"Transit"),"budget":("topic",("news",),"Budget"),"construction":("topic",("news",),"Construction"),
"emergency":("impact",("news",),"Emergency"),"service_change":("impact",("news",),"Service Change"),
"opening":("change",("news",),"Opening"),"closure":("change",("news",),"Closure")
}
TAGS={k:TagDefinition(k,v[0],v[1],v[2]) for k,v in _ROWS.items()}
def valid_tag(tag,domain=None): return tag in TAGS and (domain is None or domain in TAGS[tag].domains)
def tags_for_domain(domain): return tuple(t for t,d in TAGS.items() if domain in d.domains)
