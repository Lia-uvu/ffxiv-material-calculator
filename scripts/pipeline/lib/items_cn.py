from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Set

from .io_utils import read_text_from_dir_or_remote

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

CRAFTER_SCRIP_CRYSTAL_IDS = {2, 6}
GATHERER_SCRIP_CRYSTAL_IDS = {4, 7}


def load_item_inputs(input_dir: Path | None, *, allow_remote: bool) -> dict[str, str]:
    base_url = BASE_URL if allow_remote else None
    filenames = [
        "Item.csv",
        "GatheringType.csv",
        "GatheringItem.csv",
        "GatheringPointBase.csv",
        "FishingSpot.csv",
        "GilShopItem.csv",
        "SpecialShop.csv",
        "GCScripShopItem.csv",
    ]
    return {
        filename: read_text_from_dir_or_remote(input_dir, filename, base_url)
        for filename in filenames
    }


def load_recipe_result_ids(recipes: Iterable[dict]) -> Set[int]:
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
        mapping[key] = row[idx_name]
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


def parse_special_shop_currency_items(text: str) -> tuple[Set[int], Set[int], Set[int]]:
    rows = list(csv.reader(text.splitlines()))
    header = rows[1]
    name_idx = header.index("Name")
    receive_indices = [i for i, name in enumerate(header) if name.startswith("Item{Receive}")]
    cost_indices = [i for i, name in enumerate(header) if name.startswith("Item{Cost}")]

    crafter_items: Set[int] = set()
    gatherer_items: Set[int] = set()
    tomestone_items: Set[int] = set()

    for row in rows[4:]:
        if len(row) <= name_idx:
            continue
        shop_name = row[name_idx]
        is_crafter_white = "巧手白票" in shop_name
        is_gatherer_white = "大地白票" in shop_name
        is_purple_or_orange = "紫票交易" in shop_name or "橙票交易" in shop_name
        is_tomestone = "神典石" in shop_name

        if not (is_crafter_white or is_gatherer_white or is_purple_or_orange or is_tomestone):
            continue

        received: Set[int] = set()
        for idx in receive_indices:
            if len(row) <= idx:
                continue
            try:
                item_id = int(row[idx])
            except ValueError:
                continue
            if item_id > 0:
                received.add(item_id)

        if not received:
            continue

        if is_tomestone:
            tomestone_items.update(received)
            continue
        if is_crafter_white:
            crafter_items.update(received)
            continue
        if is_gatherer_white:
            gatherer_items.update(received)
            continue

        cost_crystals: Set[int] = set()
        for idx in cost_indices:
            if len(row) <= idx:
                continue
            try:
                cost_id = int(row[idx])
            except ValueError:
                continue
            if cost_id > 0:
                cost_crystals.add(cost_id)
        if cost_crystals & CRAFTER_SCRIP_CRYSTAL_IDS:
            crafter_items.update(received)
        elif cost_crystals & GATHERER_SCRIP_CRYSTAL_IDS:
            gatherer_items.update(received)

    return crafter_items, gatherer_items, tomestone_items


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
    crafter_scrip_items: Set[int],
    gatherer_scrip_items: Set[int],
    bicolor_gem_id: int | None,
    tomestone_items: Set[int],
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
    if item_id in crafter_scrip_items:
        methods.add("EXCHANGE_SCRIP_CRAFTER")
    if item_id in gatherer_scrip_items:
        methods.add("EXCHANGE_SCRIP_GATHERER")
    if item_id in tomestone_items:
        methods.add("EXCHANGE_TOME")
    if item_id in special_shop_costs:
        cost_ids = special_shop_costs.get(item_id, set())
        if bicolor_gem_id and bicolor_gem_id in cost_ids:
            methods.add("EXCHANGE_GEMSTONE")
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
    crafter_scrip_items: Set[int],
    gatherer_scrip_items: Set[int],
    bicolor_gem_id: int | None,
    tomestone_items: Set[int],
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
            crafter_scrip_items,
            gatherer_scrip_items,
            bicolor_gem_id,
            tomestone_items,
        )
        item_payload = {
            "id": item_id,
            "name": {"zh-CN": name},
            "isCrystal": is_crystal,
            "obtainMethods": obtain_methods,
        }
        if item_id in gil_shop_ids and price_low > 0:
            item_payload["obtainMethodDetails"] = {"SHOP_NPC": {"priceLow": price_low}}
        items_by_id[item_id] = item_payload

    items = [items_by_id[item_id] for item_id in needed_ids if item_id in items_by_id]
    stats["items_written"] = len(items)
    return items, stats


def build_items_base_cn(
    input_dir: Path | None,
    needed_ids: list[int],
    recipes: list[dict],
    *,
    allow_remote: bool,
) -> tuple[list[dict], dict[str, int | list[str]]]:
    inputs = load_item_inputs(input_dir, allow_remote=allow_remote)
    craftable_ids = load_recipe_result_ids(recipes)
    gather_methods = collect_gather_methods(
        inputs["GatheringType.csv"],
        inputs["GatheringItem.csv"],
        inputs["GatheringPointBase.csv"],
    )
    fishing_ids = parse_item_ids_by_prefix(inputs["FishingSpot.csv"], "Item[")
    gil_shop_ids = parse_item_ids_by_columns(inputs["GilShopItem.csv"], ["Item"])
    special_shop_costs = parse_special_shop_costs(inputs["SpecialShop.csv"])
    gc_scrip_ids = parse_item_ids_by_columns(inputs["GCScripShopItem.csv"], ["Item"])
    item_name_map = parse_item_name_map(inputs["Item.csv"])
    crafter_scrip_items, gatherer_scrip_items, tomestone_items = parse_special_shop_currency_items(
        inputs["SpecialShop.csv"]
    )
    all_cost_ids: Set[int] = set()
    for cost_set in special_shop_costs.values():
        all_cost_ids.update(cost_set)
    bicolor_gem_id = next(
        (item_id for item_id in all_cost_ids if item_name_map.get(item_id) == "双色宝石"),
        None,
    )

    items, stats = parse_items(
        inputs["Item.csv"],
        needed_ids,
        craftable_ids,
        gather_methods,
        fishing_ids,
        gil_shop_ids,
        gc_scrip_ids,
        special_shop_costs,
        crafter_scrip_items,
        gatherer_scrip_items,
        bicolor_gem_id,
        tomestone_items,
    )
    stats["ignored_sources"] = IGNORED_SOURCES
    return items, stats
