#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DEFAULT_INPUT = path.resolve(__dirname, 'data/xivapi-names-normalized.json');
const DEFAULT_ITEMS_PATH = path.resolve(__dirname, '../../src/data/items.json');
const DEFAULT_LOG_DIR = path.resolve(__dirname, '../logs');

const parseArgs = (argv) => {
  const args = new Map();
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const next = argv[i + 1];
      if (!next || next.startsWith('--')) {
        args.set(key, true);
      } else {
        args.set(key, next);
        i += 1;
      }
    }
  }
  return args;
};

const shouldUpdateName = ({ existing, zhName }) => {
  if (!existing) return true;
  if (!existing.trim()) return true;
  if (zhName && existing.trim() === zhName.trim()) return true;
  return false;
};

const run = async () => {
  const args = parseArgs(process.argv.slice(2));
  const inputPath = path.resolve(args.get('input') ?? DEFAULT_INPUT);
  const itemsPath = path.resolve(args.get('items') ?? DEFAULT_ITEMS_PATH);
  const logDir = path.resolve(args.get('log-dir') ?? DEFAULT_LOG_DIR);

  await fs.mkdir(logDir, { recursive: true });

  const startedAt = Date.now();
  const normalizedRaw = await fs.readFile(inputPath, 'utf-8');
  const normalizedPayload = JSON.parse(normalizedRaw);
  const normalizedItems = Array.isArray(normalizedPayload)
    ? normalizedPayload
    : normalizedPayload.items ?? [];

  const itemsRaw = await fs.readFile(itemsPath, 'utf-8');
  const items = JSON.parse(itemsRaw);

  const itemsById = new Map(items.map((item) => [item.id, item]));

  const missingItemIds = [];
  const missingNormalized = [];
  let updatedEn = 0;
  let updatedJa = 0;
  let skippedEn = 0;
  let skippedJa = 0;

  for (const entry of normalizedItems) {
    const item = itemsById.get(entry.id);
    if (!item) {
      missingItemIds.push(entry.id);
      continue;
    }
    item.name = item.name ?? {};
    const zhName = item.name['zh-CN'];

    if (entry.en) {
      if (shouldUpdateName({ existing: item.name.en, zhName })) {
        item.name.en = entry.en;
        updatedEn += 1;
      } else {
        skippedEn += 1;
      }
    } else {
      missingNormalized.push({ id: entry.id, language: 'en' });
    }

    if (entry.ja) {
      if (shouldUpdateName({ existing: item.name.ja, zhName })) {
        item.name.ja = entry.ja;
        updatedJa += 1;
      } else {
        skippedJa += 1;
      }
    } else {
      missingNormalized.push({ id: entry.id, language: 'ja' });
    }
  }

  await fs.writeFile(itemsPath, `${JSON.stringify(items, null, 2)}\n`, 'utf-8');

  const finishedAt = Date.now();
  const log = {
    startedAt: new Date(startedAt).toISOString(),
    finishedAt: new Date(finishedAt).toISOString(),
    durationMs: finishedAt - startedAt,
    totalEntries: normalizedItems.length,
    updatedEn,
    updatedJa,
    skippedEn,
    skippedJa,
    missingItemIds,
    missingNormalized
  };

  const logPath = path.join(
    logDir,
    `xivapi-merge-${new Date(finishedAt).toISOString().replace(/[:.]/g, '-')}.json`
  );
  await fs.writeFile(logPath, `${JSON.stringify(log, null, 2)}\n`, 'utf-8');

  console.log(`Merged names into ${itemsPath}`);
  console.log(`Log written to ${logPath}`);
};

run();
