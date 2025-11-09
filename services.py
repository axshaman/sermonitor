"""Service layer helpers used by the REST API."""
from __future__ import annotations

from typing import Iterable, List

import json

from requests.exceptions import HTTPError

from models.models import KeyWords, Users, db
from xmlproxy import get_urls


def normalise_keyword(name: str) -> str:
    return name.strip().lower()


def get_or_create_keyword(name: str) -> KeyWords:
    keyword = KeyWords.get_word_by_name(name)
    if keyword:
        return keyword
    keyword = KeyWords(name=name)
    db.session.add(keyword)
    db.session.commit()
    return keyword


def add_keywords_to_user(user: Users, keywords: Iterable[str]) -> List[KeyWords]:
    added: List[KeyWords] = []
    for raw_name in keywords:
        name = normalise_keyword(raw_name)
        if not name:
            continue
        keyword = get_or_create_keyword(name)
        if keyword not in user.keywords:
            user.keywords.append(keyword)
            added.append(keyword)
    db.session.commit()
    return added


def delete_user_keywords(user: Users, keywords: Iterable[str]) -> List[str]:
    removed: List[str] = []
    for raw_name in keywords:
        name = normalise_keyword(raw_name)
        keyword = KeyWords.get_word_by_name(name)
        if keyword and keyword in user.keywords:
            user.keywords.remove(keyword)
            removed.append(keyword.name)
    db.session.commit()
    return removed


def get_keywords_for_user(user: Users) -> List[str]:
    return sorted(keyword.name for keyword in user.keywords)


def perform_search(query: str, keywords: Iterable[str]) -> List[dict]:
    """Perform the XMLProxy search and return structured results."""

    joined_keywords = ",".join(sorted({normalise_keyword(name) for name in keywords}))
    response_text = get_urls(query=f"{query} {joined_keywords}")

    results: List[dict] = []
    try:
        data = json.loads(response_text)
        groups = data["yandexsearch"]["response"]["results"]["grouping"].get("group", [])
    except (KeyError, ValueError, TypeError) as exc:  # pragma: no cover - defensive
        raise HTTPError(f"Unexpected response from search provider: {exc}") from exc

    for index, group in enumerate(groups, start=1):
        doc = group.get("doc", {})
        url = doc.get("url")
        snippet = ""
        headline = doc.get("headline")
        passages = doc.get("passages")
        if passages and "passage" in passages:
            passage = passages["passage"]
            if isinstance(passage, list):
                snippet = " ".join(p.get("#text", "") for p in passage)
            else:
                snippet = passage.get("#text", "")
        elif headline:
            if isinstance(headline, dict):
                snippet = headline.get("#text", "")
            else:
                snippet = str(headline)

        results.append(
            {
                "id": index,
                "url": url,
                "snippet": snippet.strip(),
                "headline": _extract_headline(headline, joined_keywords),
            }
        )
    return results


def _extract_headline(headline: object, fallback: str) -> str:
    if isinstance(headline, dict):
        text = headline.get("hlword") or headline.get("#text")
        if isinstance(text, list):
            return " ".join(str(item) for item in text)
        if text:
            return str(text)
    if isinstance(headline, list):
        return " ".join(str(item) for item in headline)
    if isinstance(headline, str):
        return headline
    return fallback


__all__ = [
    "add_keywords_to_user",
    "delete_user_keywords",
    "get_keywords_for_user",
    "perform_search",
]
