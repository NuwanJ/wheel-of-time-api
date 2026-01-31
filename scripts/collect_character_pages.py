#!/usr/bin/env python3
"""
Collect character page titles for configured character groups using fandom-py.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import List

import fandom

DATA_DIR = Path(__file__).resolve().parent / "data"
GROUPS_PATH = DATA_DIR / "character_groups.txt"
OUTPUT_PATH = DATA_DIR / "character_pages.json"

WIKI_NAME = "wot"
LANGUAGE = "en"

MAX_RESULTS = 50
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
        return _decode_title(category_part)

    return value.strip()


def _decode_title(title: str) -> str:
    """
    Decode basic URL title encodings for fandom category URLs.
    """
    replaced = title.replace("_", " ").replace("%27", "'").replace("%20", " ")
    return replaced.strip()


def collect_pages_for_group(group_name: str) -> List[str]:
    """
    Collect page titles for a group using fandom search.

    Note: fandom-py does not currently expose category membership directly,
    so this uses search queries as a fallback mechanism.
    """
    queries = [
        f"Category:{group_name}",
        group_name,
        f"{group_name} character",
    ]

    titles: List[str] = []
    seen = set()

    for query in queries:
        results = fandom.search(query, results=MAX_RESULTS)
        for title, _page_id in results:
            if _is_valid_title(title) and title not in seen:
                seen.add(title)
                titles.append(title)

    return titles


def _is_valid_title(title: str) -> bool:
    """
    Filter out non-article namespace titles.
    """
    if not title:
        return False
    for prefix in NAMESPACE_PREFIXES:
        if title.startswith(prefix):
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


def _init_fandom() -> None:
    """
    Configure fandom-py defaults for this script.
    """
    fandom.set_wiki(WIKI_NAME)
    fandom.set_lang(LANGUAGE)
    fandom.set_rate_limiting(True, min_wait=100)
    fandom.set_user_agent("wheel-of-time-api/collect_character_pages")


def _with_retries(func, *args, **kwargs):
    for attempt in range(RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 - generic to catch network errors
            if attempt >= RETRIES - 1:
                raise exc
            time.sleep(BACKOFF_SECONDS[attempt])


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    _init_fandom()

    if not GROUPS_PATH.exists():
        logging.error("Group file not found: %s", GROUPS_PATH)
        return 1

    group_names = read_group_names(GROUPS_PATH)
    if not group_names:
        logging.error("No valid group names found in %s", GROUPS_PATH)
        return 1

    output: dict[str, List[str]] = {}

    for group in group_names:
        logging.info("Collecting pages for group: %s", group)
        try:
            pages = _with_retries(collect_pages_for_group, group)
            output[group] = pages
            logging.info(
                "Group %s succeeded with %d pages",
                group,
                len(pages),
            )
        except Exception as exc:  # noqa: BLE001 - log and continue
            logging.error("Group %s failed after retries: %s", group, exc)
            output[group] = []

    write_json(OUTPUT_PATH, output)
    logging.info("Wrote output to %s", OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
