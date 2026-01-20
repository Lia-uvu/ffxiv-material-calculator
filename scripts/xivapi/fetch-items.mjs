import fs from "node:fs";
import path from "node:path";

import {
  DEFAULT_USER_AGENT,
  delay,
  extractId,
  fetchJsonWithRetry,
  readJsonlLines,
  uniqueSorted,
  writeJsonlLine,
} from "./utils.mjs";

const config = {
  baseUrl: process.env.XIVAPI_BASE_URL ?? "https://v2.xivapi.com/api/sheet",
  sheet: process.env.XIVAPI_SHEET ?? "Item",
  language: process.env.XIVAPI_LANGUAGE ?? "en",
  version: process.env.XIVAPI_VERSION ?? "7.0",
  rowsParam: process.env.ROWS_PARAM ?? "rows",
  batchSize: Number(process.env.BATCH_SIZE ?? "100"),
  concurrency: Math.min(Number(process.env.CONCURRENCY ?? "1"), 2),
  minDelayMs: Number(process.env.MIN_DELAY_MS ?? "200"),
  recipesPath: process.env.RECIPES_PATH ?? path.join("src", "data", "recipes_7.0.jsonl"),
  outputPath: process.env.OUTPUT_PATH ?? path.join("src", "data", "items_7.0.jsonl"),
  userAgent: process.env.USER_AGENT ?? DEFAULT_USER_AGENT,
};

if (Number.isNaN(config.batchSize) || config.batchSize <= 0) {
  throw new Error(`Invalid BATCH_SIZE: ${config.batchSize}`);
}

if (Number.isNaN(config.concurrency) || config.concurrency <= 0) {
  throw new Error(`Invalid CONCURRENCY: ${config.concurrency}`);
}

const outputDir = path.dirname(config.outputPath);
fs.mkdirSync(outputDir, { recursive: true });

const outputStream = fs.createWriteStream(config.outputPath, { flags: "a" });

function collectItemIds(recipesPath) {
  if (!fs.existsSync(recipesPath)) {
    throw new Error(`Recipes file not found: ${recipesPath}`);
  }
  const items = new Set();
  const recipes = readJsonlLines(recipesPath);
  for (const recipe of recipes) {
    if (recipe?.resultItemId != null) items.add(recipe.resultItemId);
    for (const mat of recipe?.materials ?? []) {
      if (mat?.itemId != null) items.add(mat.itemId);
    }
  }
  return items;
}

function collectExistingItemIds(outputPath) {
  if (!fs.existsSync(outputPath)) return new Set();
  const items = new Set();
  const existing = readJsonlLines(outputPath);
  for (const item of existing) {
    if (item?.id != null) items.add(item.id);
  }
  return items;
}

const allItemIds = collectItemIds(config.recipesPath);
const craftableIds = new Set();
for (const recipe of readJsonlLines(config.recipesPath)) {
  if (recipe?.resultItemId != null) craftableIds.add(recipe.resultItemId);
}

const existingItemIds = collectExistingItemIds(config.outputPath);
const pendingIds = uniqueSorted(
  [...allItemIds].filter((id) => !existingItemIds.has(id))
);

const fields = [
  "Name",
  "IsCrystal",
  "IsUntradable",
  "CanBeMarketed",
  "PriceLow",
].join(",");

async function fetchBatch(batch) {
  const url = new URL(`${config.baseUrl}/${config.sheet}`);
  url.searchParams.set(config.rowsParam, batch.join(","));
  url.searchParams.set("fields", fields);
  url.searchParams.set("language", config.language);
  if (config.version) url.searchParams.set("version", config.version);

  const { payload, retries, durationMs } = await fetchJsonWithRetry(
    url,
    {
      headers: {
        "User-Agent": config.userAgent,
      },
    },
    {}
  );

  return { payload, retries, durationMs };
}

function toItemRows(payload) {
  return payload?.rows ?? payload?.results ?? payload?.data ?? [];
}

function buildObtainMethods(itemFields, itemId) {
  const methods = new Set();
  if (itemId != null && craftableIds.has(itemId)) methods.add("CRAFT");

  const canBeMarketed = itemFields?.CanBeMarketed;
  if (canBeMarketed === true || itemFields?.IsUntradable === false) {
    methods.add("MARKET");
  }

  if ((itemFields?.PriceLow ?? 0) > 0) {
    methods.add("NPC");
  }

  if (itemFields?.IsCrystal === true) {
    methods.add("GATHER_MINER");
    methods.add("GATHER_BOTANIST");
  }

  return Array.from(methods);
}

let processed = 0;
let batchIndex = 0;

const batches = [];
for (let i = 0; i < pendingIds.length; i += config.batchSize) {
  batches.push(pendingIds.slice(i, i + config.batchSize));
}

async function runWorker(workerId) {
  while (batchIndex < batches.length) {
    const index = batchIndex;
    const batch = batches[index];
    batchIndex += 1;

    const { payload, retries, durationMs } = await fetchBatch(batch);
    const rows = toItemRows(payload);

    for (const row of rows) {
      const fieldsData = row?.fields ?? row?.Fields ?? row ?? {};
      const id = extractId(row?.row_id ?? row?.ID ?? row?.id);
      const name = fieldsData?.Name ?? "";
      const isCrystal = Boolean(fieldsData?.IsCrystal);
      if (id == null || !name) continue;

      const obtainMethods = buildObtainMethods(fieldsData, id);
      writeJsonlLine(outputStream, {
        id,
        name,
        isCrystal,
        obtainMethods,
      });
      processed += 1;
    }

    console.log(
      `[items] worker=${workerId} batch=${index + 1}/${batches.length} ` +
        `ids=${batch.length} processed=${processed} durationMs=${durationMs} retries=${retries}`
    );

    if (config.minDelayMs > 0) {
      await delay(config.minDelayMs);
    }
  }
}

if (pendingIds.length === 0) {
  console.log("[items] no new items to fetch.");
} else {
  const workers = [];
  for (let i = 0; i < config.concurrency; i += 1) {
    workers.push(runWorker(i + 1));
  }
  await Promise.all(workers);
}

outputStream.end();
console.log(`[items] done. wrote=${processed} file=${config.outputPath}`);
