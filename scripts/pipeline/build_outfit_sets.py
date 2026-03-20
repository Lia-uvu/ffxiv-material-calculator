#!/usr/bin/env python3
"""Generate outfitSets.json from enriched recipes and items data.

Can run standalone (downloads CSVs from GitHub) or be called after the main
pipeline has produced enriched recipes/items with secretRecipeBook, ilvl, and
equipSlotCategory fields.
"""
from __future__ import annotations

import csv
import json
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE_URL_CN = "https://raw.githubusercontent.com/thewakingsands/ffxiv-datamining-cn/master"
BASE_URL_EN = "https://raw.githubusercontent.com/InfSein/ffxiv-datamining-mixed/master/en"
BASE_URL_JA = "https://raw.githubusercontent.com/a1hena/ffxiv-datamining-jp/master/csv"

MIN_CRAFTER_LEVEL = 70
MIN_SET_SIZE = 5
MAX_PREFIX_LEN = 8


def fetch_csv(url: str) -> str:
    print(f"  Downloading {url.split('/')[-1]}...")
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")


def locate_header_row(rows: list[list[str]], required_columns: tuple[str, ...]) -> tuple[int, list[str]]:
    """Find the header row by looking for required columns (handles BOM and varying formats)."""
    for idx, row in enumerate(rows[:10]):
        normalized = [cell.lstrip("\ufeff") for cell in row]
        if all(column in normalized for column in required_columns):
            return idx, normalized
    raise ValueError(f"Could not find CSV header containing columns: {required_columns}")


def parse_csv_rows(text: str, required: tuple[str, ...] = ("#",)) -> tuple[list[str], list[list[str]]]:
    rows = list(csv.reader(text.splitlines()))
    header_idx, header = locate_header_row(rows, required)
    data = rows[header_idx + 1:]
    # Skip type/key rows that start with non-numeric values
    while data and data[0] and not data[0][0].lstrip("-").isdigit():
        data = data[1:]
    return header, data


def build_item_name_maps(cn_text: str, en_text: str, ja_text: str) -> dict[int, dict[str, str]]:
    names: dict[int, dict[str, str]] = {}

    for locale, text in [("zh-CN", cn_text), ("en", en_text), ("ja", ja_text)]:
        header, data = parse_csv_rows(text, required=("#", "Name"))
        idx_key = header.index("#")
        idx_name = header.index("Name")
        for row in data:
            if len(row) <= max(idx_key, idx_name):
                continue
            try:
                item_id = int(row[idx_key])
            except ValueError:
                continue
            name = row[idx_name].strip()
            if name:
                names.setdefault(item_id, {})[locale] = name

    return names


