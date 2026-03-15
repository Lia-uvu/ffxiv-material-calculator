#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lib.io_utils import ensure_files_exist, try_git_rev_parse, utc_now_iso, write_json
from lib.items_cn import build_items_base_cn
from lib.items_i18n import build_i18n_name_rows, merge_items_with_i18n
from lib.pipeline_state import (
    create_publish_diff,
    extract_needed_item_ids,
    publish_outputs,
    validate_outputs,
    write_state_manifest,
)
from lib.recipe_cn import build_recipes

SCRIPT_VERSION = "1.0"


def build_manifest(current_repo: Path, cn_repo: Path, en_repo: Path, ja_repo: Path) -> dict:
    return {
        "runAt": utc_now_iso(),
        "scriptVersion": SCRIPT_VERSION,
        "currentRepoSha": try_git_rev_parse(current_repo),
        "upstream": {
            "cn": {"path": str(cn_repo), "sha": try_git_rev_parse(cn_repo)},
            "en": {"path": str(en_repo), "sha": try_git_rev_parse(en_repo)},
            "ja": {"path": str(ja_repo), "sha": try_git_rev_parse(ja_repo)},
        },
    }


def run_pipeline(
    *,
    current_repo: Path,
    cn_repo: Path,
    en_repo: Path,
    ja_repo: Path,
    work_dir: Path,
    publish_dir: Path,
    state_path: Path | None = None,
) -> dict:
    ensure_files_exist(cn_repo, ["Recipe.csv", "RecipeLevelTable.csv", "Item.csv"])
    ensure_files_exist(
        cn_repo,
        [
            "GatheringType.csv",
            "GatheringItem.csv",
            "GatheringPointBase.csv",
            "FishingSpot.csv",
            "GilShopItem.csv",
            "SpecialShop.csv",
            "GCScripShopItem.csv",
        ],
    )
    ensure_files_exist(en_repo, ["Item.csv"])
    ensure_files_exist(ja_repo, ["Item.csv"])

    work_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(current_repo, cn_repo, en_repo, ja_repo)
    manifest_path = work_dir / "00_manifest.json"
    write_json(manifest_path, manifest)

    recipes, _ = build_recipes(cn_repo, allow_remote=False)
    recipes_path = work_dir / "01_recipes.full.json"
    write_json(recipes_path, recipes)

    needed_item_ids = extract_needed_item_ids(recipes)
    if not needed_item_ids:
        raise ValueError("needed_item_ids is empty.")
    needed_ids_path = work_dir / "02_needed_item_ids.json"
    write_json(needed_ids_path, needed_item_ids)

    base_items, item_stats = build_items_base_cn(cn_repo, needed_item_ids, recipes, allow_remote=False)
    if not base_items:
        raise ValueError("CN items generation failed: no items were produced.")
    base_items_path = work_dir / "03_items.base.cn.json"
    write_json(base_items_path, base_items)

    i18n_name_rows = build_i18n_name_rows(en_repo, ja_repo, needed_item_ids)
    i18n_names_path = work_dir / "04_items.i18n_name.json"
    write_json(i18n_names_path, i18n_name_rows)

    merged_items = merge_items_with_i18n(base_items, i18n_name_rows)
    merged_items_path = work_dir / "05_items.merged.json"
    write_json(merged_items_path, merged_items)

    validation_report = validate_outputs(recipes, merged_items, i18n_name_rows)
    validation_path = work_dir / "06_validation_report.json"
    write_json(validation_path, validation_report)
    if not validation_report["passed"]:
        raise ValueError("Validation failed: recipes reference missing items.")

    publish_diff = create_publish_diff(publish_dir, recipes, merged_items)
    publish_diff_path = work_dir / "07_publish_diff.json"
    write_json(publish_diff_path, publish_diff)

    publish_outputs(publish_dir, recipes, merged_items, validation_report=validation_report)
    if state_path is not None:
        write_state_manifest(state_path, manifest)

    return {
        "manifest": manifest,
        "itemStats": item_stats,
        "validationReport": validation_report,
        "publishDiff": publish_diff,
        "paths": {
            "manifest": str(manifest_path),
            "recipes": str(recipes_path),
            "neededIds": str(needed_ids_path),
            "baseItems": str(base_items_path),
            "i18nNames": str(i18n_names_path),
            "mergedItems": str(merged_items_path),
            "validation": str(validation_path),
            "publishDiff": str(publish_diff_path),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full local CSV data pipeline.")
    parser.add_argument("--cn-repo", type=Path, required=True, help="CN CSV repository root.")
    parser.add_argument("--en-repo", type=Path, required=True, help="EN CSV repository root.")
    parser.add_argument("--ja-repo", type=Path, required=True, help="JA CSV repository root.")
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path("tmp/pipeline"),
        help="Temporary work directory for pipeline artifacts.",
    )
    parser.add_argument(
        "--publish-dir",
        type=Path,
        default=Path("src/data"),
        help="Runtime publish directory for final items.json and recipes.json.",
    )
    parser.add_argument(
        "--state-path",
        type=Path,
        default=Path("scripts/pipeline/state/last_successful_manifest.json"),
        help="Committed state metadata used by CI to detect upstream changes.",
    )
    args = parser.parse_args()

    result = run_pipeline(
        current_repo=Path.cwd(),
        cn_repo=args.cn_repo,
        en_repo=args.en_repo,
        ja_repo=args.ja_repo,
        work_dir=args.work_dir,
        publish_dir=args.publish_dir,
        state_path=args.state_path,
    )
    print(f"Pipeline completed successfully. Validation: {result['validationReport']['summary']}")


if __name__ == "__main__":
    main()
