#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { execFile } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DEFAULT_IDS_PATH = path.resolve(__dirname, '../../src/data/needed_item_ids.json');
const DEFAULT_OUTPUT_DIR = path.resolve(__dirname, 'data');
const DEFAULT_LOG_DIR = path.resolve(__dirname, '../logs');
const DEFAULT_BASE_URL = 'https://v2.xivapi.com';
const DEFAULT_FIELDS = 'Name';
const DEFAULT_LANGUAGES = ['en', 'ja'];
const DEFAULT_DELAY_MS = 250;
const DEFAULT_CONCURRENCY = 3;

const execFileAsync = promisify(execFile);

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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

const fetchSingleName = async ({ baseUrl, id, language, fields }) => {
  const url = new URL(`/api/sheet/Item/${id}`, baseUrl);
  url.searchParams.set('fields', fields);
  url.searchParams.set('language', language);

  const marker = '\n__STATUS__';
  try {
    const { stdout } = await execFileAsync('curl', [
      '-sS',
      '-H',
      'User-Agent: ffxiv-material-calculator/1.0',
      '-H',
      'Accept: application/json',
      '-w',
      `${marker}%{http_code}`,
      url.toString()
    ]);
    const [body, statusRaw] = stdout.split(marker);
    const status = Number(statusRaw?.trim()) || 0;
    if (status < 200 || status >= 300) {
      return {
        id,
        language,
        ok: false,
        status,
        data: null
      };
    }
    const data = JSON.parse(body);
    const name = extractName(data);
    return {
      id,
      language,
      ok: Boolean(name),
      status,
      data
    };
  } catch (error) {
    return {
      id,
      language,
      ok: false,
      status: 'error',
      error: error instanceof Error ? error.message : String(error),
      data: null
    };
  }
};

const run = async () => {
  const args = parseArgs(process.argv.slice(2));
  const idsPath = path.resolve(args.get('ids') ?? DEFAULT_IDS_PATH);
  const outputDir = path.resolve(args.get('out-dir') ?? DEFAULT_OUTPUT_DIR);
  const logDir = path.resolve(args.get('log-dir') ?? DEFAULT_LOG_DIR);
  const baseUrl = args.get('base-url') ?? DEFAULT_BASE_URL;
  const fields = args.get('fields') ?? DEFAULT_FIELDS;
  const delayMs = Number(args.get('delay-ms') ?? DEFAULT_DELAY_MS);
  const concurrency = Number(args.get('concurrency') ?? DEFAULT_CONCURRENCY);
  const languages = (args.get('languages') ?? DEFAULT_LANGUAGES.join(','))
    .split(',')
    .map((lang) => lang.trim())
    .filter(Boolean);

  await fs.mkdir(outputDir, { recursive: true });
  await fs.mkdir(logDir, { recursive: true });

  const idsRaw = await fs.readFile(idsPath, 'utf-8');
  const ids = JSON.parse(idsRaw);

  const startedAt = Date.now();
  const tasks = [];
  for (const id of ids) {
    for (const language of languages) {
      tasks.push({ id, language });
    }
  }

  const results = [];
  let cursor = 0;
  let completed = 0;

  const worker = async (workerId) => {
    while (true) {
      const index = cursor;
      cursor += 1;
      if (index >= tasks.length) {
        return;
      }
      const task = tasks[index];
      try {
        const result = await fetchSingleName({
          baseUrl,
          id: task.id,
          language: task.language,
          fields
        });
        results.push(result);
      } catch (error) {
        results.push({
          id: task.id,
          language: task.language,
          ok: false,
          status: 'error',
          error: error instanceof Error ? error.message : String(error),
          data: null
        });
      }
      completed += 1;
      if (completed % 200 === 0 || completed === tasks.length) {
        const percent = ((completed / tasks.length) * 100).toFixed(1);
        console.log(`Progress: ${completed}/${tasks.length} (${percent}%)`);
      }
      await sleep(delayMs + workerId * 10);
    }
  };

  const workers = Array.from({ length: concurrency }, (_, index) => worker(index));
  await Promise.all(workers);

  const finishedAt = Date.now();
  const totalRequests = results.length;
  const successRequests = results.filter((result) => result.ok).length;
  const failedRequests = totalRequests - successRequests;

  const missingIds = results
    .filter((result) => !result.ok)
    .map((result) => `${result.id}:${result.language}`);

  const output = {
    generatedAt: new Date(finishedAt).toISOString(),
    baseUrl,
    fields,
    languages,
    ids,
    results
  };

  const outputPath = path.join(outputDir, 'xivapi-names-raw.json');
  await fs.writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, 'utf-8');

  const log = {
    startedAt: new Date(startedAt).toISOString(),
    finishedAt: new Date(finishedAt).toISOString(),
    durationMs: finishedAt - startedAt,
    baseUrl,
    fields,
    languages,
    totalRequests,
    successRequests,
    failedRequests,
    missingIds
  };

  const logPath = path.join(
    logDir,
    `xivapi-fetch-${new Date(finishedAt).toISOString().replace(/[:.]/g, '-')}.json`
  );
  await fs.writeFile(logPath, `${JSON.stringify(log, null, 2)}\n`, 'utf-8');

  console.log(`Saved raw response to ${outputPath}`);
  console.log(`Log written to ${logPath}`);
};

run();
