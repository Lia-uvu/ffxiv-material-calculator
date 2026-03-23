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

# Equipment slot categories
ARMOR_SLOTS = {3, 4, 5, 7, 8}        # head, body, hands, legs, feet
ACCESSORY_SLOTS = {9, 10, 11, 12}     # earring, necklace, bracelet, ring
WEAPON_SLOTS = {1, 2, 13}             # main hand, off-hand/shield, two-hand
RING_SLOT = 12
GEAR_SLOTS = ARMOR_SLOTS | ACCESSORY_SLOTS

MIN_ARMOR_SLOT_COVERAGE = 3

# In FFXIV, some roles share accessories (Slaying accessories for all melee DPS).
# This maps each display role → which role's accessories it uses.
ACCESSORY_ROLE_FOR = {
    "tank": "tank",
    "healer": "healer",
    "maiming": "maiming",
    "striking": "maiming",   # shares Slaying (强攻) accessories with maiming
    "scouting": "maiming",   # shares Slaying (强攻) accessories with maiming
    "aiming": "aiming",
    "casting": "casting",
    "crafter": "crafter",
    "gatherer": "gatherer",
}

BATTLE_JOB_ABBRS = {
    "PLD", "WAR", "DRK", "GNB",
    "WHM", "SCH", "AST", "SGE",
    "MNK", "DRG", "NIN", "SAM", "RPR", "VPR",
    "BRD", "MCH", "DNC",
    "BLM", "SMN", "RDM", "PCT",
}


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


def build_class_job_category_map(cjc_text: str) -> dict[int, set[str]]:
    """Parse ClassJobCategory.csv → { categoryId: set of job abbreviations }."""
    rows = list(csv.reader(cjc_text.splitlines()))
    header_idx = -1
    header = []
    for idx, row in enumerate(rows[:10]):
        normalized = [cell.lstrip("\ufeff") for cell in row]
        if "#" in normalized and "Name" in normalized:
            header = normalized
            header_idx = idx
            break
    if header_idx < 0:
        raise ValueError("Could not find ClassJobCategory header")

    data_start = header_idx + 1
    while data_start < len(rows) and not rows[data_start][0].lstrip("\ufeff-").isdigit():
        data_start += 1

    idx_id = header.index("#")
    job_columns: list[tuple[int, str]] = []
    for abbr in BATTLE_JOB_ABBRS:
        if abbr in header:
            job_columns.append((header.index(abbr), abbr))

    result: dict[int, set[str]] = {}
    for row in rows[data_start:]:
        try:
            cat_id = int(row[idx_id])
        except (ValueError, IndexError):
            continue
        jobs = set()
        for col_idx, abbr in job_columns:
            if col_idx < len(row) and row[col_idx].strip().lower() == "true":
                jobs.add(abbr)
        if jobs:
            result[cat_id] = jobs
    return result


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

    # Parse Item.csv
    header, data = parse_csv_rows(cn_text_item, required=("#", "ItemSearchCategory", "Level{Item}", "EquipSlotCategory"))
    idx_key = header.index("#")
    idx_search_cat = header.index("ItemSearchCategory")
    idx_ilvl = header.index("Level{Item}")
    idx_equip_slot = header.index("EquipSlotCategory")
    idx_name = header.index("Name")
    idx_cjc = header.index("ClassJobCategory")

    item_search_cat = {}
    item_ilvl = {}
    item_equip_slot = {}
    item_cn_name = {}
    item_cjc = {}
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
        try:
            item_cjc[item_id] = int(row[idx_cjc])
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
            "classJobCategory": item_cjc.get(result_item_id, 0),
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
    if prefix and prefix[-1] != " " and any(c.isascii() and c.isalpha() for c in prefix):
        last_space = prefix.rfind(" ")
        if last_space > 0:
            prefix = prefix[:last_space + 1]
    return prefix.rstrip()


