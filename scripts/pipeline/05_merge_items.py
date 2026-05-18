#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lib.io_utils import read_json, write_json
from lib.items_i18n import merge_items_with_i18n


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge CN base items with EN/JA item names.")
    parser.add_argument("--base-items", type=Path, required=True, help="Path to 03_items.base.cn.json.")
    parser.add_argument("--i18n-names", type=Path, required=True, help="Path to 04_items.i18n_name.json.")
    parser.add_argument("--output", type=Path, required=True, help="Output path for 05_items.merged.json.")
    args = parser.parse_args()

    merged_items = merge_items_with_i18n(read_json(args.base_items), read_json(args.i18n_names))
    write_json(args.output, merged_items)
    print(f"Wrote {len(merged_items)} merged items to {args.output}")


if __name__ == "__main__":
    main()
