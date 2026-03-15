#!/usr/bin/env python3
"""Convert FFXIV CN Item.csv into items.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
PIPELINE_DIR = ROOT_DIR / "scripts" / "pipeline"
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

from lib.io_utils import read_json, write_json
from lib.items_cn import IGNORED_SOURCES, build_items_base_cn
from lib.pipeline_state import summarize_methods


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing Item.csv and related CN CSVs. Defaults to remote repo.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("src/data"),
        help="Directory containing needed_item_ids.json and recipes.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("src/data"),
        help="Output directory for items.json.",
    )
    args = parser.parse_args()

    needed_ids = read_json(args.data_dir / "needed_item_ids.json")
    recipes = read_json(args.data_dir / "recipes.json")
    items, stats = build_items_base_cn(
        args.input_dir,
        needed_ids,
        recipes,
        allow_remote=args.input_dir is None,
    )

    write_json(args.output_dir / "items.json", items)
    print(f"Item rows total: {stats['rows_total']}")
    print(f"Item rows with valid id: {stats['rows_with_id']}")
    print(f"Item rows matched needed ids: {stats['rows_needed']}")
    print(f"Item rows with name: {stats['rows_with_name']}")
    print(f"Wrote {stats['items_written']} items to {args.output_dir / 'items.json'}")
    print(f"Method summary: {summarize_methods(items)}")
    print("Ignored sources:")
    for source in IGNORED_SOURCES:
        print(f"- {source}")


if __name__ == "__main__":
    main()
