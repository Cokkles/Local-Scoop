NEWS_CATEGORIES={
"public_safety":("shooting","police","fire","crime","arrest","emergency"),
"government_civic":("city council","county commissioners","budget","ordinance","public hearing","election","voter"),
"traffic_transportation":("road","traffic","lane closure","street closure","transit","bus"),
"weather_environment":("weather","drought","storm","heat","flood","water shortage"),
"schools_education":("school","schools","teacher","student","university"),
"business_development":("development","rezoning","construction","business","opens","opening","closes","closing"),
"food_drink_business":("restaurant","brewery","bar","coffee","dining"),
"health":("health","measles","hospital","clinic","opioid"),
"community":("community","library","park","neighborhood"),
"arts_entertainment":("museum","arts","theater","music","festival"),
"sports":("sports","game","team","hockey","soccer"),
"utilities_infrastructure":("utility","water main","sewer","power","infrastructure")}
TAG_PHRASES={"road_closure":("road closure","street closure","lane closure","closed until"),"traffic":("traffic","lane","road"),"development":("development","rezoning","development ordinance"),"housing":("housing","homes","apartments"),"restaurant_opening":("restaurant opens","restaurant opening","new restaurant"),"business_opening":("grand opening","opens first","new business"),"business_closure":("business closing","restaurant closing","closes permanently"),"public_safety":("public safety","police","fire","shooting"),"police":("police","sheriff"),"fire":("fire department","firefighters","fire "),"crime":("crime","shooting","homicide","robbery","arrest"),"schools":("school","schools"),"elections":("election","voter","voting"),"utilities":("utility","utilities","power"),"water":("water","drought"),"health":("health","measles","opioid"),"weather":("weather","storm","heat","flood","drought"),"transit":("transit","bus","rail"),"budget":("budget","tax rate"),"construction":("construction","project update"),"emergency":("emergency","warning","advisory"),"service_change":("service change","offices closed","schedule change"),"opening":("opens","opening","grand opening"),"closure":("closed","closure","closing")}
def classify_story(headline,summary="",hints=()):
    title=headline.lower(); text=(headline+" "+(summary or "")).lower(); scores={}
    for hint in hints:
        if hint in NEWS_CATEGORIES: scores[hint]=scores.get(hint,0)+4
    for cat,phrases in NEWS_CATEGORIES.items(): scores[cat]=scores.get(cat,0)+sum(3 for p in phrases if p in title)+sum(1 for p in phrases if p in text)
    category=max(scores,key=lambda k:(scores[k],k)) if max(scores.values(),default=0)>0 else "community"
    tags=tuple(k for k,phrases in TAG_PHRASES.items() if any(p in text for p in phrases))
    return category,tags
