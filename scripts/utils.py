"""
Shared utility helpers for collection scripts.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List

import fandom

WIKI_NAME = "wot"
LANGUAGE = "en"

RETRIES = 3
BACKOFF_SECONDS = [1, 2, 4]

NAMESPACE_PREFIXES = (
    "Category:",
    "Template:",
    "File:",
    "User:",
    "Help:",
    "Special:",
    "Forum:",
    "MediaWiki:",
    "Portal:",
    "Talk:",
)


def read_group_names(path: Path) -> List[str]:
    """
    Read group names from a text file, ignoring comments/empties and de-duplicating.

    If a line is a Category URL, normalize it into a human-friendly group name.
    """
    groups: List[str] = []
    seen = set()

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        group_name = _normalize_group_name(line)
        if not group_name:
            continue

        if group_name not in seen:
            seen.add(group_name)
            groups.append(group_name)

    return groups


def _normalize_group_name(value: str) -> str:
    """
    Normalize group names; supports raw names and Category URLs.
    """
    if "Category:" in value:
        # Extract portion after Category: and decode URL-like separators.
        category_part = value.split("Category:", 1)[1]
        category_part = category_part.split("/", 1)[0]
        return category_part

    return value.strip()


def _decode_title(title: str) -> str:
    """
    Decode basic URL title encodings for fandom category URLs.
    """
    replaced = title.replace("_", " ").replace("%27", "'").replace("%20", " ")
    return replaced.strip()


def safe_page_url(char_dict: Dict[str, Dict[str, str]], title: str) -> str:
    """
    Resolve a page URL from a title using fandom-py.
    """
    try:
        if title in char_dict:
            return char_dict[title]["link"]

        page = fandom.page(title)
        return page.url or ""

    except Exception:  # noqa: BLE001 - fallback to empty string
        return ""


def is_valid_title(title: str) -> bool:
    """
    Filter out non-article namespace titles.
    """
    if not title:
        return False
    for prefix in NAMESPACE_PREFIXES:
        if title.startswith(prefix):
            return False

    skip_terms = ("Chapter", "List of", "Glossary")
    if any(term in title for term in skip_terms):
        return False

    return True


def write_json(path: Path, payload: dict) -> None:
    """
    Write payload to JSON on disk.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=False)
        handle.write("\n")


def init_fandom() -> None:
    """
    Configure fandom-py defaults for this script.
    """
    fandom.set_wiki(WIKI_NAME)
    fandom.set_lang(LANGUAGE)
    fandom.set_rate_limiting(True, min_wait=100)
    fandom.set_user_agent("wheel-of-time-api/collect_character_pages")


def with_retries(func, *args, **kwargs):
    """
    Retry helper with exponential backoff for transient failures.
    """
    for attempt in range(RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 - generic to catch network errors
            if attempt >= RETRIES - 1:
                raise exc
            time.sleep(BACKOFF_SECONDS[attempt])