def _slugify(text: str) -> str:
    text = text.lower().strip().rstrip("'s").rstrip("'")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def _resolve_weapon_job(cjc_id: int, cjc_map: dict[int, set[str]]) -> str | None:
    """Resolve a weapon's ClassJobCategory to a single battle job abbreviation."""
    jobs = cjc_map.get(cjc_id, set())
    battle_jobs = jobs & BATTLE_JOB_ABBRS
    if len(battle_jobs) == 1:
        return battle_jobs.pop()
    if "PLD" in battle_jobs:
        return "PLD"
    if battle_jobs:
        return sorted(battle_jobs)[0]
    return None


def build_outfit_sets(
    recipes: list[dict],
    item_cn_names: dict[int, str],
    cjc_map: dict[int, set[str]],
) -> list[dict]:
    # ── Step 1: Filter candidates (non-weapon gear with role suffixes) ──
    gear_candidates = []
    weapon_candidates = []

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

        slot = r["equipSlotCategory"]
        if slot in WEAPON_SLOTS:
            weapon_candidates.append({**r, "cn_name": cn_name})
        else:
            base_name, role = _strip_role_suffix(cn_name)
            if role:
                gear_candidates.append({
                    **r, "cn_name": cn_name,
                    "base_name": base_name, "role": role,
                })

    print(f"  {len(gear_candidates)} gear candidates, {len(weapon_candidates)} weapon candidates")

    # ── Step 2: Group gear by (base_name, ilvl) → identify sets ──
    groups: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for c in gear_candidates:
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

        # Separate armor and accessories by role
        role_armor: dict[str, list[int]] = defaultdict(list)
        role_accessories: dict[str, list[int]] = defaultdict(list)

        for item in items:
            item_id = item["resultItemId"]
            slot = item["equipSlotCategory"]
            role_key = ROLE_SUFFIX_TO_KEY.get(item["role"], item["role"])

            if slot in ARMOR_SLOTS:
                role_armor[role_key].append(item_id)
            elif slot in ACCESSORY_SLOTS:
                role_accessories[role_key].append(item_id)
                if slot == RING_SLOT:
                    role_accessories[role_key].append(item_id)  # ring x2

        # ── Step 3: Build final role lists (armor + shared accessories) ──
        roles: dict[str, list[int]] = {}
        all_display_roles = set(role_armor.keys())
        for display_role in sorted(all_display_roles):
            armor_ids = role_armor.get(display_role, [])
            acc_role = ACCESSORY_ROLE_FOR.get(display_role, display_role)
            acc_ids = role_accessories.get(acc_role, [])
            combined = sorted(set(armor_ids)) + sorted(acc_ids)
            if combined:
                roles[display_role] = combined

        all_item_ids = sorted({item["resultItemId"] for item in items})

        raw_sets.append({
            "cn_prefix": cn_prefix,
            "ilvl": ilvl,
            "crafterLevel": crafter_level,
            "roles": roles,
            "weapons": {},
            "_all_item_ids": all_item_ids,
        })

    # ── Step 4: Match weapons to sets by name prefix ──
    # Sort sets by prefix length descending for longest-match-first
    sets_by_prefix = sorted(raw_sets, key=lambda s: -len(s["cn_prefix"]))
    for w in weapon_candidates:
        cn_name = w["cn_name"]
        job_abbr = _resolve_weapon_job(w["classJobCategory"], cjc_map)
        if not job_abbr:
            continue
        for s in sets_by_prefix:
            if cn_name.startswith(s["cn_prefix"]) and w["ilvl"] == s["ilvl"]:
                s["weapons"].setdefault(job_abbr, []).append(w["resultItemId"])
                if w["resultItemId"] not in s["_all_item_ids"]:
                    s["_all_item_ids"].append(w["resultItemId"])
                break

    # Sort weapon lists
    for s in raw_sets:
        s["weapons"] = {k: sorted(v) for k, v in s["weapons"].items()}
        s["_all_item_ids"] = sorted(s["_all_item_ids"])

    print(f"  {len(raw_sets)} outfit sets detected")
    return raw_sets


