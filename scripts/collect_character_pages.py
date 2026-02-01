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
from utils import (
    init_fandom,
    is_valid_title,
    read_group_names,
    safe_page_url,
    with_retries,
    write_json,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
GROUPS_PATH = DATA_DIR / "character_groups.txt"
OUTPUT_PATH_GROUPS = DATA_DIR / "character_pages.json"
OUTPUT_PATH_CHARS = DATA_DIR / "character_groups.json"

MAX_RESULTS = 250


def collect_pages_for_group(char_dict: dict, group_name: str) -> List[Dict[str, str]]:
    """
    Collect page titles and links for a group using fandom search.

    Note: fandom-py does not currently expose category membership directly,
    so this uses search queries as a fallback mechanism.
    """
    queries = [f"{group_name} Biographical Information"]
    pages: List[Dict[str, str]] = []
    seen = set()

    for query in queries:
        print(f"\nQuery: {query} ")
        results = fandom.search(query, results=MAX_RESULTS)
        i = 0
        c = len(results)
        for title, _page_id in results:
            if not is_valid_title(title) or title in seen:
                continue
            link = safe_page_url(char_dict, title)
            if not link:
                continue

            i += 1
            print(f"> {i:3}/{c}\t {title} - {link}")
            seen.add(title)
            pages.append({"title": title, "link": link})

    return pages


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    start_time = time.time()
    init_fandom()

    if not GROUPS_PATH.exists():
        logging.error("Group file not found: %s", GROUPS_PATH)
        return 1

    group_names = read_group_names(GROUPS_PATH)
    if not group_names:
        logging.error("No valid group names found in %s", GROUPS_PATH)
        return 1

    output: dict[str, List[Dict[str, str]]] = {}

    # Read existing character groups if available
    if OUTPUT_PATH_CHARS.exists():
        print("Loading existing character groups from", OUTPUT_PATH_CHARS)
        try:
            with OUTPUT_PATH_CHARS.open("r", encoding="utf-8") as f:
                reverse_lookup = json.load(f)
        except Exception as exc:
            logging.error("Failed to read existing character groups file: %s", exc)
            reverse_lookup = {}
        finally:
            print("Loaded", len(reverse_lookup), "entries from existing file")

    for group in group_names:
        logging.info("Collecting pages for group: %s", group)
        try:
            pages = with_retries(collect_pages_for_group, reverse_lookup, group)
            output[group] = pages
            logging.info(
                "Group %s succeeded with %d pages",
                group,
                len(pages),
            )

            for page in pages:
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

        finally:
            # Write intermediate results after each group
            write_json(OUTPUT_PATH_GROUPS, output)
            logging.info("Wrote output to %s", OUTPUT_PATH_GROUPS)

            write_json(OUTPUT_PATH_CHARS, reverse_lookup)
            logging.info("Wrote output to %s", OUTPUT_PATH_CHARS)

    elapsed = time.time() - start_time
    logging.info("Total time: %.2f seconds", elapsed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
