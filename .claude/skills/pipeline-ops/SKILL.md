---
name: pipeline-ops
description: Use this skill when the user asks about running, debugging, or modifying the data pipeline for this project. Trigger phrases include "run pipeline", "update data", "pipeline steps", "build outfit sets", "pipeline failed", "force run", "pipeline operations", "流水线", "pipeline 怎么运行", "数据更新", "pipeline 报错".
version: 1.1.0
---

# FFXIV Material Calculator — Pipeline Operations Guide

## Overview

The data pipeline transforms raw FFXIV datamining CSVs (CN/EN/JA) into three runtime JSON files committed to `src/data/`:
- `items.json` — All items with names (zh-CN/en/ja), obtain methods, and metadata
- `recipes.json` — All craftable recipes with materials
- `outfitSetMeta.json` — Equipment slot/ilvl metadata (for outfit set detection)

A post-pipeline step (`build_outfit_sets.py`) consumes those files to produce:
- `src/data/outfitSets.json`
- `src/i18n/generated/outfitSetNames.json`

CI runs the main pipeline daily, then runs `build_outfit_sets.py`, and auto-commits all changed files.

---

## Running the Main Pipeline Locally

### Prerequisites

Three local clones of the datamining repos are required. Upstream repo identifiers (check `scripts/pipeline/state/last_successful_manifest.json` for current paths):

```bash
# CN: thewakingsands/ffxiv-datamining-cn  (flat CSV directory)
# EN: thewakingsands/ffxiv-datamining-mixed (CSV under en/ subdirectory)
# JA: thewakingsands/ffxiv-datamining  (CSV under csv/ subdirectory)
git clone https://github.com/thewakingsands/ffxiv-datamining-cn    upstream/cn
git clone https://github.com/thewakingsands/ffxiv-datamining-mixed  upstream/en
git clone https://github.com/thewakingsands/ffxiv-datamining        upstream/ja
```

### Full Pipeline

```bash
python scripts/pipeline/run_pipeline.py \
  --cn-repo upstream/cn \
  --en-repo upstream/en \
  --ja-repo upstream/ja \
  --work-dir tmp/pipeline \
  --publish-dir src/data \
  --state-path scripts/pipeline/state/last_successful_manifest.json
```

Artifacts are written to `tmp/pipeline/` (debug) and final output to `src/data/`.
Use `python3` instead of `python` if the local shell does not provide a `python` alias.

### Run Individual Steps

Each step can run standalone; inputs must already exist from previous steps.

```bash
# Step 1: build recipes
python scripts/pipeline/01_build_recipes.py \
  --input-dir upstream/cn \
  --output tmp/pipeline/01_recipes.full.json

# Step 2: extract needed item IDs
python scripts/pipeline/02_extract_needed_item_ids.py \
  --recipes tmp/pipeline/01_recipes.full.json \
  --output tmp/pipeline/02_needed_item_ids.json

# Step 3: build CN base items (with obtain methods)
python scripts/pipeline/03_build_items_cn.py \
  --input-dir upstream/cn \
  --needed-ids tmp/pipeline/02_needed_item_ids.json \
  --recipes tmp/pipeline/01_recipes.full.json \
  --output tmp/pipeline/03_items.base.cn.json

# Step 4: extract EN/JA names
python scripts/pipeline/04_build_items_i18n_name.py \
  --en-dir upstream/en \
  --ja-dir upstream/ja \
  --needed-ids tmp/pipeline/02_needed_item_ids.json \
  --output tmp/pipeline/04_items.i18n_name.json

# Step 5: merge items + i18n
python scripts/pipeline/05_merge_items.py \
  --base-items tmp/pipeline/03_items.base.cn.json \
  --i18n-names tmp/pipeline/04_items.i18n_name.json \
  --output tmp/pipeline/05_items.merged.json

# Step 6: validate (exits with code 1 if failed)
python scripts/pipeline/06_validate_publish.py \
  --recipes tmp/pipeline/01_recipes.full.json \
  --items tmp/pipeline/05_items.merged.json \
  --i18n-names tmp/pipeline/04_items.i18n_name.json \
  --output tmp/pipeline/06_validation_report.json

# Step 7: publish to src/data/
python scripts/pipeline/07_publish.py \
  --recipes tmp/pipeline/01_recipes.full.json \
  --items tmp/pipeline/05_items.merged.json \
  --validation tmp/pipeline/06_validation_report.json \
  --publish-dir src/data \
  --diff-output tmp/pipeline/07_publish_diff.json \
  --state-path scripts/pipeline/state/last_successful_manifest.json
```

---

## Post-Pipeline: Generate Outfit Sets

After `src/data/` is updated, run this to regenerate `outfitSets.json` and `outfitSetNames.json`:

```bash
python scripts/pipeline/build_outfit_sets.py
```

Reads from `src/data/{items.json,recipes.json,outfitSetMeta.json}`. Writes to `src/data/outfitSets.json` and `src/i18n/generated/outfitSetNames.json`.

