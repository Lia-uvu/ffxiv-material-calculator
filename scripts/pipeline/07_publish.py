#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lib.io_utils import read_json, write_json
from lib.pipeline_state import create_publish_diff, publish_outputs, write_state_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish final recipes/items JSON after validation.")
    parser.add_argument("--recipes", type=Path, required=True, help="Path to 01_recipes.full.json.")
    parser.add_argument("--items", type=Path, required=True, help="Path to 05_items.merged.json.")
    parser.add_argument("--validation", type=Path, required=True, help="Path to 06_validation_report.json.")
    parser.add_argument("--publish-dir", type=Path, required=True, help="Directory for runtime data files.")
    parser.add_argument("--diff-output", type=Path, required=True, help="Output path for 07_publish_diff.json.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional path to 00_manifest.json for updating committed state metadata.",
    )
    parser.add_argument(
        "--state-path",
        type=Path,
        default=None,
        help="Optional path for committed pipeline state metadata.",
    )
    args = parser.parse_args()

    recipes = read_json(args.recipes)
    items = read_json(args.items)
    validation_report = read_json(args.validation)
    publish_diff = create_publish_diff(args.publish_dir, recipes, items)
    write_json(args.diff_output, publish_diff)
    publish_outputs(args.publish_dir, recipes, items, validation_report=validation_report)
    if args.manifest and args.state_path and args.manifest.exists():
        write_state_manifest(args.state_path, read_json(args.manifest))
    print(f"Wrote publish diff to {args.diff_output}")
    print(f"Published runtime data to {args.publish_dir}")


if __name__ == "__main__":
    main()
