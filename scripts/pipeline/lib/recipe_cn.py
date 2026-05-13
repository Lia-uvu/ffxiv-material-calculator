from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from .io_utils import read_text_from_dir_or_remote

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

RESTORED_UNMARKETABLE_RESULT_NAME_KEYWORDS = ("第四期重建用",)


def load_recipe_inputs(
    input_dir: Path | None,
    *,
    allow_remote: bool,
) -> tuple[str, str, str]:
    base_url = BASE_URL if allow_remote else None
    recipe_text = read_text_from_dir_or_remote(input_dir, "Recipe.csv", base_url)
    level_text = read_text_from_dir_or_remote(input_dir, "RecipeLevelTable.csv", base_url)
    item_text = read_text_from_dir_or_remote(input_dir, "Item.csv", base_url)
    return recipe_text, level_text, item_text


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


def parse_item_recipe_filter_metadata(text: str) -> Dict[int, tuple[int, str]]:
    rows = list(csv.reader(text.splitlines()))
    header = rows[1]
    idx_key = header.index("#")
    idx_name = header.index("Name")
    idx_cat = header.index("ItemSearchCategory")
    result: Dict[int, tuple[int, str]] = {}
    for row in rows[4:]:
        if len(row) <= max(idx_key, idx_name, idx_cat):
            continue
        try:
            item_id = int(row[idx_key])
            category = int(row[idx_cat])
        except ValueError:
            continue
        result[item_id] = (category, row[idx_name].strip())
    return result


def should_keep_recipe_result(
    item_id: int,
    item_filter_metadata: Dict[int, tuple[int, str]],
) -> bool:
    item_search_category, item_name = item_filter_metadata.get(item_id, (0, ""))
    if item_search_category != 0:
        return True
    return any(keyword in item_name for keyword in RESTORED_UNMARKETABLE_RESULT_NAME_KEYWORDS)


def parse_recipe_csv(
    text: str,
    item_filter_metadata: Dict[int, tuple[int, str]],
) -> Tuple[List[Dict], List[int]]:
    rows = list(csv.reader(text.splitlines()))
    header = rows[1]

    def get_index(name: str) -> int:
        return header.index(name)

    idx_number = get_index("#")
    idx_craft = get_index("CraftType")
    idx_level_table = get_index("RecipeLevelTable")
    idx_result_item = get_index("Item{Result}")
    idx_result_amount = get_index("Amount{Result}")
    idx_patch = get_index("PatchNumber")
    idx_secret = get_index("SecretRecipeBook")

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

        if not should_keep_recipe_result(result_item_id, item_filter_metadata):
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

        patch = parse_patch_number(row[idx_patch])

        try:
            secret_recipe_book = int(row[idx_secret])
        except (ValueError, IndexError):
            secret_recipe_book = 0

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
            "secretRecipeBook": secret_recipe_book,
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
        recipe["itemLevel"] = level_table.get(level_table_id, 0)


def build_recipes(input_dir: Path | None, *, allow_remote: bool) -> tuple[List[Dict], List[int]]:
    recipe_text, level_text, item_text = load_recipe_inputs(input_dir, allow_remote=allow_remote)
    level_table = parse_recipe_level_table(level_text)
    item_filter_metadata = parse_item_recipe_filter_metadata(item_text)
    recipes, needed_item_ids = parse_recipe_csv(recipe_text, item_filter_metadata)
    update_item_levels(recipes, level_table)
    return recipes, needed_item_ids