**Outfit set detection criteria:**
- Item must have a master recipe (`secretRecipeBook > 0`)
- Crafter level ≥ 70 and ilvl ≥ 2
- Gear group requires ≥ 3 of 5 armor slots (head/body/hands/legs/feet)

---

## Running Pipeline Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Tests use fixture CSVs in `tests/fixtures/pipeline/` (CN/EN/JA subdirs). Expected outputs are in `tests/fixtures/pipeline/expected/`.
Use `python3` instead of `python` if needed locally.

---

## GitHub Actions: Automatic CI

**File:** `.github/workflows/update-data-pipeline.yml`

**Schedule:** Daily at 1:00 AM UTC. Also supports manual `workflow_dispatch`.

### How Skip Detection Works

CI compares the current upstream git SHAs and the current repository SHA against `scripts/pipeline/state/last_successful_manifest.json`. The pipeline is skipped only when:

- all three upstream repos (CN/EN/JA) are unchanged
- the current repository SHA matches the last successful publish
- `force_run` is false

To force a run regardless:
- Go to Actions → "Update Data Pipeline" → "Run workflow"
- Check the `force_run` checkbox

### What CI Commits (when data changes)

```
chore(data): update published pipeline data
```

Files committed:
- `src/data/items.json`
- `src/data/recipes.json`
- `src/data/outfitSetMeta.json`
- `src/data/outfitSets.json`
- `src/i18n/generated/outfitSetNames.json`
- `scripts/pipeline/state/last_successful_manifest.json`

---

## State Manifest

`scripts/pipeline/state/last_successful_manifest.json` tracks the upstream SHAs and the repository SHA from the last successful run:

```json
{
  "publishedAt": "2026-03-31T12:00:00Z",
  "currentRepoSha": "abc123...",
  "upstream": {
    "cn": {"path": "...", "sha": "def456..."},
    "en": {"path": "...", "sha": "ghi789..."},
    "ja": {"path": "...", "sha": "jkl012..."}
  },
  "scriptVersion": "1.0"
}
```

This file is committed to the repo. CI uses it to detect whether the pipeline inputs are unchanged on subsequent runs.

---

## Troubleshooting

### Pipeline skipped when it shouldn't run
Check `last_successful_manifest.json`:

- if upstream SHAs match, confirm whether the current repo SHA also matches
- if pipeline code changed but the workflow still skipped, use `force_run: true`
- do not update the manifest manually unless you intentionally want to override CI's change detection

### Step 6 validation fails: "recipes reference missing items"
A recipe material or result item ID is not in `items.json`. Likely cause: upstream CSV data has a new item not yet parsed. Check `06_validation_report.json` → `errors.missingRecipeItemRefs`.

### Missing EN/JA names (warnings, not errors)
Step 6 emits warnings (not failures) for items with no EN or JA translation. Check `06_validation_report.json` → `warnings.missingI18nNames`.

### `needed_item_ids is empty`
Step 1 produced no recipes. Check Recipe.csv format — the parser filters rows where `ItemSearchCategory == 0`.

### EN repo CSV path
The EN repo (`ffxiv-datamining-mixed`) stores CSVs under `en/` subdirectory. Pass the repo root, not the `en/` dir — `04_build_items_i18n_name.py` appends the path internally.

### JA repo CSV path
The JA repo (`ffxiv-datamining`) stores CSVs under `csv/` subdirectory. Same as above — pass repo root.

---

## Data Flow Summary

```
upstream/cn (CSVs)          upstream/en         upstream/ja
      │                          │                    │
      ├── Step 1: recipes ──────►│                    │
      ├── Step 2: needed IDs     │                    │
      ├── Step 3: CN items ──────┤                    │
      │                    Step 4: i18n names ◄───────┘
      │                          │
      │                    Step 5: merge
      │                          │
      │                    Step 6: validate
      │                          │
      └──────────────────► Step 7: publish ──► src/data/{items,recipes,outfitSetMeta}.json
                                                       │
                                              build_outfit_sets.py (CI + local)
                                                       │
                                         src/data/outfitSets.json
                                         src/i18n/generated/outfitSetNames.json
                                                       │
                                              CI: git add + commit all generated data files + state manifest
```

---

## Obtain Method Reference

Items can have multiple obtain methods. Step 3 detects these from CN CSVs:

| Method | Source CSV |
|--------|-----------|
| `CRAFT` | Recipe.csv |
| `GATHER_MINER` / `GATHER_BOTANIST` | GatheringPointBase + GatheringItem + GatheringType |
| `GATHER_FISHER` | FishingSpot.csv |
| `SHOP_NPC` | GilShopItem.csv |
| `SHOP_MARKET` | All tradeable items (Item.csv `IsUntradable == 0`) |
| `EXCHANGE_GC_SEALS` | GCScripShopItem.csv |
| `EXCHANGE_SCRIP_CRAFTER` / `EXCHANGE_SCRIP_GATHERER` | SpecialShop.csv (currency item detection) |
| `EXCHANGE_TOME` | SpecialShop.csv (tomestone currencies) |
| `EXCHANGE_GEMSTONE` | SpecialShop.csv (bicolor gemstone) |
