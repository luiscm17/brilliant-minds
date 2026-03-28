from typing import Any
from uuid import uuid4

_SHARED_RESULTS: dict[str, dict[str, Any]] = {}


def create_share(payload: dict[str, Any], base_url: str) -> dict[str, str]:
    token = uuid4().hex
    _SHARED_RESULTS[token] = payload
    return {
        "shareToken": token,
        "shareUrl": f"{base_url.rstrip('/')}/shared/{token}",
    }


def get_share(token: str) -> dict[str, Any] | None:
    return _SHARED_RESULTS.get(token)
