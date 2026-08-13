from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .security import validate_public_https_url


class _ValidatedRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urljoin(req.full_url, newurl); validate_public_https_url(target)
        return super().redirect_request(req, fp, code, msg, headers, target)


@dataclass(frozen=True, slots=True)
class FetchResult:
    url: str
    content_type: str
    body: bytes


class SafeHttpTransport:
    def __init__(self, *, user_agent: str = "Local-Scoop-POC/0.0.5", max_bytes: int = 2_000_000, timeout: int = 15):
        self.user_agent = user_agent; self.max_bytes = max_bytes; self.timeout = timeout; self.opener = build_opener(_ValidatedRedirects())

    def get(self, url: str, *, headers: dict[str, str] | None = None) -> FetchResult:
        validate_public_https_url(url)
        merged = {"User-Agent": self.user_agent, "Accept": "application/json, application/xml, text/xml, text/calendar, text/html;q=0.8, */*;q=0.1"}; merged.update(headers or {})
        request = Request(url, headers=merged)
        try: response = self.opener.open(request, timeout=self.timeout)
        except HTTPError: raise
        final_url = response.geturl(); validate_public_https_url(final_url)
        data = response.read(self.max_bytes + 1)
        if len(data) > self.max_bytes: raise ValueError("source response exceeds configured size limit")
        return FetchResult(url=final_url, content_type=response.headers.get_content_type(), body=data)
