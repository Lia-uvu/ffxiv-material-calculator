#!/usr/bin/env python3
"""Generate outfitSets.json and outfitSetNames i18n from enriched recipes and items data.

Only downloads Chinese CSVs from GitHub.  Multilingual set names are derived
from the already-built items.json (which contains zh-CN / en / ja names).
"""
from __future__ import annotations

import csv
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE_URL_CN = "https://raw.githubusercontent.com/thewakingsands/ffxiv-datamining-cn/master"

MIN_CRAFTER_LEVEL = 70

# Chinese role suffix → English role key
ROLE_SUFFIX_TO_KEY = {
    "御敌": "tank",
    "治愈": "healer",
    "制敌": "maiming",
    "强攻": "maiming",
    "强袭": "striking",
    "游击": "scouting",
    "精准": "aiming",
    "咏咒": "casting",
    "巧匠": "crafter",
    "大地": "gatherer",
}

ROLE_SUFFIXES = list(ROLE_SUFFIX_TO_KEY.keys())

# Equipment slot categories that count as "armor" (left-side gear + accessories).
ARMOR_SLOTS = {3, 4, 5, 7, 8}        # head, body, hands, legs, feet
ACCESSORY_SLOTS = {9, 10, 11, 12}     # earring, necklace, bracelet, ring
GEAR_SLOTS = ARMOR_SLOTS | ACCESSORY_SLOTS

# Minimum number of distinct armor slots a set must cover.
MIN_ARMOR_SLOT_COVERAGE = 3


def fetch_csv(url: str) -> str:
    print(f"  Downloading {url.split('/')[-1]}...")
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")


def locate_header_row(rows: list[list[str]], required_columns: tuple[str, ...]) -> tuple[int, list[str]]:
    for idx, row in enumerate(rows[:10]):
        normalized = [cell.lstrip("\ufeff") for cell in row]
        if all(column in normalized for column in required_columns):
            return idx, normalized
    raise ValueError(f"Could not find CSV header containing columns: {required_columns}")


def parse_csv_rows(text: str, required: tuple[str, ...] = ("#",)) -> tuple[list[str], list[list[str]]]:
    rows = list(csv.reader(text.splitlines()))
    header_idx, header = locate_header_row(rows, required)
    data = rows[header_idx + 1:]
    while data and data[0] and not data[0][0].lstrip("-").isdigit():
        data = data[1:]
    return header, data


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
    idx_name = header.index("Name")

    item_search_cat = {}
    item_ilvl = {}
    item_equip_slot = {}
    item_cn_name = {}
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
        name = row[idx_name].strip() if len(row) > idx_name else ""
        if name:
            item_cn_name[item_id] = name

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

    return recipes, item_cn_name


def _strip_role_suffix(cn_name: str) -> tuple[str, str]:
    for suffix in ROLE_SUFFIXES:
        if cn_name.startswith(suffix):
            continue
        idx = cn_name.find(suffix)
        if idx >= 2:
            return cn_name[:idx], suffix
    return cn_name, ""


def _find_common_prefix(names: list[str]) -> str:
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


def _slugify(text: str) -> str:
    """Convert a text prefix to a slug suitable for use as a key."""
    text = text.lower().strip().rstrip("'s").rstrip("'")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def build_outfit_sets(
    recipes: list[dict],
    item_cn_names: dict[int, str],
) -> list[dict]:
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
        cn_name = item_cn_names.get(r["resultItemId"], "")
        if not cn_name:
            continue
        base_name, role = _strip_role_suffix(cn_name)
        candidates.append({**r, "cn_name": cn_name, "base_name": base_name, "role": role})

    print(f"  {len(candidates)} candidate items after filtering")

    groups: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for c in candidates:
        groups[(c["base_name"], c["ilvl"])].append(c)

    raw_sets: list[dict] = []
    for (base_name, ilvl), items in groups.items():
        armor_slots_covered = {item["equipSlotCategory"] for item in items} & ARMOR_SLOTS
        if len(armor_slots_covered) < MIN_ARMOR_SLOT_COVERAGE:
            continue

        base_names = [item["base_name"] for item in items]
        cn_prefix = _find_common_prefix(base_names)
        if len(cn_prefix) < 2:
            continue

        crafter_level = items[0]["crafterLevel"]

        # Build roles dict with English keys
        roles: dict[str, list[int]] = defaultdict(list)
        for item in items:
            if item["role"]:
                role_key = ROLE_SUFFIX_TO_KEY.get(item["role"], item["role"])
            else:
                role_key = "_weapons"
            roles[role_key].append(item["resultItemId"])
        roles = {k: sorted(v) for k, v in roles.items()}

        # Collect all item IDs for i18n generation later
        all_item_ids = sorted({item["resultItemId"] for item in items})

        raw_sets.append({
            "cn_prefix": cn_prefix,
            "ilvl": ilvl,
            "crafterLevel": crafter_level,
            "roles": roles,
            "_all_item_ids": all_item_ids,  # temporary, stripped before output
        })

    print(f"  {len(raw_sets)} outfit sets detected")
    return raw_sets


