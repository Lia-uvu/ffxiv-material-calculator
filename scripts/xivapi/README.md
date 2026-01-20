# XIVAPI Data Fetcher

These scripts fetch **patch ≤ 7.0** recipe data from XIVAPI (v2), derive the related item IDs, and then fetch item data. Output is written as JSONL first to keep memory usage low, and can then be converted to JSON arrays for `src/data`.

## Requirements

- Node.js 18+ (for `fetch`).
- A polite `User-Agent` is required. Provide `USER_AGENT` or edit the default in `utils.mjs`.

## Recipes (streamed JSONL)

```bash
node scripts/xivapi/fetch-recipes.mjs \
  USER_AGENT="ffxiv-material-calculator/1.0 (contact@example.com)"
```

Defaults:
- `OUTPUT_PATH=src/data/recipes_7.0.jsonl`
- `CHECKPOINT_PATH=scripts/xivapi/recipes_checkpoint.json`
- `LIMIT=500`
- `MIN_DELAY_MS=200`
- `PATCH_MAX=7.0`

The script uses `fields=ItemResult,AmountResult,Ingredient,AmountIngredient,PatchNumber` and paginates with `after + limit`. It writes one JSON object per line and updates the checkpoint after each page.

## Items (streamed JSONL)

```bash
node scripts/xivapi/fetch-items.mjs \
  USER_AGENT="ffxiv-material-calculator/1.0 (contact@example.com)"
```

Defaults:
- `RECIPES_PATH=src/data/recipes_7.0.jsonl`
- `OUTPUT_PATH=src/data/items_7.0.jsonl`
- `BATCH_SIZE=100`
- `CONCURRENCY=1` (max 2)
- `MIN_DELAY_MS=200`

The script derives item IDs from the recipe JSONL and fetches item data in batches. Output uses only IDs plus minimal fields:

```json
{ "id": 123, "name": "Item Name", "isCrystal": false, "obtainMethods": ["CRAFT", "MARKET"] }
```

## Convert JSONL to JSON array

```bash
INPUT_PATH=src/data/recipes_7.0.jsonl \
OUTPUT_PATH=src/data/recipes.json \
node scripts/xivapi/jsonl-to-array.mjs

INPUT_PATH=src/data/items_7.0.jsonl \
OUTPUT_PATH=src/data/items.json \
node scripts/xivapi/jsonl-to-array.mjs
```

## Optional configuration

- `XIVAPI_BASE_URL` (default `https://v2.xivapi.com/api/sheet`)
- `XIVAPI_SHEET` (default `Recipe` or `Item`)
- `XIVAPI_LANGUAGE` (default `zh`)
- `IDS_PARAM` (default `ids`)

If the API uses a different base path or ID parameter, override these env vars.
