from __future__ import annotations
from dataclasses import dataclass
from urllib.request import Request, urlopen

@dataclass(frozen=True, slots=True)
class ProbeResult:
    ok: bool
    status: int | None
    content_type: str | None
    marker_hits: tuple[str, ...]
    error: str | None = None

def http_probe(url: str, markers: tuple[str, ...] = (), timeout: int = 15) -> ProbeResult:
    try:
        req = Request(url, headers={"User-Agent":"Local-Scoop-Phase0/0.4 source-audit"})
        with urlopen(req, timeout=timeout) as response:
            data = response.read(1_000_000).decode("utf-8", errors="ignore")
            hits = tuple(marker for marker in markers if marker.lower() in data.lower())
            return ProbeResult(True, getattr(response, "status", 200), response.headers.get_content_type(), hits)
    except Exception as exc:
        return ProbeResult(False, None, None, (), str(exc))
