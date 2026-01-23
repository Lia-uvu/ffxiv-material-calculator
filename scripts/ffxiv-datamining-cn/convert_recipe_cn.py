# convert_recipe_cn.py
# Usage (run from anywhere):
# python convert_recipe_cn.py --src "C:\Users\Coccyx\ffxiv-datamining-cn" --out "D:\...\recipes.ndjson" --patch "7.4"

import argparse
import csv
import json
import re
from pathlib import Path


CRAFTTYPE_TO_JOB = {
    0: "CARPENTER",     # CRP
    1: "BLACKSMITH",    # BSM
    2: "ARMORER",       # ARM
    3: "GOLDSMITH",     # GSM
    4: "LEATHERWORKER", # LTW
    5: "WEAVER",        # WVR
    6: "ALCHEMIST",     # ALC
    7: "CULINARIAN",    # CUL
}


def to_int(v, default=0) -> int:
    try:
        if v is None:
            return default
        s = str(v).strip()
        if s == "" or s.lower() == "null":
            return default
        return int(float(s))
    except Exception:
        return default


def read_dumpcsv_rows(path: Path):
    """
    FFCAFE dumpcsv format:
      line1: key,0,1,2...
      line2: real field names
      line3: types
      line4: defaults
      line5+: data rows
    Returns: (fields, list[dict])
    """
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        _header_idx = next(r, None)
        fields = next(r, None)
        _types = next(r, None)
        _defaults = next(r, None)

        if not fields:
            raise ValueError(f"{path} header missing")

        fields = [h.strip().replace("\ufeff", "") for h in fields]

        rows = []
        for row in r:
            if not row:
                continue
            if len(row) < len(fields):
                row = row + [""] * (len(fields) - len(row))
            rows.append(dict(zip(fields, row)))
    return fields, rows


def pick_first(fields, candidates):
    for c in candidates:
        if c in fields:
            return c
    return None


def main():
    parser = argparse.ArgumentParser(description="Convert ffxiv-datamining-cn Recipe.csv -> NDJSON")
    parser.add_argument("--src", default=".", help="Path to ffxiv-datamining-cn repo (contains Recipe.csv, Item.csv)")
    parser.add_argument("--out", required=True, help="Output NDJSON path, e.g. D:\\...\\recipes.ndjson")
    parser.add_argument("--patch", default="", help='Patch string to write for all recipes, e.g. "7.4" or "1.23"')
    parser.add_argument("--encoding", default="utf-8", help="Output encoding (default utf-8)")
    args = parser.parse_args()

    src = Path(args.src)
    recipe_csv = src / "Recipe.csv"
    item_csv = src / "Item.csv"

    if not recipe_csv.exists():
        raise SystemExit(f"Recipe.csv not found: {recipe_csv}")
    if not item_csv.exists():
        raise SystemExit(f"Item.csv not found: {item_csv}")

    # --- Read recipes ---
    recipe_fields, recipe_rows = read_dumpcsv_rows(recipe_csv)

    recipe_id_col = pick_first(recipe_fields, ["#", "Number", "key"])
    craft_type_col = pick_first(recipe_fields, ["CraftType"])
    rlt_col = pick_first(recipe_fields, ["RecipeLevelTable"])  # not used now, kept for future
    result_item_col = pick_first(recipe_fields, ["Item{Result}"])
    result_amount_col = pick_first(recipe_fields, ["Amount{Result}"])

    if not result_item_col:
        raise SystemExit("Cannot find Item{Result} column in Recipe.csv")
    if not result_amount_col:
        raise SystemExit("Cannot find Amount{Result} column in Recipe.csv")

    # Ingredient slots: Item{Ingredient}[0..] / Amount{Ingredient}[0..]
    item_slots = []
    amt_slots = {}

    for name in recipe_fields:
        m = re.fullmatch(r"Item\{Ingredient\}\[(\d+)\]", name)
        if m:
            item_slots.append((int(m.group(1)), name))
        m = re.fullmatch(r"Amount\{Ingredient\}\[(\d+)\]", name)
        if m:
            amt_slots[int(m.group(1))] = name

    item_slots.sort()

    base_recipes = []
    result_item_ids = set()

    for d in recipe_rows:
        rid = to_int(d.get(recipe_id_col)) if recipe_id_col else None
        result_item_id = to_int(d.get(result_item_col))
        if result_item_id <= 0:
            continue

        result_amount = to_int(d.get(result_amount_col), 1)

        craft_type = to_int(d.get(craft_type_col), -1) if craft_type_col else -1
        job = CRAFTTYPE_TO_JOB.get(craft_type, "UNKNOWN")

        mats = []
        for idx, item_col in item_slots:
            item_id = to_int(d.get(item_col))
            if item_id <= 0:
                continue
            amt_col = amt_slots.get(idx)
            amt = to_int(d.get(amt_col), 1) if amt_col else 1
            mats.append({"itemId": item_id, "amount": max(1, amt)})

        base_recipes.append(
            {
                "id": rid,
                "resultItemId": result_item_id,
                "resultAmount": result_amount,
                "job": job,
                "materials": mats,
            }
        )
        result_item_ids.add(result_item_id)

    # --- Read item levels for result items ---
    item_fields, item_rows = read_dumpcsv_rows(item_csv)

    item_id_col = pick_first(item_fields, ["#", "key", "ID", "Id"])
    # Common item level columns in dumps (try a few)
    item_level_col = pick_first(item_fields, ["Level{Item}", "LevelItem", "ItemLevel", "Level"])

    if not item_id_col:
        raise SystemExit("Cannot find item id column in Item.csv (expected '#', 'key', 'ID'...)")

    item_level_map = {}
    if item_level_col:
        for d in item_rows:
            iid = to_int(d.get(item_id_col))
            if iid in result_item_ids:
                item_level_map[iid] = to_int(d.get(item_level_col), 0)
    else:
        # fallback: no column found
        for iid in result_item_ids:
            item_level_map[iid] = 0

    # --- Write NDJSON ---
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    patch_str = args.patch

    written = 0
    with out_path.open("w", encoding=args.encoding, newline="\n") as f:
        for r in base_recipes:
            r["itemLevel"] = item_level_map.get(r["resultItemId"], 0)
            r["patch"] = patch_str
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            written += 1

    print(f"recipes written: {written}")
    print(f"output: {out_path}")


if __name__ == "__main__":
    main()
