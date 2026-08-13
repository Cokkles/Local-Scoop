from __future__ import annotations


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").lower().replace("&", " and ").replace("-", " ").replace(".", " ").split())


def content_tokens(value: str | None) -> frozenset[str]:
    stop = {"the", "a", "an", "and", "at", "in", "of", "for", "to"}
    return frozenset(word for word in normalize_text(value).split() if word not in stop and len(word) > 1)


def normalized_venue(value: str | None) -> str:
    return normalize_text(value).replace(" ctr", " center")
