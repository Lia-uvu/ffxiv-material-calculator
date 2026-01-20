import fs from "node:fs";
import path from "node:path";

import {
  DEFAULT_USER_AGENT,
  countJsonlLines,
  delay,
  extractId,
  fetchJsonWithRetry,
  normalizeAfterToken,
  readCheckpoint,
  toNumber,
  toPatchString,
  writeCheckpoint,
  writeJsonlLine,
} from "./utils.mjs";

const config = {
  baseUrl: process.env.XIVAPI_BASE_URL ?? "https://v2.xivapi.com/api/sheet",
  sheet: process.env.XIVAPI_SHEET ?? "Recipe",
  language: process.env.XIVAPI_LANGUAGE ?? "en",
  version: process.env.XIVAPI_VERSION ?? "7.0",
  patchMax: Number(process.env.PATCH_MAX ?? "7.0"),
  limit: Number(process.env.LIMIT ?? "500"),
  minDelayMs: Number(process.env.MIN_DELAY_MS ?? "200"),
  checkpointPath:
    process.env.CHECKPOINT_PATH ?? path.join("scripts", "xivapi", "recipes_checkpoint.json"),
  outputPath: process.env.OUTPUT_PATH ?? path.join("src", "data", "recipes_7.0.jsonl"),
  userAgent: process.env.USER_AGENT ?? DEFAULT_USER_AGENT,
};

if (Number.isNaN(config.limit) || config.limit <= 0) {
  throw new Error(`Invalid LIMIT: ${config.limit}`);
}

if (Number.isNaN(config.patchMax)) {
  throw new Error(`Invalid PATCH_MAX: ${config.patchMax}`);
}

const outputDir = path.dirname(config.outputPath);
fs.mkdirSync(outputDir, { recursive: true });

const outputStream = fs.createWriteStream(config.outputPath, { flags: "a" });

const checkpoint = readCheckpoint(config.checkpointPath);
let after = checkpoint?.after ?? null;
let written = checkpoint?.written ?? countJsonlLines(config.outputPath);

const fields = [
  "ItemResult@as(raw)",
  "AmountResult",
  "Ingredient@as(raw)",
  "AmountIngredient",
  "PatchNumber",
].join(",");

async function fetchPage(currentAfter) {
  const url = new URL(`${config.baseUrl}/${config.sheet}`);
  url.searchParams.set("fields", fields);
  url.searchParams.set("limit", String(config.limit));
  url.searchParams.set("language", config.language);
  if (config.version) url.searchParams.set("version", config.version);
  if (currentAfter != null) url.searchParams.set("after", String(currentAfter));

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

function toRecipeRows(payload) {
  return payload?.rows ?? payload?.results ?? payload?.data ?? [];
}

function normalizeIngredients(ingredients, amounts) {
  const list = [];
  const ids = Array.isArray(ingredients) ? ingredients : [];
  const qtys = Array.isArray(amounts) ? amounts : [];
  const max = Math.max(ids.length, qtys.length);
  for (let i = 0; i < max; i += 1) {
    const itemId = extractId(ids[i]);
    const amount = toNumber(qtys[i]);
    if (itemId == null || amount == null || amount <= 0) continue;
    list.push({ itemId, amount });
  }
  return list;
}

let pageIndex = 0;
let hasMore = true;

while (hasMore) {
  const { payload, retries, durationMs } = await fetchPage(after);
  const rows = toRecipeRows(payload);

  if (!Array.isArray(rows) || rows.length === 0) {
    console.log(`[recipes] empty page, stopping. after=${after ?? "start"}`);
    break;
  }

  let accepted = 0;
  for (const row of rows) {
    const fieldsData = row?.fields ?? row?.Fields ?? row ?? {};
    const patchNumber = toNumber(fieldsData?.PatchNumber);
    if (patchNumber == null || patchNumber > config.patchMax) continue;

    const id = extractId(row?.row_id ?? row?.ID ?? row?.id);
    const resultItemId = extractId(fieldsData?.["ItemResult@as(raw)"] ?? fieldsData?.ItemResult);
    const resultAmount = toNumber(fieldsData?.AmountResult) ?? 1;
    if (id == null || resultItemId == null) continue;

    const materials = normalizeIngredients(
      fieldsData?.["Ingredient@as(raw)"] ?? fieldsData?.Ingredient,
      fieldsData?.AmountIngredient
    );
    const patch = toPatchString(patchNumber);

    writeJsonlLine(outputStream, {
      id,
      resultItemId,
      resultAmount,
      patch,
      materials,
    });
    written += 1;
    accepted += 1;
  }

  const lastRow = rows[rows.length - 1];
  after = normalizeAfterToken(payload, lastRow);

  writeCheckpoint(config.checkpointPath, { after, written });

  console.log(
    `[recipes] page=${pageIndex} after=${after ?? "end"} ` +
      `accepted=${accepted} written=${written} ` +
      `durationMs=${durationMs} retries=${retries}`
  );

  pageIndex += 1;

  if (after == null) {
    hasMore = false;
  } else {
    await delay(config.minDelayMs);
  }
}

outputStream.end();
console.log(`[recipes] done. wrote=${written} file=${config.outputPath}`);
