from html.parser import HTMLParser
from datetime import datetime
from ..models import RawStory
class NewsHtmlCardAdapter(HTMLParser):
    def parse(self,source,body):
        self.source=source; self.out=[]; self.feed(body); return self.out
    def handle_starttag(self,tag,attrs):
        row=dict(attrs)
        if row.get("data-local-scoop-news")!="1": return
        published=datetime.fromisoformat(row["data-published"]) if row.get("data-published") else None
        self.out.append(RawStory(self.source.source_id,row.get("data-story-id") or row.get("data-headline",""),row.get("data-headline",""),published,row.get("data-summary"),row.get("data-url") or self.source.url,raw_payload=str(row)))
