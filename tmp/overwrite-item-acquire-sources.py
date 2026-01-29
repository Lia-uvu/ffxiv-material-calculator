#!/usr/bin/env python3
"""Overwrite items.obtainMethods using CN datamining CSVs.

默认行为：读取 src/data/items.json，输出到同目录的 items.patched.json。
如需直接覆写原文件，请加 --in-place。
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple
from urllib.request import urlopen

BASE_URL = "https://raw.githubusercontent.com/thewakingsands/ffxiv-datamining-cn/master"
DEFAULT_CN_REPO = Path("/workspace/ffxiv-datamining-cn")

MINER_GATHER_TYPES = {"采掘", "碎石"}
BOTANIST_GATHER_TYPES = {"采伐", "割草"}

OBTAIN_METHOD_ORDER = [
    "CRAFT",
    "GATHER_MINER",
    "GATHER_BOTANIST",
    "FISHING",
    "SHOP_GIL",
    "SHOP_SPECIAL",
    "SHOP_COLLECTABLES",
    "SHOP_GC",
    "MARKET",
]


def fetch_text(input_dir: Path | None, filename: str) -> str:
    if input_dir:
        file_path = input_dir / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8-sig")
    if DEFAULT_CN_REPO.exists():
        file_path = DEFAULT_CN_REPO / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8-sig")
    url = f"{BASE_URL}/{filename}"
    with urlopen(url) as response:
        return response.read().decode("utf-8-sig")


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


def parse_item_ids_by_columns(text: str, columns: Iterable[str]) -> Set[int]:
    rows = list(csv.reader(text.splitlines()))
    header = rows[1]
    indices = [header.index(column) for column in columns if column in header]
    if not indices:
        return set()
    result: Set[int] = set()
    for row in rows[4:]:
        for idx in indices:
            if len(row) <= idx:
                continue
            try:
                item_id = int(row[idx])
            except ValueError:
                continue
            if item_id > 0:
                result.add(item_id)
    return result


def parse_item_ids_by_prefix(text: str, prefix: str) -> Set[int]:
    rows = list(csv.reader(text.splitlines()))
    header = rows[1]
    indices = [idx for idx, name in enumerate(header) if name.startswith(prefix)]
    if not indices:
        return set()
    result: Set[int] = set()
    for row in rows[4:]:
        for idx in indices:
            if len(row) <= idx:
                continue
            try:
                item_id = int(row[idx])
            except ValueError:
                continue
            if item_id > 0:
                result.add(item_id)
    return result


def parse_item_info(text: str, needed_ids: Set[int]) -> Dict[int, Tuple[bool, int, bool]]:
    rows = list(csv.reader(text.splitlines()))
    header = rows[1]

    def get_index(name: str) -> int:
        return header.index(name)

    idx_key = get_index("#")
    idx_ui_category = get_index("ItemUICategory")
    idx_untradable = get_index("IsUntradable")
    idx_price_low = get_index("Price{Low}")

    info: Dict[int, Tuple[bool, int, bool]] = {}
    for row in rows[4:]:
        if len(row) <= idx_key:
            continue
        try:
            item_id = int(row[idx_key])
        except ValueError:
            continue
        if item_id not in needed_ids:
            continue
        is_crystal = row[idx_ui_category] == "59"
        is_untradable = row[idx_untradable].strip().lower() == "true"
        try:
            price_low = int(row[idx_price_low])
        except ValueError:
            price_low = 0
        info[item_id] = (is_untradable, price_low, is_crystal)
    return info


def load_recipe_result_ids(path: Path) -> Set[int]:
    if not path.exists():
        return set()
    recipes = json.loads(path.read_text(encoding="utf-8"))
    return {recipe.get("resultItemId") for recipe in recipes if recipe.get("resultItemId")}


def build_obtain_methods(
    item_id: int,
    is_crystal: bool,
    is_untradable: bool,
    craftable_ids: Set[int],
    gather_methods: Dict[int, Set[str]],
    fishing_ids: Set[int],
    gil_shop_ids: Set[int],
    special_shop_ids: Set[int],
    collectables_ids: Set[int],
    gc_scrip_ids: Set[int],
) -> List[str]:
    methods: Set[str] = set()
    if item_id in craftable_ids:
        methods.add("CRAFT")
    if not is_untradable:
        methods.add("MARKET")
    methods.update(gather_methods.get(item_id, set()))
    if item_id in fishing_ids:
        methods.add("FISHING")
    if item_id in gil_shop_ids:
        methods.add("SHOP_GIL")
    if item_id in special_shop_ids:
        methods.add("SHOP_SPECIAL")
    if item_id in collectables_ids:
        methods.add("SHOP_COLLECTABLES")
    if item_id in gc_scrip_ids:
        methods.add("SHOP_GC")
    if is_crystal:
        methods.update({"GATHER_MINER", "GATHER_BOTANIST"})
    return [method for method in OBTAIN_METHOD_ORDER if method in methods]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing CN CSVs. Defaults to /workspace/ffxiv-datamining-cn or remote repo.",
    )
    parser.add_argument(
        "--items",
        type=Path,
        default=Path("src/data/items.json"),
        help="Path to items.json.",
    )
    parser.add_argument(
        "--recipes",
        type=Path,
        default=Path("src/data/recipes.json"),
        help="Path to recipes.json.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path. Defaults to items.patched.json next to items.json.",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite items.json in place.",
    )
    args = parser.parse_args()

    items_path = args.items
    items = json.loads(items_path.read_text(encoding="utf-8"))
    item_ids = {item.get("id") for item in items if isinstance(item.get("id"), int)}

    craftable_ids = load_recipe_result_ids(args.recipes)

    item_text = fetch_text(args.input_dir, "Item.csv")
    gathering_type_text = fetch_text(args.input_dir, "GatheringType.csv")
    gathering_item_text = fetch_text(args.input_dir, "GatheringItem.csv")
    gathering_point_text = fetch_text(args.input_dir, "GatheringPointBase.csv")
    fishing_spot_text = fetch_text(args.input_dir, "FishingSpot.csv")
    gil_shop_text = fetch_text(args.input_dir, "GilShopItem.csv")
    special_shop_text = fetch_text(args.input_dir, "SpecialShop.csv")
    collectables_shop_item_text = fetch_text(args.input_dir, "CollectablesShopItem.csv")
    collectables_shop_reward_text = fetch_text(args.input_dir, "CollectablesShopRewardItem.csv")
    gc_scrip_shop_text = fetch_text(args.input_dir, "GCScripShopItem.csv")

    gather_methods = collect_gather_methods(
        gathering_type_text, gathering_item_text, gathering_point_text
    )
    fishing_ids = parse_item_ids_by_prefix(fishing_spot_text, "Item[")
    gil_shop_ids = parse_item_ids_by_columns(gil_shop_text, ["Item"])
    special_shop_ids = parse_item_ids_by_prefix(special_shop_text, "Item{Receive}")
    collectables_item_ids = parse_item_ids_by_columns(collectables_shop_item_text, ["Item"])
    collectables_reward_ids = parse_item_ids_by_columns(
        collectables_shop_reward_text, ["Item"]
    )
    collectables_ids = collectables_item_ids | collectables_reward_ids
    gc_scrip_ids = parse_item_ids_by_columns(gc_scrip_shop_text, ["Item"])

    item_info = parse_item_info(item_text, item_ids)

    updated = 0
    unchanged = 0
    missing_info = 0

    for item in items:
        item_id = item.get("id")
        if not isinstance(item_id, int):
            missing_info += 1
            continue
        info = item_info.get(item_id)
        if not info:
            missing_info += 1
            continue
        is_untradable, price_low, csv_is_crystal = info
        is_crystal = bool(item.get("isCrystal")) or csv_is_crystal
        new_methods = build_obtain_methods(
            item_id,
            is_crystal,
            is_untradable,
            craftable_ids,
            gather_methods,
            fishing_ids,
            gil_shop_ids,
            special_shop_ids,
            collectables_ids,
            gc_scrip_ids,
        )
        if item_id in gil_shop_ids and price_low > 0:
            item["obtainMethodDetails"] = {"SHOP_GIL": {"priceLow": price_low}}
        else:
            item.pop("obtainMethodDetails", None)
        if item.get("obtainMethods") != new_methods:
            item["obtainMethods"] = new_methods
            updated += 1
        else:
            unchanged += 1

    output_path = items_path if args.in_place else args.output
    if output_path is None:
        output_path = items_path.with_name("items.patched.json")

    output_path.write_text(
        json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("=== Overwrite obtainMethods summary ===")
    print(f"Items total: {len(items)}")
    print(f"Items updated: {updated}")
    print(f"Items unchanged: {unchanged}")
    print(f"Items missing CN Item.csv info: {missing_info}")
    print(f"Output: {output_path}")
    print("Source item counts (unique ids):")
    print(f"- CRAFT (Recipe.csv): {len(craftable_ids)}")
    print(f"- GATHER (Gathering*.csv): {len(gather_methods)}")
    print(f"- FISHING (FishingSpot.csv): {len(fishing_ids)}")
    print(f"- SHOP_GIL (GilShopItem.csv): {len(gil_shop_ids)}")
    print(f"- SHOP_SPECIAL (SpecialShop.csv): {len(special_shop_ids)}")
    print(f"- SHOP_COLLECTABLES (CollectablesShop*.csv): {len(collectables_ids)}")
    print(f"- SHOP_GC (GCScripShopItem.csv): {len(gc_scrip_ids)}")
    print("Basic validation:")
    print(f"- Item count unchanged: {len(items)}")
    print(f"- Updated + unchanged + missing = {updated + unchanged + missing_info}")


if __name__ == "__main__":
    main()
