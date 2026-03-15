#!/usr/bin/env python3
"""Convert FFXIV CN Recipe.csv into recipes.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
PIPELINE_DIR = ROOT_DIR / "scripts" / "pipeline"
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

from lib.io_utils import write_json
from lib.pipeline_state import extract_needed_item_ids
from lib.recipe_cn import build_recipes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing Recipe.csv/RecipeLevelTable.csv/Item.csv. Defaults to remote repo.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("src/data"),
        help="Output directory for recipes.json.",
    )
    parser.add_argument(
        "--write-needed-item-ids",
        action="store_true",
        help="Also write needed_item_ids.json for compatibility with legacy manual workflows.",
    )
    args = parser.parse_args()

    recipes, _ = build_recipes(args.input_dir, allow_remote=args.input_dir is None)
    write_json(args.output_dir / "recipes.json", recipes)
    print(f"Wrote {len(recipes)} recipes to {args.output_dir / 'recipes.json'}")

    if args.write_needed_item_ids:
        needed_item_ids = extract_needed_item_ids(recipes)
        write_json(args.output_dir / "needed_item_ids.json", needed_item_ids)
        print(f"Wrote {len(needed_item_ids)} item ids to {args.output_dir / 'needed_item_ids.json'}")


if __name__ == "__main__":
    main()
