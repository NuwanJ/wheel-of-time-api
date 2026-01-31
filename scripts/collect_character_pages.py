#!/usr/bin/env python3
"""
Collect character page titles for configured character groups using fandom-py.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Dict, List

import fandom

DATA_DIR = Path(__file__).resolve().parent / "data"
GROUPS_PATH = DATA_DIR / "character_groups.txt"
OUTPUT_PATH_GROUPS = DATA_DIR / "character_pages_v3.json"
OUTPUT_PATH_CHARS = DATA_DIR / "character_groups_v3.json"

WIKI_NAME = "wot"
LANGUAGE = "en"

MAX_RESULTS = 500
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
        # return _decode_title(category_part)
        return category_part

    return value.strip()


def _decode_title(title: str) -> str:
    """
    Decode basic URL title encodings for fandom category URLs.
    """
    replaced = title.replace("_", " ").replace("%27", "'").replace("%20", " ")
    return replaced.strip()


def collect_pages_for_group(group_name: str) -> List[Dict[str, str]]:
    """
    Collect page titles and links for a group using fandom search.

    Note: fandom-py does not currently expose category membership directly,
    so this uses search queries as a fallback mechanism.
    """
    # queries = [
    #     f"Category:{group_name}",
    #     group_name,
    #     f"{group_name} character",
    # ]
    queries = ["Biographical Information"]

    pages: List[Dict[str, str]] = []
    seen = set()

    for query in queries:
        print(f"\nQuery: {query} ")
        results = fandom.search(query, results=MAX_RESULTS)
        for title, _page_id in results:
            if not _is_valid_title(title) or title in seen:
                continue
            link = _safe_page_url(title)
            if not link:
                continue
            print(f"> {title} - {link}")
            seen.add(title)
            pages.append({"title": title, "link": link})

    return pages


def _safe_page_url(title: str) -> str:
    """
    Resolve a page URL from a title using fandom-py.
    """
    try:
        page = fandom.page(title)
        return page.url or ""
    except Exception:  # noqa: BLE001 - fallback to empty string
        return ""


def _is_valid_title(title: str) -> bool:
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

    start_time = time.time()
    _init_fandom()

    if not GROUPS_PATH.exists():
        logging.error("Group file not found: %s", GROUPS_PATH)
        return 1

    group_names = read_group_names(GROUPS_PATH)
    if not group_names:
        logging.error("No valid group names found in %s", GROUPS_PATH)
        return 1

    output: dict[str, List[Dict[str, str]]] = {}
    reverse_lookup = {}

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

            for page in pages[0:5]:
                title = page.get("title")
                if not title:
                    continue
                entry = reverse_lookup.setdefault(
                    title,
                    {"title": title, "link": page.get("link", ""), "groups": []},
                )
                if group not in entry["groups"]:
                    entry["groups"].append(group)

        except Exception as exc:  # noqa: BLE001 - log and continue
            logging.error("Group %s failed after retries: %s", group, exc)
            output[group] = []

    write_json(OUTPUT_PATH_GROUPS, output)
    logging.info("Wrote output to %s", OUTPUT_PATH_GROUPS)

    write_json(OUTPUT_PATH_CHARS, reverse_lookup)
    logging.info("Wrote output to %s", OUTPUT_PATH_CHARS)
    elapsed = time.time() - start_time
    logging.info("Total time: %.2f seconds", elapsed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