def generate_keys_and_i18n(
    raw_sets: list[dict],
    items_json: list[dict],
) -> tuple[list[dict], dict[str, dict[str, str]]]:
    """Add 'key' to each set and generate i18n name mappings.

    Returns (output_sets, i18n_dict) where i18n_dict maps
    set key -> { "zh-CN": ..., "en": ..., "ja": ... }.
    """
    # Build item name lookup from items.json
    name_by_id: dict[int, dict[str, str]] = {}
    for item in items_json:
        name_by_id[item["id"]] = item.get("name", {})

    i18n: dict[str, dict[str, str]] = {}
    output_sets: list[dict] = []
    key_counter: dict[str, int] = {}

    for s in raw_sets:
        all_ids = s["_all_item_ids"]

        # Compute trilingual prefixes from items.json
        prefixes = {}
        for locale in ("zh-CN", "en", "ja"):
            names = [name_by_id.get(iid, {}).get(locale, "") for iid in all_ids]
            prefixes[locale] = _find_common_prefix(names)

        # Generate key from English prefix + ilvl
        en_slug = _slugify(prefixes.get("en", ""))
        if not en_slug:
            en_slug = _slugify(s["cn_prefix"])
        base_key = f"{en_slug}_{s['ilvl']}"

        # Handle duplicates
        key_counter[base_key] = key_counter.get(base_key, 0) + 1
        if key_counter[base_key] > 1:
            key = f"{base_key}_{key_counter[base_key]}"
        else:
            key = base_key

        # Store i18n entry
        i18n[key] = {
            "zh-CN": prefixes.get("zh-CN") or s["cn_prefix"],
            "en": prefixes.get("en") or s["cn_prefix"],
            "ja": prefixes.get("ja") or s["cn_prefix"],
        }

        # Build output set (without _all_item_ids)
        output_sets.append({
            "key": key,
            "ilvl": s["ilvl"],
            "crafterLevel": s["crafterLevel"],
            "roles": s["roles"],
        })

    return output_sets, i18n


def main():
    project_root = Path(__file__).resolve().parent.parent.parent
    publish_dir = project_root / "src" / "data"
    i18n_dir = project_root / "src" / "i18n" / "generated"

    print("Downloading Chinese CSVs from GitHub...")
    cn_recipe = fetch_csv(f"{BASE_URL_CN}/Recipe.csv")
    cn_level = fetch_csv(f"{BASE_URL_CN}/RecipeLevelTable.csv")
    cn_item = fetch_csv(f"{BASE_URL_CN}/Item.csv")

    print("Building enriched recipe data...")
    recipes, item_cn_names = build_enriched_data(cn_recipe, cn_level, cn_item)
    print(f"  {len(recipes)} recipes parsed")

    print("Detecting outfit sets...")
    raw_sets = build_outfit_sets(recipes, item_cn_names)

    # Load items.json for multilingual names
    items_json_path = publish_dir / "items.json"
    print(f"Loading {items_json_path} for multilingual names...")
    with open(items_json_path, encoding="utf-8") as f:
        items_json = json.load(f)

    print("Generating keys and i18n...")
    output_sets, i18n_names = generate_keys_and_i18n(raw_sets, items_json)

    # Sort sets: by crafter level desc, then ilvl desc, then key
    output_sets.sort(key=lambda s: (-s["crafterLevel"], -s["ilvl"], s["key"]))

    # Write outfitSets.json
    output_path = publish_dir / "outfitSets.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_sets, f, ensure_ascii=False, indent=2)
    print(f"Written {len(output_sets)} outfit sets to {output_path}")

    # Write i18n generated file
    i18n_dir.mkdir(parents=True, exist_ok=True)
    i18n_path = i18n_dir / "outfitSetNames.json"
    with open(i18n_path, "w", encoding="utf-8") as f:
        json.dump(i18n_names, f, ensure_ascii=False, indent=2)
    print(f"Written {len(i18n_names)} i18n entries to {i18n_path}")


if __name__ == "__main__":
    main()
