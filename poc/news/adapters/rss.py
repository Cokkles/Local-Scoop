import email.utils, xml.etree.ElementTree as ET
from ..models import RawStory
class NewsRssAdapter:
    def parse(self,source,body):
        root=ET.fromstring(body); out=[]
        for item in root.findall(".//item"):
            get=lambda name:(item.findtext(name) or "").strip()
            date=get("pubDate"); published=email.utils.parsedate_to_datetime(date) if date else None; link=get("link")
            out.append(RawStory(source.source_id,get("guid") or link or get("title"),get("title"),published,get("description") or None,link or source.url,raw_payload=ET.tostring(item,encoding="unicode")))
        return out
