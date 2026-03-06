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
    "GATHER_FISHER",
    "SHOP_NPC",
    "EXCHANGE_GC_SEALS",
    "EXCHANGE_SCRIP_CRAFTER",
    "EXCHANGE_SCRIP_GATHERER",
    "EXCHANGE_GEMSTONE",
    "EXCHANGE_TOME",
    "SHOP_MARKET",
]

IGNORED_SOURCES = [
    "DisposalShopItem.csv",
    "QuestClassJobReward.csv",
    "LeveRewardItemGroup.csv",
    "Achievement.csv",
    "WeeklyBingoRewardData.csv",
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
    for row in rows[3:]:
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


def parse_item_name_map(text: str) -> Dict[int, str]:
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
        name = row[idx_name].strip()
        if name:
            mapping[key] = name
    return mapping


def parse_tomestone_item_ids(text: str) -> Set[int]:
    rows = list(csv.reader(text.splitlines()))
    header = rows[1]
    idx_item = header.index("Item")
    result: Set[int] = set()
    for row in rows[4:]:
        if len(row) <= idx_item:
            continue
        try:
            item_id = int(row[idx_item])
        except ValueError:
            continue
        if item_id > 0:
            result.add(item_id)
    return result


def parse_special_shop_costs(text: str) -> Dict[int, Set[int]]:
    rows = list(csv.reader(text.splitlines()))
    header = rows[1]
    receive_indices = [idx for idx, name in enumerate(header) if name.startswith("Item{Receive}")]
    cost_indices = [idx for idx, name in enumerate(header) if name.startswith("Item{Cost}")]
    result: Dict[int, Set[int]] = {}
    if not receive_indices or not cost_indices:
        return result
    for row in rows[4:]:
        receive_ids: Set[int] = set()
        cost_ids: Set[int] = set()
        for idx in receive_indices:
            if len(row) <= idx:
                continue
            try:
                item_id = int(row[idx])
            except ValueError:
                continue
            if item_id > 0:
                receive_ids.add(item_id)
        for idx in cost_indices:
            if len(row) <= idx:
                continue
            try:
                item_id = int(row[idx])
            except ValueError:
                continue
            if item_id > 0:
                cost_ids.add(item_id)
        if not receive_ids or not cost_ids:
            continue
        for receive_id in receive_ids:
            result.setdefault(receive_id, set()).update(cost_ids)
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
    craftable_ids: Set[int],
    gather_methods: Dict[int, Set[str]],
    fishing_ids: Set[int],
    gil_shop_ids: Set[int],
    gc_scrip_ids: Set[int],
    special_shop_costs: Dict[int, Set[int]],
    crafting_scrip_ids: Set[int],
    gathering_scrip_ids: Set[int],
    bicolor_gem_id: int | None,
    tomestone_ids: Set[int],
) -> List[str]:
    methods: Set[str] = set()
    if item_id in craftable_ids:
        methods.add("CRAFT")
    if not is_untradable:
        methods.add("SHOP_MARKET")
    methods.update(gather_methods.get(item_id, set()))
    if item_id in fishing_ids:
        methods.add("GATHER_FISHER")
    if item_id in gil_shop_ids:
        methods.add("SHOP_NPC")
    if item_id in gc_scrip_ids:
        methods.add("EXCHANGE_GC_SEALS")
    if item_id in special_shop_costs:
        cost_ids = special_shop_costs.get(item_id, set())
        if cost_ids & crafting_scrip_ids:
            methods.add("EXCHANGE_SCRIP_CRAFTER")
        if cost_ids & gathering_scrip_ids:
            methods.add("EXCHANGE_SCRIP_GATHERER")
        if bicolor_gem_id and bicolor_gem_id in cost_ids:
            methods.add("EXCHANGE_GEMSTONE")
        if cost_ids & tomestone_ids:
            methods.add("EXCHANGE_TOME")
    if is_crystal:
        methods.update({"GATHER_MINER", "GATHER_BOTANIST"})
    return [method for method in OBTAIN_METHOD_ORDER if method in methods]


