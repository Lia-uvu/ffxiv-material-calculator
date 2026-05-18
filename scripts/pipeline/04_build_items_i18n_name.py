#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lib.io_utils import ensure_files_exist, read_json, write_json
from lib.items_i18n import build_i18n_name_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Build i18n item names from EN/JA Item.csv.")
    parser.add_argument("--en-dir", type=Path, required=True, help="EN CSV repository root.")
    parser.add_argument("--ja-dir", type=Path, required=True, help="JA CSV repository root.")
    parser.add_argument("--needed-ids", type=Path, required=True, help="Path to 02_needed_item_ids.json.")
    parser.add_argument("--output", type=Path, required=True, help="Output path for 04_items.i18n_name.json.")
    args = parser.parse_args()

    ensure_files_exist(args.en_dir, ["Item.csv"])
    ensure_files_exist(args.ja_dir, ["Item.csv"])
    rows = build_i18n_name_rows(args.en_dir, args.ja_dir, read_json(args.needed_ids))
    write_json(args.output, rows)
    print(f"Wrote {len(rows)} i18n name rows to {args.output}")


if __name__ == "__main__":
    main()
