COUNTY_TERMS={
"37183":("wake county","raleigh","cary","apex","wake forest","holly springs","garner"),
"37063":("durham county","durham"),"37037":("chatham county","pittsboro"),"37069":("franklin county","louisburg"),
"37077":("granville county","oxford"),"37085":("harnett county","lillington"),"37101":("johnston county","smithfield","clayton","selma"),
"37127":("nash county","rocky mount","nashville")}
def infer_geo(text,source_counties=()):
    value=text.lower(); found=[g for g,terms in COUNTY_TERMS.items() if any(t in value for t in terms)]
    if not found and len(source_counties)==1: found=list(source_counties)
    return tuple(dict.fromkeys(found))
def relevance_score(counties,source_counties=()):
    if counties: return 1.0
    if source_counties: return .65
    return 0.0