def build_enriched_data(cn_text_recipe: str, cn_text_level: str, cn_text_item: str):
    # Parse RecipeLevelTable
    header, data = parse_csv_rows(cn_text_level, required=("#", "ClassJobLevel"))
    idx_key = header.index("#")
    idx_level = header.index("ClassJobLevel")
    level_table = {}
    for row in data:
        try:
            level_table[int(row[idx_key])] = int(row[idx_level])
        except (ValueError, IndexError):
            continue

    # Parse Item.csv for search categories, ilvl, equip slot
    header, data = parse_csv_rows(cn_text_item, required=("#", "ItemSearchCategory", "Level{Item}", "EquipSlotCategory"))
    idx_key = header.index("#")
    idx_search_cat = header.index("ItemSearchCategory")
    idx_ilvl = header.index("Level{Item}")
    idx_equip_slot = header.index("EquipSlotCategory")

    item_search_cat = {}
    item_ilvl = {}
    item_equip_slot = {}
    for row in data:
        try:
            item_id = int(row[idx_key])
        except (ValueError, IndexError):
            continue
        try:
            item_search_cat[item_id] = int(row[idx_search_cat])
        except (ValueError, IndexError):
            pass
        try:
            item_ilvl[item_id] = int(row[idx_ilvl])
        except (ValueError, IndexError):
            pass
        try:
            item_equip_slot[item_id] = int(row[idx_equip_slot])
        except (ValueError, IndexError):
            pass

    # Parse Recipe.csv
    CRAFT_TYPE_TO_JOB = {
        0: "CARPENTER", 1: "BLACKSMITH", 2: "ARMORER", 3: "GOLDSMITH",
        4: "LEATHERWORKER", 5: "WEAVER", 6: "ALCHEMIST", 7: "CULINARIAN",
    }

    header, data = parse_csv_rows(cn_text_recipe, required=("#", "CraftType", "SecretRecipeBook"))
    idx_id = header.index("#")
    idx_craft = header.index("CraftType")
    idx_level_table = header.index("RecipeLevelTable")
    idx_result_item = header.index("Item{Result}")
    idx_secret = header.index("SecretRecipeBook")

    recipes = []
    for row in data:
        try:
            recipe_id = int(row[idx_id])
            result_item_id = int(row[idx_result_item])
        except (ValueError, IndexError):
            continue
        if recipe_id <= 0 or result_item_id <= 0:
            continue
        if item_search_cat.get(result_item_id, 0) == 0:
            continue
        try:
            level_table_id = int(row[idx_level_table])
        except ValueError:
            level_table_id = 0
        crafter_level = level_table.get(level_table_id, 0)
        try:
            secret_book = int(row[idx_secret])
        except (ValueError, IndexError):
            secret_book = 0
        try:
            craft_type = int(row[idx_craft])
        except ValueError:
            craft_type = 0
        job = CRAFT_TYPE_TO_JOB.get(craft_type, "UNKNOWN")

        recipes.append({
            "recipeId": recipe_id,
            "resultItemId": result_item_id,
            "job": job,
            "crafterLevel": crafter_level,
            "secretRecipeBook": secret_book,
            "ilvl": item_ilvl.get(result_item_id, 0),
            "equipSlotCategory": item_equip_slot.get(result_item_id, 0),
        })

    return recipes


def detect_prefix(names: list[str], min_len: int = 2) -> str | None:
    """Find the longest shared prefix among names that groups at least MIN_SET_SIZE items."""
    if len(names) < MIN_SET_SIZE:
        return None

    best = None
    for length in range(min_len, MAX_PREFIX_LEN + 1):
        groups: dict[str, int] = defaultdict(int)
        for name in names:
            if len(name) >= length:
                groups[name[:length]] += 1
        for prefix, count in groups.items():
            if count >= MIN_SET_SIZE:
                if best is None or len(prefix) > len(best):
                    best = prefix
    return best


