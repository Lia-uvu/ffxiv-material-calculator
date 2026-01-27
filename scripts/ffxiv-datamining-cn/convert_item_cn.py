#!/usr/bin/env python3
"""Convert FFXIV CN Item.csv into items.json."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Set
from urllib.request import urlopen

BASE_URL = "https://raw.githubusercontent.com/thewakingsands/ffxiv-datamining-cn/master"

MINER_GATHER_TYPES = {"采掘", "碎石"}
BOTANIST_GATHER_TYPES = {"采伐", "割草"}

OBTAIN_METHOD_ORDER = [
    "CRAFT",
    "GATHER_MINER",
    "GATHER_BOTANIST",
    "MARKET",
    "NPC",
]


def fetch_text(path: Path | None, filename: str) -> str:
    if path:
        file_path = path / filename
        return file_path.read_text(encoding="utf-8-sig")
    url = f"{BASE_URL}/{filename}"
    with urlopen(url) as response:
        return response.read().decode("utf-8-sig")


def load_needed_ids(path: Path) -> List[int]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_recipe_result_ids(path: Path) -> Set[int]:
    if not path.exists():
        return set()
    recipes = json.loads(path.read_text(encoding="utf-8"))
    return {recipe.get("resultItemId") for recipe in recipes if recipe.get("resultItemId")}


def parse_gathering_types(text: str) -> Dict[int, str]:
    rows = list(csv.reader(text.splitlines()))
    header = rows[1]
    idx_key = header.index("#")
    idx_name = header.index("Name")
    mapping: Dict[int, str] = {}
    for row in rows[4:]:
        if len(row) <= max(idx_key, idx_name):
            continue
        try:
            key = int(row[idx_key])
        except ValueError:
            continue
        name = row[idx_name]
        mapping[key] = name
    return mapping


def parse_gathering_item_map(text: str) -> Dict[int, int]:
    rows = list(csv.reader(text.splitlines()))
    header = rows[1]
    idx_key = header.index("#")
    idx_item = header.index("Item")
    mapping: Dict[int, int] = {}
    for row in rows[4:]:
        if len(row) <= max(idx_key, idx_item):
            continue
        try:
            key = int(row[idx_key])
            item_id = int(row[idx_item])
        except ValueError:
            continue
        if item_id > 0:
            mapping[key] = item_id
    return mapping


def parse_gathering_point_base(text: str) -> List[tuple[int, List[int]]]:
    rows = list(csv.reader(text.splitlines()))
    header = rows[1]
    idx_type = header.index("GatheringType")
    item_indices = [header.index(f"Item[{i}]") for i in range(8)]
    result: List[tuple[int, List[int]]] = []
    for row in rows[4:]:
        if len(row) <= idx_type:
            continue
        try:
            gather_type = int(row[idx_type])
        except ValueError:
            continue
        item_ids: List[int] = []
        for idx in item_indices:
            if len(row) <= idx:
                continue
            try:
                item_id = int(row[idx])
            except ValueError:
                continue
            if item_id > 0:
                item_ids.append(item_id)
        if item_ids:
            result.append((gather_type, item_ids))
    return result


def collect_gather_methods(
    types_text: str, items_text: str, points_text: str
) -> Dict[int, Set[str]]:
    type_map = parse_gathering_types(types_text)
    gathering_item_map = parse_gathering_item_map(items_text)
    point_rows = parse_gathering_point_base(points_text)

    methods_by_item: Dict[int, Set[str]] = {}
    for gather_type, gathering_items in point_rows:
        type_name = type_map.get(gather_type)
        if type_name in MINER_GATHER_TYPES:
            method = "GATHER_MINER"
        elif type_name in BOTANIST_GATHER_TYPES:
            method = "GATHER_BOTANIST"
        else:
            continue
        for gathering_item_id in gathering_items:
            item_id = gathering_item_map.get(gathering_item_id)
            if not item_id:
                continue
            methods_by_item.setdefault(item_id, set()).add(method)
    return methods_by_item


def build_obtain_methods(
    item_id: int,
    is_crystal: bool,
    is_untradable: bool,
    price_low: int,
    craftable_ids: Set[int],
    gather_methods: Dict[int, Set[str]],
) -> List[str]:
    methods: Set[str] = set()
    if item_id in craftable_ids:
        methods.add("CRAFT")
    if not is_untradable:
        methods.add("MARKET")
    if price_low > 0:
        methods.add("NPC")
    methods.update(gather_methods.get(item_id, set()))
    if is_crystal:
        methods.update({"GATHER_MINER", "GATHER_BOTANIST"})
    return [method for method in OBTAIN_METHOD_ORDER if method in methods]


def parse_items(
    text: str,
    needed_ids: Iterable[int],
    craftable_ids: Set[int],
    gather_methods: Dict[int, Set[str]],
) -> List[Dict]:
    needed_set = set(needed_ids)
    rows = list(csv.reader(text.splitlines()))
    header = rows[1]

    def get_index(name: str) -> int:
        return header.index(name)

    idx_key = get_index("#")
    idx_name = get_index("Name")
    idx_ui_category = get_index("ItemUICategory")
    idx_untradable = get_index("IsUntradable")
    idx_price_low = get_index("Price{Low}")

    items_by_id: Dict[int, Dict] = {}
    for row in rows[4:]:
        if len(row) <= idx_key:
            continue
        try:
            item_id = int(row[idx_key])
        except ValueError:
            continue
        if item_id not in needed_set:
            continue
        name = row[idx_name].strip()
        if not name:
            continue
        is_crystal = row[idx_ui_category] == "59"
        is_untradable = row[idx_untradable].strip().lower() == "true"
        try:
            price_low = int(row[idx_price_low])
        except ValueError:
            price_low = 0
        obtain_methods = build_obtain_methods(
            item_id,
            is_crystal,
            is_untradable,
            price_low,
            craftable_ids,
            gather_methods,
        )
        items_by_id[item_id] = {
            "id": item_id,
            "name": {"en": name, "zh-CN": name, "ja": name},
            "isCrystal": is_crystal,
            "obtainMethods": obtain_methods,
        }

    return [items_by_id[item_id] for item_id in needed_ids if item_id in items_by_id]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing Item.csv and gathering CSVs. Defaults to remote repo.",
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

    needed_ids = load_needed_ids(args.data_dir / "needed_item_ids.json")
    craftable_ids = load_recipe_result_ids(args.data_dir / "recipes.json")

    item_text = fetch_text(args.input_dir, "Item.csv")
    gathering_type_text = fetch_text(args.input_dir, "GatheringType.csv")
    gathering_item_text = fetch_text(args.input_dir, "GatheringItem.csv")
    gathering_point_text = fetch_text(args.input_dir, "GatheringPointBase.csv")

    gather_methods = collect_gather_methods(
        gathering_type_text, gathering_item_text, gathering_point_text
    )
    items = parse_items(item_text, needed_ids, craftable_ids, gather_methods)

    write_json(args.output_dir / "items.json", items)
    print(f"Wrote {len(items)} items to {args.output_dir / 'items.json'}")


if __name__ == "__main__":
    main()
