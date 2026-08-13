from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

USER_ADAPTERS = {"ical", "rss", "atom"}
SECRET_KEYS = {"api_key", "apikey", "token", "password", "secret", "authorization"}


def validate_public_https_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("source URL must use https")
    if parsed.username or parsed.password:
        raise ValueError("source URL must not include user credentials")
    host = (parsed.hostname or "").rstrip(".").lower()
    if not host or host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
        raise ValueError("source host is not public")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return
    if any((address.is_private, address.is_loopback, address.is_link_local, address.is_multicast, address.is_reserved, address.is_unspecified)):
        raise ValueError("source address is not public")


def ensure_no_inline_secrets(value: object) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in SECRET_KEYS:
                raise ValueError(f"inline credential field is forbidden: {key}")
            ensure_no_inline_secrets(child)
    elif isinstance(value, list):
        for child in value:
            ensure_no_inline_secrets(child)


def validate_user_adapter(adapter_family: str) -> None:
    if adapter_family not in USER_ADAPTERS:
        raise ValueError("user-added sources are limited to standard feed adapters")
