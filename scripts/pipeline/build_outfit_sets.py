#!/usr/bin/env python3
"""Generate outfitSets.json from enriched recipes and items data.

Can run standalone (downloads CSVs from GitHub) or be called after the main
pipeline has produced enriched recipes/items with secretRecipeBook, ilvl, and
equipSlotCategory fields.
"""
from __future__ import annotations

import csv
import json
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE_URL_CN = "https://raw.githubusercontent.com/thewakingsands/ffxiv-datamining-cn/master"
BASE_URL_EN = "https://raw.githubusercontent.com/InfSein/ffxiv-datamining-mixed/master/en"
BASE_URL_JA = "https://raw.githubusercontent.com/a1hena/ffxiv-datamining-jp/master/csv"

MIN_CRAFTER_LEVEL = 70

# Known role suffixes in Chinese item names.
# Combat: 制敌(Tank)/咏咒(Caster)/强袭(Striker)/御敌(Defender)/治愈(Healer)/游击(Scouter)/精准(Ranger)/强攻(Maiming)
# DoH/DoL: 巧匠(Crafter)/大地(Gatherer)
ROLE_SUFFIXES = ["制敌", "咏咒", "强袭", "御敌", "治愈", "游击", "精准", "强攻", "巧匠", "大地"]

# Equipment slot categories that count as "armor" (left-side gear + accessories).
# Weapons (1=main hand, 2=off-hand/shield, 13=two-hand) are excluded.
ARMOR_SLOTS = {3, 4, 5, 7, 8}        # head, body, hands, legs, feet
ACCESSORY_SLOTS = {9, 10, 11, 12}     # earring, necklace, bracelet, ring
GEAR_SLOTS = ARMOR_SLOTS | ACCESSORY_SLOTS

# Minimum number of distinct armor slots (from ARMOR_SLOTS) a set must cover
# to be considered a real equipment set (not just a weapon collection).
MIN_ARMOR_SLOT_COVERAGE = 3


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


def _strip_role_suffix(cn_name: str) -> tuple[str, str]:
    """Strip a known role suffix from a Chinese item name.

    Returns (base_name_without_suffix, role_suffix).
    If no known suffix matches, returns (cn_name, "").
    """
    for suffix in ROLE_SUFFIXES:
        if cn_name.startswith(suffix):
            # Edge case: the suffix IS the prefix (e.g., item just called "制敌xxx").
            # Only strip if there's at least 2 chars before the suffix.
            continue
        # Check if removing this suffix from some position leaves a reasonable base.
        # Role suffixes appear after the set name prefix in FFXIV Chinese naming.
        # e.g., "旧日王国制敌头盔" → base="旧日王国", role="制敌", rest="头盔"
        idx = cn_name.find(suffix)
        if idx >= 2:
            return cn_name[:idx], suffix
    return cn_name, ""


def _find_common_prefix(names: list[str]) -> str:
    """Find the longest common prefix among a list of strings, trimmed to word boundary."""
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
        base_name, role = _strip_role_suffix(cn_name)
        candidates.append({**r, "cn_name": cn_name, "base_name": base_name, "role": role})

    print(f"  {len(candidates)} candidate items after filtering")

    # Group by (base_name, ilvl) — this merges all role variants into one set.
    groups: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for c in candidates:
        # Use the first 2+ chars of base_name as a grouping key.
        # Items within the same ilvl sharing the same base_name belong together.
        groups[(c["base_name"], c["ilvl"])].append(c)

    # Now find the longest common prefix within each group to get the true set name.
    raw_sets: list[dict] = []
    for (base_name, ilvl), items in groups.items():
        # Check armor slot coverage: must have items in >= MIN_ARMOR_SLOT_COVERAGE armor slots
        armor_slots_covered = {item["equipSlotCategory"] for item in items} & ARMOR_SLOTS
        if len(armor_slots_covered) < MIN_ARMOR_SLOT_COVERAGE:
            continue

        # Find the true prefix (longest common prefix of all base_names in the group)
        base_names = [item["base_name"] for item in items]
        cn_prefix = _find_common_prefix(base_names)
        if len(cn_prefix) < 2:
            continue

        crafter_level = items[0]["crafterLevel"]

        # Build roles dict: role_name -> sorted list of item IDs
        roles: dict[str, list[int]] = defaultdict(list)
        for item in items:
            role_key = item["role"] if item["role"] else "_weapons"
            roles[role_key].append(item["resultItemId"])
        # Sort item IDs within each role
        roles = {k: sorted(v) for k, v in roles.items()}

        # Get EN/JA prefix from all items in the set
        all_item_ids = [item["resultItemId"] for item in items]
        en_prefix = _find_common_prefix(
            [name_maps.get(iid, {}).get("en", "") for iid in all_item_ids]
        )
        ja_prefix = _find_common_prefix(
            [name_maps.get(iid, {}).get("ja", "") for iid in all_item_ids]
        )

        raw_sets.append({
            "prefix": {
                "zh-CN": cn_prefix,
                "en": en_prefix or cn_prefix,
                "ja": ja_prefix or cn_prefix,
            },
            "ilvl": ilvl,
            "crafterLevel": crafter_level,
            "roles": roles,
        })

    print(f"  {len(raw_sets)} outfit sets detected")
    return raw_sets


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