def parse_items(
    text: str,
    needed_ids: Iterable[int],
    craftable_ids: Set[int],
    gather_methods: Dict[int, Set[str]],
    fishing_ids: Set[int],
    gil_shop_ids: Set[int],
    gc_scrip_ids: Set[int],
    special_shop_costs: Dict[int, Set[int]],
    crafting_scrip_ids: Set[int],
    gathering_scrip_ids: Set[int],
    bicolor_gem_id: int | None,
    tomestone_ids: Set[int],
) -> tuple[List[Dict], Dict[str, int]]:
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
    stats = {
        "rows_total": 0,
        "rows_with_id": 0,
        "rows_needed": 0,
        "rows_with_name": 0,
    }
    for row in rows[4:]:
        stats["rows_total"] += 1
        if len(row) <= idx_key:
            continue
        try:
            item_id = int(row[idx_key])
        except ValueError:
            continue
        stats["rows_with_id"] += 1
        if item_id not in needed_set:
            continue
        stats["rows_needed"] += 1
        name = row[idx_name].strip()
        if not name:
            continue
        stats["rows_with_name"] += 1
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
            craftable_ids,
            gather_methods,
            fishing_ids,
            gil_shop_ids,
            gc_scrip_ids,
            special_shop_costs,
            crafting_scrip_ids,
            gathering_scrip_ids,
            bicolor_gem_id,
            tomestone_ids,
        )
        item_payload = {
            "id": item_id,
            "name": {"en": name, "zh-CN": name, "ja": name},
            "isCrystal": is_crystal,
            "obtainMethods": obtain_methods,
        }
        if item_id in gil_shop_ids and price_low > 0:
            item_payload["obtainMethodDetails"] = {"SHOP_NPC": {"priceLow": price_low}}
        items_by_id[item_id] = item_payload

    items = [items_by_id[item_id] for item_id in needed_ids if item_id in items_by_id]
    stats["items_written"] = len(items)
    return items, stats


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
    fishing_spot_text = fetch_text(args.input_dir, "FishingSpot.csv")
    gil_shop_text = fetch_text(args.input_dir, "GilShopItem.csv")
    special_shop_text = fetch_text(args.input_dir, "SpecialShop.csv")
    gc_scrip_shop_text = fetch_text(args.input_dir, "GCScripShopItem.csv")
    tomestone_item_text = fetch_text(args.input_dir, "TomestonesItem.csv")

    gather_methods = collect_gather_methods(
        gathering_type_text, gathering_item_text, gathering_point_text
    )
    fishing_ids = parse_item_ids_by_prefix(fishing_spot_text, "Item[")
    gil_shop_ids = parse_item_ids_by_columns(gil_shop_text, ["Item"])
    special_shop_costs = parse_special_shop_costs(special_shop_text)
    gc_scrip_ids = parse_item_ids_by_columns(gc_scrip_shop_text, ["Item"])
    item_name_map = parse_item_name_map(item_text)
    # 识别“票据”货币本体（成本物品），而不是成品名字。
    crafting_scrip_ids = {
        item_id for item_id, name in item_name_map.items() if "巧手" in name and "票" in name
    }
    gathering_scrip_ids = {
        item_id for item_id, name in item_name_map.items() if "大地" in name and "票" in name
    }
    bicolor_gem_id = next(
        (item_id for item_id, name in item_name_map.items() if name == "双色宝石"),
        None,
    )
    tomestone_ids = parse_tomestone_item_ids(tomestone_item_text)

    items, stats = parse_items(
        item_text,
        needed_ids,
        craftable_ids,
        gather_methods,
        fishing_ids,
        gil_shop_ids,
        gc_scrip_ids,
        special_shop_costs,
        crafting_scrip_ids,
        gathering_scrip_ids,
        bicolor_gem_id,
        tomestone_ids,
    )

    write_json(args.output_dir / "items.json", items)
    print(f"Item rows total: {stats['rows_total']}")
    print(f"Item rows with valid id: {stats['rows_with_id']}")
    print(f"Item rows matched needed ids: {stats['rows_needed']}")
    print(f"Item rows with name: {stats['rows_with_name']}")
    print(f"Wrote {stats['items_written']} items to {args.output_dir / 'items.json'}")
    print("Obtain method sources (unique item ids):")
    print(f"- 制作 (Recipe.csv): {len(craftable_ids)}")
    print(f"- 采集 (Gathering*.csv): {len(gather_methods)}")
    print(f"- 捕鱼人 (FishingSpot.csv): {len(fishing_ids)}")
    print(f"- NPC 购买 (GilShopItem.csv): {len(gil_shop_ids)}")
    print(f"- 军票兑换 (GCScripShopItem.csv): {len(gc_scrip_ids)}")
    print(f"- 票据/兑换 (SpecialShop.csv): {len(special_shop_costs)}")
    print(f"- 工匠票据 (Item.csv): {len(crafting_scrip_ids)}")
    print(f"- 采集票据 (Item.csv): {len(gathering_scrip_ids)}")
    print(f"- 双色宝石 (Item.csv): {1 if bicolor_gem_id else 0}")
    print(f"- 神典石 (TomestonesItem.csv): {len(tomestone_ids)}")
    print("Ignored sources:")
    for source in IGNORED_SOURCES:
        print(f"- {source}")


if __name__ == "__main__":
    main()
