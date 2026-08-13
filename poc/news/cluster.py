import hashlib
from .models import StoryCluster
from .similarity import story_similarity

def _make_cluster(group):
    ids=tuple(sorted(item.story_id for item in group))
    cluster_id="newscluster1:"+hashlib.sha256("|".join(ids).encode()).hexdigest()[:24]
    tags=tuple(sorted(set(tag for item in group for tag in item.tags)))
    counties=tuple(sorted(set(code for item in group for code in item.county_geoids)))
    best=max(group,key=lambda item:(item.relevance_score,-len(item.headline)))
    return StoryCluster(cluster_id,ids,best.headline,best.category,tags,counties,min(item.published_at for item in group),max(item.published_at for item in group))

def cluster_stories(stories,threshold=.84):
    groups=[]
    for story in sorted(stories,key=lambda item:(item.published_at,item.story_id)):
        matched=None
        for group in groups:
            if abs((story.published_at-group[0].published_at).days)<=7 and story_similarity(group[0],story)>=threshold:
                matched=group; break
        if matched is None: groups.append([story])
        else: matched.append(story)
    return tuple(_make_cluster(group) for group in groups)
