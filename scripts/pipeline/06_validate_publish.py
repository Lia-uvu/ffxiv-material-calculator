#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from lib.io_utils import read_json, write_json
from lib.pipeline_state import validate_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate pipeline outputs before publishing.")
    parser.add_argument("--recipes", type=Path, required=True, help="Path to 01_recipes.full.json.")
    parser.add_argument("--items", type=Path, required=True, help="Path to 05_items.merged.json.")
    parser.add_argument("--i18n-names", type=Path, required=True, help="Path to 04_items.i18n_name.json.")
    parser.add_argument("--output", type=Path, required=True, help="Output path for 06_validation_report.json.")
    args = parser.parse_args()

    report = validate_outputs(
        read_json(args.recipes),
        read_json(args.items),
        read_json(args.i18n_names),
    )
    write_json(args.output, report)
    print(f"Wrote validation report to {args.output}")
    print(f"Validation passed: {report['passed']}")
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
