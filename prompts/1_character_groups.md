You are an expert Python engineer building reliable data-collection scripts.

## Goal

Implement a Python script that uses the **`fandom`** Python library to collect character page titles (or canonical page identifiers) for multiple character groups listed in a local text file, and save results as structured JSON.

Reference documentation (do not hardcode content from it; use it to correctly use the API):

- <https://fandom-py.readthedocs.io/en/latest/getting_started.html>

---

## Deliverable

Create a Python script:

```

scripts/collect_character_pages.py

````

The script must be runnable via:

```bash
python scripts/collect_character_pages.py
````

No CLI arguments required.

---

## Input

Read group names from:

```
scripts/data/character_groups.txt
```

### File format rules

- One group name per line.
- Ignore empty lines.
- Lines starting with `#` are comments and must be ignored.
- Trim surrounding whitespace from each group name.
- De-duplicate group names while preserving original order.

Example:

```
# WoT character groups
Aes Sedai
Asha'man
Forsaken
```

---

## Output

Write JSON to:

```
scripts/data/character_pages.json
```

### Required JSON structure

```json
{
  "group_name_1": ["character_page_1", "character_page_2"],
  "group_name_2": ["character_page_1", "character_page_2"]
}
```

Requirements:

- Values must be **lists of strings** (character page titles or page names).
- De-duplicate character pages per group.
- Preserve deterministic ordering (stable order preferred; if API returns unordered results, sort alphabetically).

---

## Implementation Requirements

### Library constraints

- Use the `fandom` library as the primary mechanism to retrieve pages.
- Standard library modules allowed: `json`, `os`, `pathlib`, `typing`, `time`, `logging`.

### Wiki target

This script is for the *Wheel of Time* fandom wiki. Configure `fandom` accordingly (using the library’s documented approach). Do not assume global defaults are correct.

### Collection logic

For each group name from the input file:

1. Query fandom for relevant results tied to that group name (e.g., via search, category lookup, or other supported methods per docs).
2. Extract **character page identifiers** as strings (prefer page titles).
3. Store under the group key in the output JSON.

**Note:** If the library cannot directly list category members, implement a robust fallback via search that still uses `fandom` (e.g., search for `"Category:<group>"` or `"group <character>"` patterns), and document the limitation in code comments.

---

## Reliability & Edge Cases

### Error handling

The script must not crash due to one failing group. Handle:

- Network failures/timeouts
- Empty / invalid group names
- No results for a group
- Rate limiting or transient failures

### Retry policy

- Implement up to **3 retries** per group with exponential backoff (e.g., 1s, 2s, 4s) for transient errors.

### Logging

- Log progress to stdout using `logging`.
- For each group, log:

  - group name
  - number of pages collected
  - whether it succeeded or failed
- If a group fails after retries, store an empty list for it and log the error.

---

## Code Quality

- PEP8 compliant
- Type hints
- Docstrings
- Small, testable functions, at minimum:

  - `read_group_names(path) -> list[str]`
  - `collect_pages_for_group(group_name: str) -> list[str]`
  - `write_json(path, payload) -> None`
  - `main() -> int`

---

## Acceptance Criteria

- `scripts/collect_character_pages.py` exists and runs.
- Reads `scripts/data/character_groups.txt`.
- Produces `scripts/data/character_pages.json` in the required structure.
- Uses the `fandom` library for data retrieval.
- Handles failures gracefully without terminating the whole run.
