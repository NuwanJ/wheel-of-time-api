You are an expert Python software engineer specializing in data transformation, validation, and deterministic JSON generation.

---

## 🎯 Goal

Implement a Python script that **reads an existing JSON file** containing character pages grouped by group name, and produces a **reverse lookup JSON** mapping each character name to:

- Its canonical page name
- A list of groups it belongs to

---

## 📥 Input File

Path:

```

scripts/data/character_pages.json

````

Structure:

```json
{
  "group_name_1": ["character_page_1", "character_page_2"],
  "group_name_2": ["character_page_2", "character_page_3"]
}
````

Notes:

- Keys = group names
- Values = arrays of character page identifiers (strings)

---

## 📤 Output File

Path:

```
scripts/data/character_page_lookup.json
```

Required structure:

```json
{
  "Character Name 1": {
    "page": "Character Name 1",
    "groups": ["group_name_1", "group_name_3"]
  },
  "Character Name 2": {
    "page": "Character Name 2",
    "groups": ["group_name_2"]
  }
}
```

---

## 🔁 Transformation Rules

1. Iterate over all groups.
2. For each character name inside a group:

   - If character does not yet exist in lookup:

     - Create entry with:

       - `"page"` = character name
       - `"groups"` = empty list
   - Append the current group to `"groups"` if not already present.
3. De-duplicate group names per character.
4. Preserve deterministic ordering:

   - Sort characters alphabetically (A–Z).
   - Sort group arrays alphabetically.

---

## 📁 Required Script

Create:

```
scripts/build_character_page_lookup.py
```

Script must be executable via:

```bash
python scripts/build_character_page_lookup.py
```

No CLI arguments.

---

## 📚 Allowed Libraries

Standard library only:

- json
- os / pathlib
- typing
- logging

---

## 🛡 Validation & Error Handling

Handle gracefully:

- Missing input file
- Invalid JSON
- Unexpected data types
- Empty files

Behavior:

- If input file is missing → log error and exit with non-zero code.
- If malformed JSON → log error and exit with non-zero code.
- Script must never silently fail.

---

## 🧩 Required Functions

Implement at minimum:

```python
read_character_pages(path: Path) -> dict[str, list[str]]
build_lookup(pages: dict[str, list[str]]) -> dict[str, dict]
write_json(path: Path, payload: dict) -> None
main() -> int
```

---

## 🧪 Code Quality Requirements

- PEP8 compliant
- Type hints everywhere
- Docstrings for all functions
- Clear variable naming
- No global mutable state

---

## ✅ Acceptance Criteria

- Reads `scripts/data/character_pages.json`
- Produces `scripts/data/character_page_lookup.json`
- Correctly aggregates groups per character
- Deterministic, stable output
- Robust error handling

---

## 🚫 Prohibited

- External dependencies
- Pandas
- CLI frameworks

---

Deliver only the Python implementation in:

```
scripts/build_character_page_lookup.py
```

following all rules above.
