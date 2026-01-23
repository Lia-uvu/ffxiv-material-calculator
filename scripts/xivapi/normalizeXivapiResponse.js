#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DEFAULT_INPUT = path.resolve(__dirname, 'data/xivapi-names-raw.json');
const DEFAULT_OUTPUT = path.resolve(__dirname, 'data/xivapi-names-normalized.json');

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

const extractName = (data) => {
  if (!data) return null;
  if (data.fields?.Name) return data.fields.Name;
  if (data.Name) return data.Name;
  if (data.fields?.name) return data.fields.name;
  return null;
};

const run = async () => {
  const args = parseArgs(process.argv.slice(2));
  const inputPath = path.resolve(args.get('input') ?? DEFAULT_INPUT);
  const outputPath = path.resolve(args.get('output') ?? DEFAULT_OUTPUT);

  const raw = await fs.readFile(inputPath, 'utf-8');
  const payload = JSON.parse(raw);
  const results = Array.isArray(payload) ? payload : payload.results ?? [];
  const ids = Array.isArray(payload) ? [] : payload.ids ?? [];

  const itemMap = new Map();
  const missingEntries = [];

  for (const entry of results) {
    const id = entry.id;
    const language = entry.language;
    if (!itemMap.has(id)) {
      itemMap.set(id, { id, en: null, ja: null });
    }
    const name = entry.ok ? extractName(entry.data) : null;
    if (!name) {
      missingEntries.push({ id, language });
      continue;
    }
    const item = itemMap.get(id);
    if (language === 'en') {
      item.en = name;
    } else if (language === 'ja') {
      item.ja = name;
    } else {
      item[language] = name;
    }
  }

  const orderedItems = ids.length
    ? ids.map((id) => itemMap.get(id)).filter(Boolean)
    : Array.from(itemMap.values()).sort((a, b) => a.id - b.id);

  const output = {
    generatedAt: new Date().toISOString(),
    source: path.basename(inputPath),
    missingEntries,
    items: orderedItems
  };

  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, 'utf-8');

  console.log(`Saved normalized output to ${outputPath}`);
};

run();
