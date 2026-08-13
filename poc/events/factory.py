from __future__ import annotations

from poc.sources.catalog import SourceDefinition
from .adapters.feed_lines import RssAtomAdapter
from .adapters.html_cards import StructuredHtmlCardAdapter
from .adapters.ical import ICalendarAdapter
from .adapters.localist import LocalistAdapter
from .adapters.ticketmaster import TicketmasterAdapter

ADAPTERS = {"civicengage": ICalendarAdapter, "ical": ICalendarAdapter, "rss": RssAtomAdapter, "atom": RssAtomAdapter, "simpleview": RssAtomAdapter, "localist": LocalistAdapter, "ticketmaster_api": TicketmasterAdapter, "custom_html": StructuredHtmlCardAdapter, "vision_calendar": StructuredHtmlCardAdapter}

def create_adapter(source: SourceDefinition):
    family = source.config.get("parser_family") or source.adapter_family
    try:
        return ADAPTERS[family]()
    except KeyError as exc:
        raise ValueError(f"unsupported adapter family: {family}") from exc
