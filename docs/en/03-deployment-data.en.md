# Static Data & Deployment (v2.0)
This document describes the local CSV data pipeline, runtime data layout, and automated publishing flow used by the FFXIV Material Calculator.

Architecture: [`01-architecture-dataflow.en.md`](01-architecture-dataflow.en.md)  
Data contracts: [`02-contracts.en.md`](02-contracts.en.md)

## Data Sources
### CN recipes and base item data
- Upstream repository: configured via GitHub Actions repository variables
- Files used: `Recipe.csv`, `RecipeLevelTable.csv`, `Item.csv`, plus obtain-method CSVs
- Purpose:
  - `Recipe.csv` builds the full `recipes` payload
  - `Item.csv` + obtain-method CSVs build CN base `items`
- Current integration path:
  - `FFXIV_DATAMINING_CN_REPO=thewakingsands/ffxiv-datamining-cn`

### EN / JA item names
- Upstream repositories: configured via GitHub Actions repository variables
- Files used: each upstream repo's `Item.csv`
- Purpose: extract names for the same `needed_item_ids`
- Current integration paths:
  - `FFXIV_DATAMINING_EN_REPO=InfSein/ffxiv-datamining-mixed`, reading `en/Item.csv`
  - `FFXIV_DATAMINING_JA_REPO=a1hena/ffxiv-datamining-jp`, reading `csv/Item.csv`

### Legacy tooling
- `scripts/xivapi/` still exists as a manual historical toolset.
- It is no longer part of the main pipeline or CI, and now requires explicit `--ids` / `--items` arguments instead of writing into `src/data/` by default.

## Pipeline Steps
Single entrypoint: `scripts/pipeline/run_pipeline.py`

Step scripts:
1. `01_build_recipes.py`: build `01_recipes.full.json` from CN CSVs
2. `02_extract_needed_item_ids.py`: extract sorted `needed_item_ids` from recipes
3. `03_build_items_cn.py`: build `03_items.base.cn.json` from CN `Item.csv` and obtain-method CSVs
4. `04_build_items_i18n_name.py`: extract EN / JA names into `04_items.i18n_name.json`
5. `05_merge_items.py`: merge CN base items with EN / JA names, falling back to `zh-CN`
6. `06_validate_publish.py`: validate recipe/item cross references and report missing translations
7. `07_publish.py`: publish the final runtime JSON files when validation passes

## Intermediate Artifact Contract
The default pipeline work directory is `tmp/pipeline/`. These files are not committed; they are uploaded as CI artifacts:

- `00_manifest.json`
- `01_recipes.full.json`
- `02_needed_item_ids.json`
- `03_items.base.cn.json`
- `04_items.i18n_name.json`
- `05_items.merged.json`
- `06_validation_report.json`
- `07_publish_diff.json`

A small state file is committed back to the repo:
- `scripts/pipeline/state/last_successful_manifest.json`
- Purpose: record the upstream SHAs from the last successful publish so CI can skip unchanged runs

## Runtime Data Directory
The frontend runtime directory `src/data/` now contains only:

- `items.json`
- `recipes.json`
- `index.js`

Minimal sample data moved to `tests/fixtures/pipeline/` and no longer lives under the runtime directory.

## Runtime Data Shapes
### Item example
```jsonc
{
  "id": 4421,
  "name": {
    "zh-CN": "兽骨戒指",
    "en": "Bone Ring",
    "ja": "ボーンリング"
  },
  "isCrystal": false,
  "obtainMethods": [
    "CRAFT",
    "SHOP_MARKET"
  ],
  "obtainMethodDetails": {
    "SHOP_NPC": {
      "priceLow": 9
    }
  }
}
```

### `items.obtainMethods` values
| Value | Meaning | Source |
| --- | --- | --- |
| `CRAFT` | Crafted by players | `Recipe.csv` |
| `GATHER_MINER` | Miner gathering | `GatheringType.csv` + `GatheringItem.csv` + `GatheringPointBase.csv` |
| `GATHER_BOTANIST` | Botanist gathering | Same as above |
| `GATHER_FISHER` | Fishing | `FishingSpot.csv` |
| `SHOP_NPC` | Gil shop | `GilShopItem.csv` |
| `EXCHANGE_GC_SEALS` | GC seals exchange | `GCScripShopItem.csv` |
| `EXCHANGE_SCRIP_CRAFTER` | Crafting scrip exchange | `SpecialShop.csv`, identified by shop name |
| `EXCHANGE_SCRIP_GATHERER` | Gathering scrip exchange | `SpecialShop.csv`, identified by shop name |
| `EXCHANGE_GEMSTONE` | Bicolor gemstone exchange | `SpecialShop.csv` + `Item.csv`, identified by cost item name |
| `EXCHANGE_TOME` | Tomestone exchange | `SpecialShop.csv`, identified by shop name |
| `SHOP_MARKET` | Market board | `Item.csv:IsUntradable` |

### Recipe example
```jsonc
{
  "id": 2000,
  "resultItemId": 4421,
  "resultAmount": 1,
  "job": "GOLDSMITH",
  "itemLevel": 9,
  "patch": "1.23",
  "materials": [
    { "itemId": 1370, "amount": 1 },
    { "itemId": 2210, "amount": 1 }
  ]
}
```

## CI / Publishing
Workflow: `.github/workflows/update-data-pipeline.yml`

Triggers:
- `schedule`: once per day
- `workflow_dispatch`: manual runs with optional `force_run`
- “Upstream update detection”: compare the last successful upstream SHAs with the current remote HEAD SHAs inside the workflow

Workflow outline:
1. Checkout the current repo
2. Resolve the current CN / EN / JA upstream HEAD SHAs
3. Exit early when all SHAs are unchanged and `force_run` is false
4. Checkout the three upstream CSV repositories
5. Run Python pipeline tests
6. Run `scripts/pipeline/run_pipeline.py`
7. Upload the full `tmp/pipeline/` directory as an artifact
8. Run `npm run build`
9. If runtime outputs changed, commit `src/data/items.json`, `src/data/recipes.json`, and the state manifest in one atomic commit

Blocking failures:
- Recipe generation failure
- Empty `needed_item_ids`
- CN item generation failure
- Missing or unreadable EN / JA `Item.csv`
- Recipes referencing items missing from merged items

Non-blocking warnings:
- Missing EN / JA names only produce warnings in `06_validation_report.json`; merged output falls back to `zh-CN`

## Validation Coverage
- `tests/test_pipeline.py` uses the local CSV fixture set in `tests/fixtures/pipeline/`
- Coverage includes:
  - result-item filtering via `ItemSearchCategory == 0`
  - `needed_item_ids` containing both recipe outputs and materials
  - obtain-method regression checks for scrips, gemstones, tomestones, GC seals, fishing, and crystals
  - EN / JA fallback to `zh-CN`
  - blocking validation for missing recipe item references
  - full smoke test of the end-to-end local CSV rebuild path
