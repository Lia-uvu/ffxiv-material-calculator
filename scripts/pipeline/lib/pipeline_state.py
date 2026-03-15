from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .io_utils import read_json, write_json


def extract_needed_item_ids(recipes: list[dict]) -> list[int]:
    item_ids: set[int] = set()
    for recipe in recipes:
        result_item_id = recipe.get("resultItemId")
        if isinstance(result_item_id, int) and result_item_id > 0:
            item_ids.add(result_item_id)
        for material in recipe.get("materials", []):
            item_id = material.get("itemId")
            if isinstance(item_id, int) and item_id > 0:
                item_ids.add(item_id)
    return sorted(item_ids)


def validate_outputs(
    recipes: list[dict],
    merged_items: list[dict],
    i18n_name_rows: list[dict],
) -> dict[str, Any]:
    item_ids = {item["id"] for item in merged_items}
    missing_recipe_item_refs = []
    for recipe in recipes:
        result_item_id = recipe.get("resultItemId")
        if result_item_id not in item_ids:
            missing_recipe_item_refs.append(
                {"recipeId": recipe.get("id"), "kind": "result", "itemId": result_item_id}
            )
        for material in recipe.get("materials", []):
            item_id = material.get("itemId")
            if item_id not in item_ids:
                missing_recipe_item_refs.append(
                    {"recipeId": recipe.get("id"), "kind": "material", "itemId": item_id}
                )

    raw_name_map = {row["id"]: row for row in i18n_name_rows}
    missing_names = {"en": [], "ja": []}
    for item in merged_items:
        name_row = raw_name_map.get(item["id"], {"id": item["id"]})
        if not name_row.get("en"):
            missing_names["en"].append(item["id"])
        if not name_row.get("ja"):
            missing_names["ja"].append(item["id"])

    return {
        "passed": not missing_recipe_item_refs,
        "summary": {
            "recipeCount": len(recipes),
            "itemCount": len(merged_items),
            "missingRecipeItemRefCount": len(missing_recipe_item_refs),
            "missingEnNameCount": len(missing_names["en"]),
            "missingJaNameCount": len(missing_names["ja"]),
        },
        "errors": {
            "missingRecipeItemRefs": missing_recipe_item_refs,
        },
        "warnings": {
            "missingI18nNames": missing_names,
        },
    }


def build_publish_diff(existing_payload: list[dict], next_payload: list[dict], *, key: str) -> dict[str, Any]:
    existing_by_id = {item[key]: item for item in existing_payload}
    next_by_id = {item[key]: item for item in next_payload}

    existing_ids = set(existing_by_id)
    next_ids = set(next_by_id)
    added_ids = sorted(next_ids - existing_ids)
    removed_ids = sorted(existing_ids - next_ids)
    changed_ids = sorted(
        item_id
        for item_id in existing_ids & next_ids
        if existing_by_id[item_id] != next_by_id[item_id]
    )
    return {
        "addedCount": len(added_ids),
        "removedCount": len(removed_ids),
        "changedCount": len(changed_ids),
        "addedIds": added_ids[:50],
        "removedIds": removed_ids[:50],
        "changedIds": changed_ids[:50],
    }


def create_publish_diff(
    publish_dir: Path,
    recipes: list[dict],
    items: list[dict],
) -> dict[str, Any]:
    existing_recipes = read_json(publish_dir / "recipes.json") if (publish_dir / "recipes.json").exists() else []
    existing_items = read_json(publish_dir / "items.json") if (publish_dir / "items.json").exists() else []
    return {
        "recipes": build_publish_diff(existing_recipes, recipes, key="id"),
        "items": build_publish_diff(existing_items, items, key="id"),
    }


def publish_outputs(
    publish_dir: Path,
    recipes: list[dict],
    items: list[dict],
    *,
    validation_report: dict[str, Any],
) -> None:
    if not validation_report.get("passed"):
        raise ValueError("Validation failed; refusing to publish output files.")
    write_json(publish_dir / "recipes.json", recipes)
    write_json(publish_dir / "items.json", items)


def write_state_manifest(state_path: Path, manifest: dict[str, Any]) -> None:
    state_payload = {
        "publishedAt": manifest.get("runAt"),
        "currentRepoSha": manifest.get("currentRepoSha"),
        "upstream": manifest.get("upstream", {}),
        "scriptVersion": manifest.get("scriptVersion"),
    }
    write_json(state_path, state_payload)


def summarize_methods(items: list[dict]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for item in items:
        for method in item.get("obtainMethods", []):
            counter[method] += 1
    return dict(sorted(counter.items()))
