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

1. **Fetch raw data**:
   ```bash
   node scripts/xivapi/fetchNames.js
   ```
   - Reads `src/data/needed_item_ids.json` by default.
   - Writes `scripts/xivapi/data/xivapi-names-raw.json`.
   - Request logs are written to `scripts/logs/`.

2. **Normalize into `{id,en,ja}`**:
   ```bash
   node scripts/xivapi/normalizeXivapiResponse.js
   ```
   - Outputs `scripts/xivapi/data/xivapi-names-normalized.json`.

3. **Merge into local items.json**:
   ```bash
   node scripts/xivapi/mergeIntoLocalJson.js
   ```
   - Updates `src/data/items.json` by default.
   - Writes merge statistics to `scripts/logs/`.

#### Server-friendly strategy
XIVAPI is a public service, so keep the load light:
- **Throttling**: default concurrency is 3 with a 250ms delay between requests (configurable).
- **Minimal fields**: only request `Name` to keep payloads small.
- **Retry-friendly**: failures and missing IDs are logged so you can re-run selectively.
- **Two-stage processing**: fetch raw data first, then normalize + merge locally to avoid duplicate API calls.

Optional parameters example:
```bash
node scripts/xivapi/fetchNames.js \
  --ids src/data/needed_item_ids.json \
  --concurrency 2 \
  --delay-ms 400
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
    "CRAFT",
    "MARKET",
    "NPC",
    "GATHER_MINER",
    "GATHER_BOTANIST"
  ]
}
```

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
3. If EN/JA names are missing, run the fetch → normalize → merge steps in `scripts/xivapi/`.
4. Update `src/data/version.json` to record the data source and timestamp.

## Version record
`src/data/version.json` captures the data source and update metadata for traceability. Recommended fields:
- `data_version`: manual version number
- `updated_at`: update date
- `i18n_source`: source of EN/JA names

## Deployment
Deployment uses Cloudflare Pages:
1. Any update on `main` triggers a build.
2. Build output is from `vite build`.
3. Production site: `https://msjcalc.pages.dev`
