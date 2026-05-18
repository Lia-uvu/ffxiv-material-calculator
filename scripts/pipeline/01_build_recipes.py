#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lib.io_utils import ensure_files_exist, write_json
from lib.recipe_cn import build_recipes


def main() -> None:
    parser = argparse.ArgumentParser(description="Build full recipes JSON from local CN CSV files.")
    parser.add_argument("--input-dir", type=Path, required=True, help="CN CSV repository root.")
    parser.add_argument("--output", type=Path, required=True, help="Output path for 01_recipes.full.json.")
    args = parser.parse_args()

    ensure_files_exist(args.input_dir, ["Recipe.csv", "RecipeLevelTable.csv", "Item.csv"])
    recipes, _ = build_recipes(args.input_dir, allow_remote=False)
    write_json(args.output, recipes)
    print(f"Wrote {len(recipes)} recipes to {args.output}")


if __name__ == "__main__":
    main()
