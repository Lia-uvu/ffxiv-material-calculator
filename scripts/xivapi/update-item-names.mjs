import fs from "node:fs";
import path from "node:path";

import {
  DEFAULT_USER_AGENT,
  delay,
  extractId,
  fetchJsonWithRetry,
} from "./utils.mjs";

const config = {
  baseUrl: process.env.XIVAPI_BASE_URL ?? "https://xivapi.com/api/sheet",
  cnBaseUrl: process.env.XIVAPI_CN_BASE_URL ?? "https://cafemaker.wakingsands.com",
  sheet: process.env.XIVAPI_SHEET ?? "Item",
  locales: (process.env.XIVAPI_LOCALES ?? "en,ja,zh-CN")
    .split(",")
    .map((locale) => locale.trim())
    .filter(Boolean),
  version: process.env.XIVAPI_VERSION ?? "",
  rowsParam: process.env.ROWS_PARAM ?? "rows",
  batchSize: Number(process.env.BATCH_SIZE ?? "100"),
  minDelayMs: Number(process.env.MIN_DELAY_MS ?? "200"),
  itemsPath: process.env.ITEMS_PATH ?? path.join("src", "data", "items.json"),
  userAgent: process.env.USER_AGENT ?? DEFAULT_USER_AGENT,
};

if (Number.isNaN(config.batchSize) || config.batchSize <= 0) {
  throw new Error(`Invalid BATCH_SIZE: ${config.batchSize}`);
}

if (Number.isNaN(config.minDelayMs) || config.minDelayMs < 0) {
  throw new Error(`Invalid MIN_DELAY_MS: ${config.minDelayMs}`);
}

function resolveBaseUrl(locale) {
  if (locale === "zh-CN") return config.cnBaseUrl;
  return config.baseUrl;
}

function resolveLanguage(locale) {
  if (locale === "zh-CN") return "zh";
  return locale;
}

function toItemRows(payload) {
  return (
    payload?.rows ??
    payload?.results ??
    payload?.data ??
    payload?.Results ??
    []
  );
}

async function fetchNames(batch, locale) {
  const baseUrl = resolveBaseUrl(locale);
  const url = new URL(`${baseUrl}/${config.sheet}`);
  if (locale === "zh-CN") {
    url.searchParams.set("ids", batch.join(","));
    url.searchParams.set("columns", "ID,Name");
  } else {
    url.searchParams.set(config.rowsParam, batch.join(","));
    url.searchParams.set("fields", "Name");
    if (config.version) url.searchParams.set("version", config.version);
  }
  url.searchParams.set("language", resolveLanguage(locale));

  const { payload, retries, durationMs } = await fetchJsonWithRetry(
    url,
    {
      headers: {
        "User-Agent": config.userAgent,
      },
    },
    {}
  );

  return { rows: toItemRows(payload), retries, durationMs };
}

const items = JSON.parse(fs.readFileSync(config.itemsPath, "utf-8"));
const itemsById = new Map(items.map((item) => [item.id, item]));
const itemIds = items.map((item) => item.id).filter((id) => id != null);

const batches = [];
for (let i = 0; i < itemIds.length; i += config.batchSize) {
  batches.push(itemIds.slice(i, i + config.batchSize));
}

let processed = 0;

for (let index = 0; index < batches.length; index += 1) {
  const batch = batches[index];
  for (const locale of config.locales) {
    const { rows, retries, durationMs } = await fetchNames(batch, locale);
    for (const row of rows) {
      const fieldsData = row?.fields ?? row?.Fields ?? row ?? {};
      const id = extractId(row?.row_id ?? row?.ID ?? row?.id);
      const name = fieldsData?.Name ?? "";
      if (id == null || !name) continue;
      const item = itemsById.get(id);
      if (!item) continue;
      if (!item.name) item.name = {};
      item.name[locale] = name;
    }
    console.log(
      `[names] batch=${index + 1}/${batches.length} locale=${locale} ` +
        `ids=${batch.length} processed=${processed} durationMs=${durationMs} retries=${retries}`
    );
    processed += batch.length;
    if (config.minDelayMs > 0) {
      await delay(config.minDelayMs);
    }
  }
}

fs.writeFileSync(config.itemsPath, `${JSON.stringify(items, null, 2)}\n`);
console.log(`[names] done. updated=${items.length} file=${config.itemsPath}`);
