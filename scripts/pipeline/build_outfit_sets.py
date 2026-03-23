#!/usr/bin/env python3
"""Generate outfitSets.json and outfitSetNames i18n from local static data.

Reads from:
  - src/data/items.json          (multilingual names)
  - src/data/recipes.json        (recipe → resultItemId, itemLevel)
  - src/data/outfitSetMeta.json  (ilvl, equipSlotCategory, classJobCategory, secretRecipeBook)

No network access required.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

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

MIN_ARMOR_SLOT_COVERAGE = 3

# In FFXIV, some roles share accessories (Slaying accessories for all melee DPS).
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


# ── Data loading from static files ──────────────────────────────────────────


def load_local_data(data_dir: Path) -> tuple[list[dict], dict[int, str], dict[int, set[str]]]:
    """Load and merge items.json, recipes.json, and outfitSetMeta.json.

    Returns:
        enriched_recipes: list of dicts with keys:
            resultItemId, crafterLevel, secretRecipeBook, ilvl,
            equipSlotCategory, classJobCategory
        item_cn_names: { itemId: CN name }
        cjc_map: { categoryId: set of job abbreviations }
    """
    with open(data_dir / "items.json", encoding="utf-8") as f:
        items_json = json.load(f)
    with open(data_dir / "recipes.json", encoding="utf-8") as f:
        recipes_json = json.load(f)
    with open(data_dir / "outfitSetMeta.json", encoding="utf-8") as f:
        meta = json.load(f)

    # Build CN name lookup
    item_cn_names: dict[int, str] = {}
    for item in items_json:
        cn_name = item.get("name", {}).get("zh-CN", "")
        if cn_name:
            item_cn_names[item["id"]] = cn_name

    # Build metadata lookups
    master_ids = set(meta["masterRecipeItemIds"])
    item_meta = {int(k): v for k, v in meta["items"].items()}
    cjc_map: dict[int, set[str]] = {
        int(k): set(v) for k, v in meta["cjcJobs"].items()
    }

    # Merge recipes with metadata
    enriched: list[dict] = []
    for r in recipes_json:
        result_id = r["resultItemId"]
        im = item_meta.get(result_id)
        if not im:
            continue
        enriched.append({
            "resultItemId": result_id,
            "crafterLevel": r["itemLevel"],
            "secretRecipeBook": 1 if result_id in master_ids else 0,
            "ilvl": im["ilvl"],
            "equipSlotCategory": im["slot"],
            "classJobCategory": im["cjc"],
        })

    return enriched, item_cn_names, cjc_map


# ── Outfit set detection (unchanged logic) ──────────────────────────────────


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
    # ── Step 1: Filter candidates ──
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
    data_dir = project_root / "src" / "data"
    i18n_dir = project_root / "src" / "i18n" / "generated"

    print("Loading local static data...")
    recipes, item_cn_names, cjc_map = load_local_data(data_dir)
    print(f"  {len(recipes)} enriched recipes loaded")

    print("Detecting outfit sets...")
    raw_sets = build_outfit_sets(recipes, item_cn_names, cjc_map)

    items_json_path = data_dir / "items.json"
    print(f"Loading {items_json_path} for multilingual names...")
    with open(items_json_path, encoding="utf-8") as f:
        items_json = json.load(f)

    print("Generating keys and i18n...")
    output_sets, i18n_names = generate_keys_and_i18n(raw_sets, items_json)

    output_sets.sort(key=lambda s: (-s["crafterLevel"], -s["ilvl"], s["key"]))

    output_path = data_dir / "outfitSets.json"
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
