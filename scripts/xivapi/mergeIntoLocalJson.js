#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DEFAULT_INCREMENTAL_PATH = path.resolve(
  __dirname,
  './cache/nameMap.incremental.ndjson'
);
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

const ensureDir = async (dirPath) => {
  await fs.mkdir(dirPath, { recursive: true });
};

const getLogPath = (logDir) => {
  const date = new Date().toISOString().slice(0, 10);
  return path.join(logDir, `${date}.log`);
};

const appendLogLine = async ({ logPath, payload }) => {
  const line = `${JSON.stringify(payload)}\n`;
  await fs.appendFile(logPath, line, 'utf-8');
};

const shouldUpdateName = ({ existing, zhName }) => {
  if (!existing) return true;
  if (!existing.trim()) return true;
  if (zhName && existing.trim() === zhName.trim()) return true;
  return false;
};

const readNdjson = async (filePath) => {
  try {
    const raw = await fs.readFile(filePath, 'utf-8');
    return raw
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        try {
          return JSON.parse(line);
        } catch (error) {
          return null;
        }
      })
      .filter(Boolean);
  } catch (error) {
    return [];
  }
};

const run = async () => {
  const args = parseArgs(process.argv.slice(2));
  const incrementalPath = path.resolve(args.get('incremental') ?? DEFAULT_INCREMENTAL_PATH);
  const itemsArg = args.get('items');
  if (!itemsArg) {
    throw new Error('Missing required --items argument. Historical XIVAPI tooling no longer writes src/data by default.');
  }
  const itemsPath = path.resolve(itemsArg);
  const logDir = path.resolve(args.get('log-dir') ?? DEFAULT_LOG_DIR);
  const clearIncremental = Boolean(args.get('clear-incremental'));

  await ensureDir(logDir);
  await ensureDir(path.dirname(incrementalPath));

  const logPath = getLogPath(logDir);
  const startedAt = Date.now();

  const incrementalEntries = await readNdjson(incrementalPath);
  const nameMap = new Map();
  for (const entry of incrementalEntries) {
    if (!entry || !Number.isFinite(Number(entry.id))) {
      continue;
    }
    nameMap.set(Number(entry.id), {
      en: entry.en ?? null,
      ja: entry.ja ?? null
    });
  }

  const itemsRaw = await fs.readFile(itemsPath, 'utf-8');
  const items = JSON.parse(itemsRaw);
  const itemsById = new Map(items.map((item) => [item.id, item]));

  let updatedEn = 0;
  let updatedJa = 0;
  let skippedEn = 0;
  let skippedJa = 0;
  const missingItems = [];
  const missingNames = [];

  for (const [id, names] of nameMap.entries()) {
    const item = itemsById.get(id);
    if (!item) {
      missingItems.push(id);
      continue;
    }
    item.name = item.name ?? {};
    const zhName = item.name['zh-CN'];

    if (names.en) {
      if (shouldUpdateName({ existing: item.name.en, zhName })) {
        item.name.en = names.en;
        updatedEn += 1;
      } else {
        skippedEn += 1;
      }
    } else {
      missingNames.push({ id, language: 'en' });
    }

    if (names.ja) {
      if (shouldUpdateName({ existing: item.name.ja, zhName })) {
        item.name.ja = names.ja;
        updatedJa += 1;
      } else {
        skippedJa += 1;
      }
    } else {
      missingNames.push({ id, language: 'ja' });
    }
  }

  await fs.writeFile(itemsPath, `${JSON.stringify(items, null, 2)}\n`, 'utf-8');

  if (clearIncremental) {
    await fs.writeFile(incrementalPath, '', 'utf-8');
  }

  const finishedAt = Date.now();
  const logPayload = {
    type: 'merge-complete',
    at: new Date(finishedAt).toISOString(),
    durationMs: finishedAt - startedAt,
    totalEntries: nameMap.size,
    updatedEn,
    updatedJa,
    skippedEn,
    skippedJa,
    missingItems,
    missingNames,
    incrementalPath,
    itemsPath,
    clearedIncremental: clearIncremental
  };

  await appendLogLine({ logPath, payload: logPayload });

  console.log(`Merged names into ${itemsPath}`);
  console.log(
    `Updated en: ${updatedEn}, updated ja: ${updatedJa}, skipped en: ${skippedEn}, skipped ja: ${skippedJa}`
  );
  console.log(`Missing item ids: ${missingItems.length}`);
  console.log(`Log file: ${logPath}`);
  if (clearIncremental) {
    console.log(`Cleared incremental file: ${incrementalPath}`);
  }
};

run();