def build_outfit_sets(
    recipes: list[dict],
    name_maps: dict[int, dict[str, str]],
) -> list[dict]:
    # Filter: master recipes, equipment, ilvl > 1, crafter level >= 70
    candidates = []
    for r in recipes:
        if r["secretRecipeBook"] == 0:
            continue
        if r["equipSlotCategory"] == 0:
            continue
        if r["ilvl"] <= 1:
            continue
        if r["crafterLevel"] < MIN_CRAFTER_LEVEL:
            continue
        cn_name = name_maps.get(r["resultItemId"], {}).get("zh-CN", "")
        if not cn_name:
            continue
        candidates.append({**r, "cn_name": cn_name})

    print(f"  {len(candidates)} candidate items after filtering")

    # Group by ilvl, then detect prefix within each ilvl group
    by_ilvl: dict[int, list[dict]] = defaultdict(list)
    for c in candidates:
        by_ilvl[c["ilvl"]].append(c)

    raw_sets: list[dict] = []
    for ilvl, items in sorted(by_ilvl.items(), reverse=True):
        if len(items) < MIN_SET_SIZE:
            continue

        # Try to find prefix groups within this ilvl
        names = [item["cn_name"] for item in items]

        # Group by prefix: try lengths from MAX_PREFIX_LEN down to 2
        assigned = set()
        prefix_groups: list[tuple[str, list[dict]]] = []

        for plen in range(MAX_PREFIX_LEN, 1, -1):
            groups: dict[str, list[dict]] = defaultdict(list)
            for item in items:
                if id(item) in assigned:
                    continue
                if len(item["cn_name"]) >= plen:
                    groups[item["cn_name"][:plen]].append(item)

            for prefix, group in sorted(groups.items(), key=lambda x: -len(x[1])):
                if len(group) >= MIN_SET_SIZE:
                    # Check if this prefix is just a substring of an already-found prefix
                    already_covered = any(
                        existing_prefix.startswith(prefix) and existing_prefix != prefix
                        for existing_prefix, _ in prefix_groups
                    )
                    if already_covered:
                        continue
                    prefix_groups.append((prefix, group))
                    for item in group:
                        assigned.add(id(item))

        for prefix, group in prefix_groups:
            # Build localized prefix from shared item name prefixes
            item_ids = [item["resultItemId"] for item in group]
            jobs = sorted(set(item["job"] for item in group))
            crafter_level = group[0]["crafterLevel"]

            # Get EN/JA prefix by finding common prefix of translated names
            en_prefix = _find_common_prefix(
                [name_maps.get(iid, {}).get("en", "") for iid in item_ids]
            )
            ja_prefix = _find_common_prefix(
                [name_maps.get(iid, {}).get("ja", "") for iid in item_ids]
            )

            raw_sets.append({
                "prefix": {
                    "zh-CN": prefix,
                    "en": en_prefix or prefix,
                    "ja": ja_prefix or prefix,
                },
                "ilvl": ilvl,
                "crafterLevel": crafter_level,
                "jobs": jobs,
                "itemIds": sorted(item_ids),
            })

    print(f"  {len(raw_sets)} outfit sets detected")
    return raw_sets


def _find_common_prefix(names: list[str]) -> str:
    """Find the longest common prefix among a list of strings, trimmed to last word boundary."""
    names = [n for n in names if n]
    if not names:
        return ""
    prefix = names[0]
    for name in names[1:]:
        while not name.startswith(prefix) and prefix:
            prefix = prefix[:-1]
        if not prefix:
            return ""
    # Trim to word boundary for Latin scripts
    if prefix and prefix[-1] != " " and any(c.isascii() and c.isalpha() for c in prefix):
        last_space = prefix.rfind(" ")
        if last_space > 0:
            prefix = prefix[:last_space + 1]
    return prefix.rstrip()


def main():
    publish_dir = Path(__file__).resolve().parent.parent.parent / "src" / "data"

    print("Downloading CSVs from GitHub...")
    cn_recipe = fetch_csv(f"{BASE_URL_CN}/Recipe.csv")
    cn_level = fetch_csv(f"{BASE_URL_CN}/RecipeLevelTable.csv")
    cn_item = fetch_csv(f"{BASE_URL_CN}/Item.csv")
    en_item = fetch_csv(f"{BASE_URL_EN}/Item.csv")
    ja_item = fetch_csv(f"{BASE_URL_JA}/Item.csv")

    print("Building enriched recipe data...")
    recipes = build_enriched_data(cn_recipe, cn_level, cn_item)
    print(f"  {len(recipes)} recipes parsed")

    print("Building item name maps...")
    name_maps = build_item_name_maps(cn_item, en_item, ja_item)
    print(f"  {len(name_maps)} items with names")

    print("Detecting outfit sets...")
    sets = build_outfit_sets(recipes, name_maps)

    # Sort sets: by crafter level desc, then ilvl desc, then prefix
    sets.sort(key=lambda s: (-s["crafterLevel"], -s["ilvl"], s["prefix"]["zh-CN"]))

    output_path = publish_dir / "outfitSets.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sets, f, ensure_ascii=False, indent=2)
    print(f"Written {len(sets)} outfit sets to {output_path}")


if __name__ == "__main__":
    main()
