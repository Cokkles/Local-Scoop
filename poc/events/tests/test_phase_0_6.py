from datetime import datetime,timedelta,timezone
from poc.events.models import EventCandidate
from poc.events.dedupe import EventMatcher,EventResolver,MatchDisposition
from poc.events.taxonomy import classify

NOW=datetime(2026,8,13,18,tzinfo=timezone.utc)
def item(i,source,title="Downtown Food Truck Rodeo",days=0):
    start=NOW+timedelta(days=days)
    return EventCandidate(i,source,i,title,start,None,"City Plaza","400 Fayetteville St","Raleigh","NC","27601",35.7775,-78.638,"Food trucks. Free to attend.",None,(),"scheduled",NOW,"0"*64)

def test_close_sources_auto_merge():
    a=item("a","official"); b=item("b","tourism","Food Truck Rodeo Downtown Raleigh")
    assert EventMatcher().compare(a,b).disposition==MatchDisposition.AUTO_MERGE

def test_recurrence_date_does_not_merge():
    assert EventMatcher().compare(item("a","official"),item("b","official",days=7)).disposition==MatchDisposition.CONFLICT

def test_probable_pair_stays_separate():
    a=item("a","official"); b=item("b","community","Food Truck Event")
    canonical,pending=EventResolver().resolve([a,b],{"official":1,"community":4})
    assert len(canonical)==2 and len(pending)==1

def test_provenance_survives_merge():
    a=item("a","official"); b=item("b","tourism","Food Truck Rodeo Downtown Raleigh")
    canonical,_=EventResolver().resolve([a,b],{"official":1,"tourism":2})
    assert {row["source_id"] for row in canonical[0]["provenance"]}=={"official","tourism"}

def test_taxonomy_food_and_free():
    result=classify(item("a","official"))
    assert result.category=="food_drink" and "food_trucks" in result.subcategories and "free" in result.attributes
