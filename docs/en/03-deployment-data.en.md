# Static Data & Deployment (v1.0)
This document describes the static data model, the update workflow, and deployment details for the FFXIV Material Calculator.

Architecture: [`01-architecture-dataflow.en.md`](01-architecture-dataflow.en.md)  
Data contracts: [`02-contracts.en.md`](02-contracts.en.md)

## Data Sources
### CN item names & recipes
Repository:
https://github.com/thewakingsands/ffxiv-datamining-cn

Workflow: grab CSV files from that repo, then run the Python scripts in `scripts/ffxiv-datamining-cn/` to normalize them into the formats used by this project.

### EN/JA item names: XIVAPI v2
Base URL:
https://v2.xivapi.com
Common v2 endpoints:
https://v2.xivapi.com/api/…
Example (from v2 docs):
https://v2.xivapi.com/api/sheet/Item/37362?fields=Name,Description

Usage: call the API with the ID list in `src/data/needed_item_ids.json` and fetch EN/JA item names.

#### XIVAPI fetching workflow (scripts)
Scripts live in `scripts/xivapi/`.

1. **Fetch incremental NDJSON (resume supported)**:
   ```bash
   node scripts/xivapi/fetchNames.js
   ```
   - Reads `src/data/needed_item_ids.json` by default.
   - Appends successful results to `src/data/nameMap.incremental.ndjson` (intermediate).
   - Writes checkpoints to `scripts/xivapi/cache/nameFetch.checkpoint.ndjson`.
   - Failed ids are stored in `scripts/xivapi/cache/failed-ids.ndjson`.
   - Logs are written to `scripts/logs/YYYY-MM-DD.log`.

2. **Merge into local items.json**:
   ```bash
   node scripts/xivapi/mergeIntoLocalJson.js
   ```
   - Reads `src/data/nameMap.incremental.ndjson` and merges into `src/data/items.json`.
   - Only fills `item.name.en/ja` when empty or equal to the zh-CN placeholder.
   - Writes merge statistics to `scripts/logs/YYYY-MM-DD.log`.

#### Server-friendly strategy
XIVAPI is a public service, so keep the load light:
- **Throttling**: default rps=3 and concurrency=6 for a gentle QPS (configurable).
- **Minimal fields**: only request `Name` to keep payloads small.
- **Retry-friendly**: 429 uses exponential backoff + jitter; failures are logged for selective retries.
- **Two-stage processing**: fetch NDJSON first, then merge into items.json to avoid duplicate API calls.

Optional parameters example:
```bash
node scripts/xivapi/fetchNames.js \
  --ids src/data/needed_item_ids.json \
  --rps 2 \
  --concurrency 4
```

Retry failed IDs:
```bash
node scripts/xivapi/fetchNames.js \
  --retry-failed scripts/xivapi/cache/failed-ids.ndjson
```

Clear incremental file after merging (optional):
```bash
node scripts/xivapi/mergeIntoLocalJson.js --clear-incremental
```

## Static Data Structures

The internal data model is split into two entities:

- `Item`: item metadata
- `Recipe`: crafting recipe information

### Item example
```jsonc
{
  "id": 4421,
  "name": {
    "zh-CN": "兽骨戒指",
    "ja": "ボーンリング",
    "en": "Bone Ring"
  },
  "isCrystal": false,
  "obtainMethods": [
    "制作",
    "市场购买",
    "采矿工",
    "园艺工",
    "NPC 购买"
  ],
  "obtainMethodDetails": {
    "NPC 购买": {
      "priceLow": 9
    }
  }
}
```

### `items.obtainMethods` values
`obtainMethods` is a **string array**. Each entry is a display label and can be combined freely.

| Value | Meaning | CSV source |
| --- | --- | --- |
| `制作` | Crafted by players | `Recipe.csv`: `Item{Result}` |
| `采矿工` | Miner gathering | `GatheringType.csv` + `GatheringItem.csv` + `GatheringPointBase.csv` |
| `园艺工` | Botanist gathering | Same as above (gather type name is 采伐/割草) |
| `捕鱼人` | Fishing | `FishingSpot.csv`: `Item[0..9]` |
| `NPC 购买` | Gil shop | `GilShopItem.csv`: `Item` |
| `军票兑换` | GC seals exchange | `GCScripShopItem.csv`: `Item` |
| `工匠票据兑换` | Crafting scrip exchange | `SpecialShop.csv`: `Item{Receive}` + `Item{Cost}`, using the **cost item (currency) name** that contains “巧手” + “票” |
| `采集票据兑换` | Gathering scrip exchange | `SpecialShop.csv`: `Item{Receive}` + `Item{Cost}`, using the **cost item (currency) name** that contains “大地” + “票” |
| `双色宝石兑换` | Bicolor gemstone exchange | `SpecialShop.csv`: `Item{Cost}` is “双色宝石” |
| `神典石兑换` | Tomestone exchange | `SpecialShop.csv` + `TomestonesItem.csv`: cost item id appears in `TomestonesItem.csv` |
| `市场购买` | Market board | `Item.csv`: `IsUntradable` (tradable ⇒ added) |

### `items.obtainMethodDetails`
Additional metadata for specific sources:
- `NPC 购买.priceLow`: from `Item.csv` `Price{Low}` when the item appears in `GilShopItem.csv` and `priceLow > 0`.

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
    { "itemId": 2210, "amount": 1 },
    { "itemId": 1000, "amount": 1 },
    { "itemId": 1001, "amount": 1 }
  ]
}
```

## Data update automation (CI)
Data updates are currently mostly manual, using a scripted workflow:
1. Update CN CSVs from `ffxiv-datamining-cn`.
2. Run `scripts/ffxiv-datamining-cn/` to normalize into project JSON.
3. If EN/JA names are missing, run the fetch (incremental NDJSON) → merge steps in `scripts/xivapi/`.
4. Logs are written to `scripts/logs/YYYY-MM-DD.log`.

## Deployment
Deployment uses Cloudflare Pages:
1. Any update on `main` triggers a build.
2. Build output is from `vite build`.
3. Production site: `https://msjcalc.pages.dev`
