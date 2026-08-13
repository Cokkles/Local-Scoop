from __future__ import annotations
from typing import Protocol
from poc.sources.catalog import SourceDefinition
from poc.sources.transport import FetchResult
from ..models import RawEvent
class EventAdapter(Protocol):
    def parse(self, source: SourceDefinition, result: FetchResult) -> list[RawEvent]: ...
