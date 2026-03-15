from __future__ import annotations

import csv
from pathlib import Path

from .io_utils import read_text_from_dir


def extract_item_names(item_text: str, needed_ids: list[int]) -> dict[int, str]:
    needed_set = set(needed_ids)
    rows = list(csv.reader(item_text.splitlines()))
    header = rows[1]
    idx_key = header.index("#")
    idx_name = header.index("Name")
    result: dict[int, str] = {}
    for row in rows[4:]:
        if len(row) <= max(idx_key, idx_name):
            continue
        try:
            item_id = int(row[idx_key])
        except ValueError:
            continue
        if item_id not in needed_set:
            continue
        name = row[idx_name].strip()
        if name:
            result[item_id] = name
    return result


def build_i18n_name_rows(en_dir: Path, ja_dir: Path, needed_ids: list[int]) -> list[dict]:
    en_names = extract_item_names(read_text_from_dir(en_dir, "Item.csv"), needed_ids)
    ja_names = extract_item_names(read_text_from_dir(ja_dir, "Item.csv"), needed_ids)

    rows = []
    for item_id in needed_ids:
        payload = {"id": item_id}
        if item_id in en_names:
            payload["en"] = en_names[item_id]
        if item_id in ja_names:
            payload["ja"] = ja_names[item_id]
        rows.append(payload)
    return rows


def merge_items_with_i18n(base_items: list[dict], i18n_name_rows: list[dict]) -> list[dict]:
    names_by_id = {row["id"]: row for row in i18n_name_rows}
    merged_items = []
    for item in base_items:
        zh_name = item.get("name", {}).get("zh-CN")
        name_patch = names_by_id.get(item["id"], {})
        merged_item = dict(item)
        merged_item["name"] = {
            "zh-CN": zh_name,
            "en": name_patch.get("en") or zh_name,
            "ja": name_patch.get("ja") or zh_name,
        }
        merged_items.append(merged_item)
    return merged_items
