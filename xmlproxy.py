"""Wrapper around the XMLProxy search API."""
from __future__ import annotations

import json
import os
from typing import Optional

import requests
import xmltodict

USER_API: str = os.getenv("XMLPROXY_URL", "http://xmlproxy.ru/search/")


def get_urls(query: str, user_api: Optional[str] = None, timeout: int = 30) -> str:
    """Return the XMLProxy response serialised to JSON."""

    base_url = user_api or USER_API
    response = requests.get(f"{base_url}&query={query}", timeout=timeout)
    response.raise_for_status()
    parsed = xmltodict.parse(response.text)
    return json.dumps(parsed, ensure_ascii=False)


__all__ = ["get_urls"]
