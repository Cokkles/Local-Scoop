def _tokens(text):
    value=(text or "").lower()
    for char in ",.;:!?-/": value=value.replace(char," ")
    words=[]
    for word in value.split():
        if word in {"the","a","an","in","on","at","after","of"}: continue
        for suffix in ("ing","ed","es","s"):
            if word.endswith(suffix) and len(word)>len(suffix)+3: word=word[:-len(suffix)]; break
        if word=="fallen": word="fall"
        words.append(word)
    return frozenset(words)
def story_similarity(left,right):
    a,b=_tokens(left.headline),_tokens(right.headline); title=len(a&b)/max(1,len(a|b))
    tags=len(set(left.tags)&set(right.tags))/max(1,len(set(left.tags)|set(right.tags)))
    geo=1.0 if set(left.county_geoids)&set(right.county_geoids) else 0.0
    hours=abs((left.published_at-right.published_at).total_seconds())/3600; time=max(0.0,1-hours/96)
    return round(.70*title+.10*tags+.15*geo+.05*time,3)
