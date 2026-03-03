#!/usr/bin/env python3
"""Convert FFXIV CN Recipe.csv into recipes.json and needed_item_ids.json."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from urllib.request import urlopen

BASE_URL = "https://raw.githubusercontent.com/thewakingsands/ffxiv-datamining-cn/master"

CRAFT_TYPE_TO_JOB = {
    0: "CARPENTER",
    1: "BLACKSMITH",
    2: "ARMORER",
    3: "GOLDSMITH",
    4: "LEATHERWORKER",
    5: "WEAVER",
    6: "ALCHEMIST",
    7: "CULINARIAN",
}


def fetch_text(path: Path | None, filename: str) -> str:
    if path:
        file_path = path / filename
        return file_path.read_text(encoding="utf-8-sig")
    url = f"{BASE_URL}/{filename}"
    with urlopen(url) as response:
        return response.read().decode("utf-8-sig")


def parse_recipe_level_table(text: str) -> Dict[int, int]:
    lines = text.splitlines()
    rows = list(csv.reader(lines))
    header = rows[1]
    idx_key = header.index("#")
    idx_level = header.index("ClassJobLevel")
    levels: Dict[int, int] = {}
    for row in rows[4:]:
        if len(row) <= max(idx_key, idx_level):
            continue
        try:
            key = int(row[idx_key])
        except ValueError:
            continue
        try:
            level = int(row[idx_level])
        except ValueError:
            level = 0
        levels[key] = level
    return levels


def parse_item_search_categories(text: str) -> Dict[int, int]:
    """Build a map of item_id -> ItemSearchCategory from Item.csv.

    ItemSearchCategory == 0 means the item cannot be searched on the market board,
    i.e. it is untradable / content-specific (e.g. Cosmic Exploration deliverables).
    Only items with ItemSearchCategory != 0 should be included as recipe results.
    """
    lines = text.splitlines()
    rows = list(csv.reader(lines))
    header = rows[1]
    idx_key = header.index("#")
    idx_cat = header.index("ItemSearchCategory")
    result: Dict[int, int] = {}
    for row in rows[4:]:
        if len(row) <= max(idx_key, idx_cat):
            continue
        try:
            item_id = int(row[idx_key])
            cat = int(row[idx_cat])
        except ValueError:
            continue
        result[item_id] = cat
    return result


def parse_recipe_csv(text: str, item_search_categories: Dict[int, int]) -> Tuple[List[Dict], List[int]]:
    lines = text.splitlines()
    rows = list(csv.reader(lines))
    header = rows[1]

    def get_index(name: str) -> int:
        return header.index(name)

    idx_number = get_index("Number")
    idx_craft = get_index("CraftType")
    idx_level_table = get_index("RecipeLevelTable")
    idx_result_item = get_index("Item{Result}")
    idx_result_amount = get_index("Amount{Result}")
    idx_patch = get_index("PatchNumber")

    ingredient_pairs = []
    for i in range(8):
        item_idx = get_index(f"Item{{Ingredient}}[{i}]")
        amount_idx = get_index(f"Amount{{Ingredient}}[{i}]")
        ingredient_pairs.append((item_idx, amount_idx))

    recipes: List[Dict] = []
    item_ids: set[int] = set()

    for row in rows[4:]:
        if len(row) <= idx_patch:
            continue
        try:
            recipe_id = int(row[idx_number])
        except ValueError:
            continue
        if recipe_id <= 0:
            continue

        try:
            result_item_id = int(row[idx_result_item])
        except ValueError:
            result_item_id = 0
        if result_item_id <= 0:
            continue

        # Filter: skip recipes whose result item is not market-searchable.
        # ItemSearchCategory == 0 means untradable / content-specific
        # (e.g. Cosmic Exploration deliverables stored in Cosmopouch).
        if item_search_categories.get(result_item_id, 0) == 0:
            continue

        try:
            result_amount = int(row[idx_result_amount])
        except ValueError:
            result_amount = 0

        craft_type = int(row[idx_craft]) if row[idx_craft] else 0
        job = CRAFT_TYPE_TO_JOB.get(craft_type)

        try:
            level_table_id = int(row[idx_level_table])
        except ValueError:
            level_table_id = 0

        patch_raw = row[idx_patch]
        patch = parse_patch_number(patch_raw)

        materials = []
        for item_idx, amount_idx in ingredient_pairs:
            try:
                item_id = int(row[item_idx])
            except ValueError:
                item_id = 0
            try:
                amount = int(row[amount_idx])
            except ValueError:
                amount = 0
            if item_id > 0 and amount > 0:
                materials.append({"itemId": item_id, "amount": amount})
                item_ids.add(item_id)

        recipe = {
            "id": recipe_id,
            "resultItemId": result_item_id,
            "resultAmount": result_amount,
            "job": job,
            "itemLevel": level_table_id,
            "patch": patch,
            "materials": materials,
        }
        recipes.append(recipe)
        item_ids.add(result_item_id)

    return recipes, sorted(item_ids)


def parse_patch_number(value: str) -> str:
    try:
        number = int(value)
    except ValueError:
        return "0.0"
    if number in (0, 65535):
        return "0.0"
    major = number // 100
    minor = number % 100
    return f"{major}.{minor}"


def update_item_levels(recipes: Iterable[Dict], level_table: Dict[int, int]) -> None:
    for recipe in recipes:
        level_table_id = recipe.get("itemLevel", 0)
        if level_table_id in level_table:
            recipe["itemLevel"] = level_table[level_table_id]
        else:
            recipe["itemLevel"] = 0


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing Recipe.csv/CraftType.csv/RecipeLevelTable.csv. Defaults to remote repo.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("src/data"),
        help="Output directory for recipes.json and needed_item_ids.json.",
    )
    args = parser.parse_args()

    recipe_text = fetch_text(args.input_dir, "Recipe.csv")
    level_text = fetch_text(args.input_dir, "RecipeLevelTable.csv")
    item_text = fetch_text(args.input_dir, "Item.csv")

    level_table = parse_recipe_level_table(level_text)
    item_search_categories = parse_item_search_categories(item_text)
    recipes, item_ids = parse_recipe_csv(recipe_text, item_search_categories)
    update_item_levels(recipes, level_table)

    write_json(args.output_dir / "recipes.json", recipes)
    write_json(args.output_dir / "needed_item_ids.json", item_ids)

    print(f"Wrote {len(recipes)} recipes to {args.output_dir / 'recipes.json'}")
    print(f"Wrote {len(item_ids)} item ids to {args.output_dir / 'needed_item_ids.json'}")


if __name__ == "__main__":
    main()
