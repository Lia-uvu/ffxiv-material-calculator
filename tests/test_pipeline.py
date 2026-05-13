from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
PIPELINE_DIR = ROOT_DIR / "scripts" / "pipeline"
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

from lib.items_cn import build_items_base_cn
from lib.items_i18n import build_i18n_name_rows, merge_items_with_i18n
from lib.pipeline_state import extract_needed_item_ids, validate_outputs
from lib.recipe_cn import build_recipes
from run_pipeline import run_pipeline


class PipelineFixtureTest(unittest.TestCase):
    def setUp(self) -> None:
        fixture_root = ROOT_DIR / "tests" / "fixtures" / "pipeline"
        self.cn_dir = fixture_root / "cn"
        self.en_dir = fixture_root / "en"
        self.ja_dir = fixture_root / "ja"
        self.expected_items = json.loads((fixture_root / "expected" / "items.json").read_text(encoding="utf-8"))
        self.expected_recipes = json.loads(
            (fixture_root / "expected" / "recipes.json").read_text(encoding="utf-8")
        )
        self.expected_outfit_meta = json.loads(
            (fixture_root / "expected" / "outfitSetMeta.json").read_text(encoding="utf-8")
        )

    def test_recipe_filter_excludes_item_search_category_zero_except_restored_ishgard_phase_4(self) -> None:
        recipes, needed_ids = build_recipes(self.cn_dir, allow_remote=False)

        self.assertEqual([recipe["resultItemId"] for recipe in recipes], [2210, 4421, 1370, 3240, 9100, 9997])
        self.assertIn(9997, needed_ids)
        self.assertNotIn(9999, needed_ids)

    def test_needed_item_ids_include_results_and_materials(self) -> None:
        recipes, _ = build_recipes(self.cn_dir, allow_remote=False)
        needed_ids = extract_needed_item_ids(recipes)

        self.assertEqual(
            needed_ids,
            [
                1000,
                1001,
                1370,
                1371,
                2210,
                3240,
                3241,
                4421,
                9001,
                9002,
                9003,
                9004,
                9005,
                9006,
                9100,
                9997,
                9998,
            ],
        )

    def test_obtain_methods_rules_cover_special_sources(self) -> None:
        recipes, _ = build_recipes(self.cn_dir, allow_remote=False)
        needed_ids = extract_needed_item_ids(recipes)
        items, _ = build_items_base_cn(self.cn_dir, needed_ids, recipes, allow_remote=False)
        items_by_id = {item["id"]: item for item in items}

        self.assertEqual(items_by_id[9001]["obtainMethods"], ["EXCHANGE_SCRIP_CRAFTER"])
        self.assertEqual(items_by_id[9002]["obtainMethods"], ["EXCHANGE_SCRIP_GATHERER"])
        self.assertEqual(items_by_id[9003]["obtainMethods"], ["EXCHANGE_GEMSTONE"])
        self.assertEqual(items_by_id[9004]["obtainMethods"], ["EXCHANGE_TOME"])
        self.assertEqual(items_by_id[9005]["obtainMethods"], ["EXCHANGE_GC_SEALS"])
        self.assertEqual(items_by_id[9006]["obtainMethods"], ["GATHER_FISHER", "SHOP_MARKET"])
        self.assertEqual(items_by_id[1000]["obtainMethods"], ["GATHER_MINER", "GATHER_BOTANIST", "SHOP_MARKET"])

    def test_merge_falls_back_to_zh_cn_for_missing_names(self) -> None:
        recipes, _ = build_recipes(self.cn_dir, allow_remote=False)
        needed_ids = extract_needed_item_ids(recipes)
        base_items, _ = build_items_base_cn(self.cn_dir, needed_ids, recipes, allow_remote=False)
        i18n_rows = build_i18n_name_rows(self.en_dir, self.ja_dir, needed_ids)
        merged_items = merge_items_with_i18n(base_items, i18n_rows)
        items_by_id = {item["id"]: item for item in merged_items}

        self.assertEqual(items_by_id[9004]["name"]["en"], items_by_id[9004]["name"]["zh-CN"])
        self.assertEqual(items_by_id[9006]["name"]["ja"], items_by_id[9006]["name"]["zh-CN"])

    def test_validation_blocks_missing_items_but_only_warns_on_missing_i18n(self) -> None:
        recipes, _ = build_recipes(self.cn_dir, allow_remote=False)
        needed_ids = extract_needed_item_ids(recipes)
        base_items, _ = build_items_base_cn(self.cn_dir, needed_ids, recipes, allow_remote=False)
        i18n_rows = build_i18n_name_rows(self.en_dir, self.ja_dir, needed_ids)
        merged_items = merge_items_with_i18n(base_items, i18n_rows)

        report = validate_outputs(recipes, merged_items, i18n_rows)
        self.assertTrue(report["passed"])
        self.assertEqual(report["summary"]["missingEnNameCount"], 1)
        self.assertEqual(report["summary"]["missingJaNameCount"], 1)

        broken_report = validate_outputs(recipes, [item for item in merged_items if item["id"] != 9005], i18n_rows)
        self.assertFalse(broken_report["passed"])
        self.assertEqual(broken_report["summary"]["missingRecipeItemRefCount"], 1)

    def test_run_pipeline_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            publish_dir = temp_dir / "publish"
            work_dir = temp_dir / "work"
            state_path = temp_dir / "state" / "last_successful_manifest.json"

            result = run_pipeline(
                current_repo=ROOT_DIR,
                cn_repo=self.cn_dir,
                en_repo=self.en_dir,
                ja_repo=self.ja_dir,
                work_dir=work_dir,
                publish_dir=publish_dir,
                state_path=state_path,
            )

            actual_recipes = json.loads((publish_dir / "recipes.json").read_text(encoding="utf-8"))
            actual_items = json.loads((publish_dir / "items.json").read_text(encoding="utf-8"))
            actual_outfit_meta = json.loads((publish_dir / "outfitSetMeta.json").read_text(encoding="utf-8"))

            self.assertEqual(actual_recipes, self.expected_recipes)
            self.assertEqual(actual_items, self.expected_items)
            self.assertEqual(actual_outfit_meta, self.expected_outfit_meta)
            self.assertEqual(
                sorted(path.name for path in publish_dir.iterdir()),
                ["items.json", "outfitSetMeta.json", "recipes.json"],
            )
            self.assertEqual(result["publishDiff"]["recipes"]["addedCount"], 6)
            self.assertEqual(result["publishDiff"]["items"]["addedCount"], 17)
            self.assertTrue(Path(result["paths"]["outfitMeta"]).exists())
            self.assertTrue(state_path.exists())


if __name__ == "__main__":
    unittest.main()
