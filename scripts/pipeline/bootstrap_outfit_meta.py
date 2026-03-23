#!/usr/bin/env python3
"""One-time bootstrap: download CN CSVs from GitHub and generate outfitSetMeta.json.

After the initial generation, `build_outfit_sets.py` reads from local static files
and no longer needs network access. Future updates to outfitSetMeta.json are handled
by the main pipeline (run_pipeline.py).
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from lib.outfit_meta import build_outfit_meta

BASE_URL_CN = "https://raw.githubusercontent.com/thewakingsands/ffxiv-datamining-cn/master"


def fetch_csv(url: str) -> str:
    print(f"  Downloading {url.split('/')[-1]}...")
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")


def main():
    project_root = Path(__file__).resolve().parent.parent.parent
    data_dir = project_root / "src" / "data"

    print("Loading recipes.json (for secretRecipeBook data)...")
    # We need the full recipes with secretRecipeBook. Since the published
    # recipes.json may not have it, we rebuild from the CN CSV.
    from lib.recipe_cn import build_recipes  # noqa: E402

    print("Downloading CN CSVs from GitHub...")
    item_text = fetch_csv(f"{BASE_URL_CN}/Item.csv")
    cjc_text = fetch_csv(f"{BASE_URL_CN}/ClassJobCategory.csv")

    # Download recipe CSVs and build full recipes (with secretRecipeBook)
    recipe_text = fetch_csv(f"{BASE_URL_CN}/Recipe.csv")
    level_text = fetch_csv(f"{BASE_URL_CN}/RecipeLevelTable.csv")

    # Write temp CSVs for recipe building (it expects local files)
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / "Recipe.csv").write_text(recipe_text, encoding="utf-8")
        (tmpdir / "RecipeLevelTable.csv").write_text(level_text, encoding="utf-8")
        (tmpdir / "Item.csv").write_text(item_text, encoding="utf-8")
        recipes, _ = build_recipes(tmpdir, allow_remote=False)

    print(f"  {len(recipes)} recipes loaded")

    print("Building outfit set metadata...")
    meta = build_outfit_meta(recipes, item_text, cjc_text)

    output_path = data_dir / "outfitSetMeta.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"Written metadata to {output_path}")
    print(f"  {len(meta['masterRecipeItemIds'])} master recipe items")
    print(f"  {len(meta['items'])} equippable items")
    print(f"  {len(meta['cjcJobs'])} ClassJobCategory entries")


if __name__ == "__main__":
    main()
