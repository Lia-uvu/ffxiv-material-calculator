#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lib.io_utils import read_json, write_json
from lib.pipeline_state import extract_needed_item_ids


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract needed item ids from full recipes JSON.")
    parser.add_argument("--recipes", type=Path, required=True, help="Path to 01_recipes.full.json.")
    parser.add_argument("--output", type=Path, required=True, help="Output path for 02_needed_item_ids.json.")
    args = parser.parse_args()

    recipes = read_json(args.recipes)
    needed_item_ids = extract_needed_item_ids(recipes)
    if not needed_item_ids:
        raise ValueError("needed_item_ids is empty.")
    write_json(args.output, needed_item_ids)
    print(f"Wrote {len(needed_item_ids)} item ids to {args.output}")


if __name__ == "__main__":
    main()
