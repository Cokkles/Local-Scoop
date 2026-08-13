from dataclasses import dataclass
from datetime import datetime,timezone
from .adapters import NewsRssAdapter,NewsHtmlCardAdapter
from .models import NewsSourceMetrics
from .normalizer import normalize_story
ADAPTERS={"news_rss":NewsRssAdapter,"rss":NewsRssAdapter,"atom":NewsRssAdapter,"news_html":NewsHtmlCardAdapter,"civicengage_news":NewsHtmlCardAdapter}
@dataclass(frozen=True,slots=True)
class NewsBatch:
    stories:tuple; metrics:tuple
class NewsIngestionService:
    def ingest(self,sources,payloads,retrieved_at=None,min_relevance=.5):
        stories=[]; metrics=[]; now=retrieved_at or datetime.now(timezone.utc)
        for source in sources:
            fetched=accepted=rejected=nonlocal_count=0; errors=[]
            try:
                adapter=ADAPTERS[source.adapter_family](); raw=adapter.parse(source,payloads[source.source_id]); fetched=len(raw)
                for item in raw:
                    try:
                        story=normalize_story(item,source,now)
                        if story.relevance_score<min_relevance: nonlocal_count+=1; continue
                        stories.append(story); accepted+=1
                    except Exception as exc: rejected+=1; errors.append(str(exc))
            except Exception as exc: errors.append(str(exc))
            metrics.append(NewsSourceMetrics(source.source_id,fetched,accepted,rejected,nonlocal_count,tuple(errors)))
        return NewsBatch(tuple(stories),tuple(metrics))
