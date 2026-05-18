"""Extract equipment metadata needed by build_outfit_sets.py.

Generates a compact JSON file with:
- masterRecipeItemIds: set of item IDs craftable only via master recipe books
- items: per-item ilvl, equipSlotCategory, classJobCategory
- cjcJobs: ClassJobCategory ID → list of battle job abbreviations
"""
from __future__ import annotations

import csv
from typing import Dict, List, Set

BATTLE_JOB_ABBRS = {
    "PLD", "WAR", "DRK", "GNB",
    "WHM", "SCH", "AST", "SGE",
    "MNK", "DRG", "NIN", "SAM", "RPR", "VPR",
    "BRD", "MCH", "DNC",
    "BLM", "SMN", "RDM", "PCT",
}


def _locate_header(rows: list[list[str]], required: tuple[str, ...]) -> tuple[int, list[str]]:
    for idx, row in enumerate(rows[:10]):
        normalized = [cell.lstrip("\ufeff") for cell in row]
        if all(col in normalized for col in required):
            return idx, normalized
    raise ValueError(f"Could not find header with columns: {required}")


def _find_data_start(rows: list[list[str]], header_idx: int) -> int:
    start = header_idx + 1
    while start < len(rows) and not rows[start][0].lstrip("\ufeff-").isdigit():
        start += 1
    return start


def parse_class_job_categories(cjc_text: str) -> Dict[int, List[str]]:
    """Parse ClassJobCategory.csv → { categoryId: [job abbreviations] }."""
    rows = list(csv.reader(cjc_text.splitlines()))
    header_idx, header = _locate_header(rows, ("#", "Name"))
    data_start = _find_data_start(rows, header_idx)

    idx_id = header.index("#")
    job_columns = [(header.index(abbr), abbr) for abbr in BATTLE_JOB_ABBRS if abbr in header]

    result: Dict[int, List[str]] = {}
    for row in rows[data_start:]:
        try:
            cat_id = int(row[idx_id])
        except (ValueError, IndexError):
            continue
        jobs = sorted(
            abbr for col_idx, abbr in job_columns
            if col_idx < len(row) and row[col_idx].strip().lower() == "true"
        )
        if jobs:
            result[cat_id] = jobs
    return result


def parse_item_equip_meta(item_text: str, needed_ids: Set[int]) -> Dict[int, dict]:
    """Extract ilvl, equipSlotCategory, classJobCategory for needed items."""
    rows = list(csv.reader(item_text.splitlines()))
    header_idx, header = _locate_header(rows, ("#", "Level{Item}", "EquipSlotCategory", "ClassJobCategory"))
    data_start = _find_data_start(rows, header_idx)

    idx_id = header.index("#")
    idx_ilvl = header.index("Level{Item}")
    idx_slot = header.index("EquipSlotCategory")
    idx_cjc = header.index("ClassJobCategory")

    result: Dict[int, dict] = {}
    for row in rows[data_start:]:
        try:
            item_id = int(row[idx_id])
        except (ValueError, IndexError):
            continue
        if item_id not in needed_ids:
            continue
        try:
            slot = int(row[idx_slot])
        except (ValueError, IndexError):
            slot = 0
        if slot == 0:
            continue
        try:
            ilvl = int(row[idx_ilvl])
        except (ValueError, IndexError):
            ilvl = 0
        try:
            cjc = int(row[idx_cjc])
        except (ValueError, IndexError):
            cjc = 0
        result[item_id] = {"ilvl": ilvl, "slot": slot, "cjc": cjc}
    return result


def parse_master_recipe_ids(recipes: list[dict]) -> List[int]:
    """Return item IDs that require a master recipe book."""
    seen: Set[int] = set()
    result: List[int] = []
    for r in recipes:
        if r.get("secretRecipeBook", 0) != 0:
            item_id = r["resultItemId"]
            if item_id not in seen:
                seen.add(item_id)
                result.append(item_id)
    return sorted(result)


def build_outfit_meta(
    recipes: list[dict],
    item_csv_text: str,
    cjc_csv_text: str,
) -> dict:
    """Build the outfit set metadata dictionary.

    Args:
        recipes: Full recipe list (with secretRecipeBook field).
        item_csv_text: Raw text of CN Item.csv.
        cjc_csv_text: Raw text of CN ClassJobCategory.csv.
    """
    master_ids = parse_master_recipe_ids(recipes)

    # Collect all result item IDs from recipes
    all_result_ids = {r["resultItemId"] for r in recipes}

    item_meta = parse_item_equip_meta(item_csv_text, all_result_ids)
    cjc_jobs = parse_class_job_categories(cjc_csv_text)

    # Only keep CJC entries that are actually referenced
    referenced_cjcs = {m["cjc"] for m in item_meta.values() if m["cjc"] != 0}
    cjc_jobs_filtered = {
        str(k): v for k, v in cjc_jobs.items() if k in referenced_cjcs
    }

    return {
        "masterRecipeItemIds": master_ids,
        "items": {str(k): v for k, v in sorted(item_meta.items())},
        "cjcJobs": cjc_jobs_filtered,
    }
