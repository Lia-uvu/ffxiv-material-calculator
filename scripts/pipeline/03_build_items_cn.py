#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lib.io_utils import ensure_files_exist, read_json, write_json
from lib.items_cn import build_items_base_cn
from lib.pipeline_state import summarize_methods


def main() -> None:
    parser = argparse.ArgumentParser(description="Build CN base items JSON from local CSV files.")
    parser.add_argument("--input-dir", type=Path, required=True, help="CN CSV repository root.")
    parser.add_argument("--needed-ids", type=Path, required=True, help="Path to 02_needed_item_ids.json.")
    parser.add_argument("--recipes", type=Path, required=True, help="Path to 01_recipes.full.json.")
    parser.add_argument("--output", type=Path, required=True, help="Output path for 03_items.base.cn.json.")
    args = parser.parse_args()

    ensure_files_exist(
        args.input_dir,
        [
            "Item.csv",
            "GatheringType.csv",
            "GatheringItem.csv",
            "GatheringPointBase.csv",
            "FishingSpot.csv",
            "GilShopItem.csv",
            "SpecialShop.csv",
            "GCScripShopItem.csv",
        ],
    )
    items, stats = build_items_base_cn(
        args.input_dir,
        read_json(args.needed_ids),
        read_json(args.recipes),
        allow_remote=False,
    )
    write_json(args.output, items)
    print(f"Wrote {len(items)} items to {args.output}")
    print(f"Method summary: {summarize_methods(items)}")
    print(f"Stats: {stats}")


if __name__ == "__main__":
    main()