def generate_keys_and_i18n(
    raw_sets: list[dict],
    items_json: list[dict],
) -> tuple[list[dict], dict[str, dict[str, str]]]:
    name_by_id: dict[int, dict[str, str]] = {}
    for item in items_json:
        name_by_id[item["id"]] = item.get("name", {})

    i18n: dict[str, dict[str, str]] = {}
    output_sets: list[dict] = []
    key_counter: dict[str, int] = {}

    for s in raw_sets:
        all_ids = s["_all_item_ids"]

        prefixes = {}
        for locale in ("zh-CN", "en", "ja"):
            names = [name_by_id.get(iid, {}).get(locale, "") for iid in all_ids]
            prefixes[locale] = _find_common_prefix(names)

        en_slug = _slugify(prefixes.get("en", ""))
        if not en_slug:
            en_slug = _slugify(s["cn_prefix"])
        base_key = f"{en_slug}_{s['ilvl']}"

        key_counter[base_key] = key_counter.get(base_key, 0) + 1
        if key_counter[base_key] > 1:
            key = f"{base_key}_{key_counter[base_key]}"
        else:
            key = base_key

        i18n[key] = {
            "zh-CN": prefixes.get("zh-CN") or s["cn_prefix"],
            "en": prefixes.get("en") or s["cn_prefix"],
            "ja": prefixes.get("ja") or s["cn_prefix"],
        }

        output_set = {
            "key": key,
            "ilvl": s["ilvl"],
            "crafterLevel": s["crafterLevel"],
            "roles": s["roles"],
        }
        if s["weapons"]:
            output_set["weapons"] = s["weapons"]

        output_sets.append(output_set)

    return output_sets, i18n


def main():
    project_root = Path(__file__).resolve().parent.parent.parent
    publish_dir = project_root / "src" / "data"
    i18n_dir = project_root / "src" / "i18n" / "generated"

    print("Downloading Chinese CSVs from GitHub...")
    cn_recipe = fetch_csv(f"{BASE_URL_CN}/Recipe.csv")
    cn_level = fetch_csv(f"{BASE_URL_CN}/RecipeLevelTable.csv")
    cn_item = fetch_csv(f"{BASE_URL_CN}/Item.csv")
    cn_cjc = fetch_csv(f"{BASE_URL_CN}/ClassJobCategory.csv")

    print("Building ClassJobCategory map...")
    cjc_map = build_class_job_category_map(cn_cjc)
    print(f"  {len(cjc_map)} categories with battle jobs")

    print("Building enriched recipe data...")
    recipes, item_cn_names = build_enriched_data(cn_recipe, cn_level, cn_item)
    print(f"  {len(recipes)} recipes parsed")

    print("Detecting outfit sets...")
    raw_sets = build_outfit_sets(recipes, item_cn_names, cjc_map)

    items_json_path = publish_dir / "items.json"
    print(f"Loading {items_json_path} for multilingual names...")
    with open(items_json_path, encoding="utf-8") as f:
        items_json = json.load(f)

    print("Generating keys and i18n...")
    output_sets, i18n_names = generate_keys_and_i18n(raw_sets, items_json)

    output_sets.sort(key=lambda s: (-s["crafterLevel"], -s["ilvl"], s["key"]))

    output_path = publish_dir / "outfitSets.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_sets, f, ensure_ascii=False, indent=2)
    print(f"Written {len(output_sets)} outfit sets to {output_path}")

    i18n_dir.mkdir(parents=True, exist_ok=True)
    i18n_path = i18n_dir / "outfitSetNames.json"
    with open(i18n_path, "w", encoding="utf-8") as f:
        json.dump(i18n_names, f, ensure_ascii=False, indent=2)
    print(f"Written {len(i18n_names)} i18n entries to {i18n_path}")


if __name__ == "__main__":
    main()
