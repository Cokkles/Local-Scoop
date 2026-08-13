from __future__ import annotations

import json
from typing import Any
from urllib.request import Request, urlopen


def json_get(url: str, headers: dict[str, str]) -> dict[str, Any]:
    request = Request(url, headers=headers)
    with urlopen(request, timeout=15) as response:
        return json.load(response)
