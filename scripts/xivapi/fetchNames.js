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
const DEFAULT_CHECKPOINT_PATH = path.resolve(__dirname, 'cache/nameFetch.checkpoint.ndjson');
const DEFAULT_FAILED_PATH = path.resolve(__dirname, 'cache/failed-ids.ndjson');
const DEFAULT_LOG_DIR = path.resolve(__dirname, '../logs');
const DEFAULT_BASE_URL = 'https://v2.xivapi.com';
const DEFAULT_FIELDS = 'Name';
const DEFAULT_RPS = 3;
const DEFAULT_CONCURRENCY = 6;
const DEFAULT_TIMEOUT_MS = 12000;
const DEFAULT_MAX_RETRIES = 4;

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

const ensureDir = async (dirPath) => {
  await fs.mkdir(dirPath, { recursive: true });
};

const appendLogLine = async ({ logPath, payload }) => {
  const line = `${JSON.stringify(payload)}\n`;
  await fs.appendFile(logPath, line, 'utf-8');
};

const getLogPath = (logDir) => {
  const date = new Date().toISOString().slice(0, 10);
  return path.join(logDir, `${date}.log`);
};

const extractName = (data) => {
  if (!data) return null;
  if (data.fields?.Name) return data.fields.Name;
  if (data.Name) return data.Name;
  if (data.fields?.name) return data.fields.name;
  return null;
};

const readNdjsonIds = async (filePath) => {
  try {
    const raw = await fs.readFile(filePath, 'utf-8');
    return raw
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        try {
          const parsed = JSON.parse(line);
          if (typeof parsed === 'number') return parsed;
          if (typeof parsed === 'string') return Number(parsed);
          if (parsed && typeof parsed === 'object' && parsed.id != null) return Number(parsed.id);
          return null;
        } catch (error) {
          return null;
        }
      })
      .filter((value) => Number.isFinite(value));
  } catch (error) {
    return [];
  }
};

const readIdsFromFile = async (filePath) => {
  const raw = await fs.readFile(filePath, 'utf-8');
  const parsed = JSON.parse(raw);
  if (!Array.isArray(parsed)) {
    throw new Error(`Expected array in ${filePath}`);
  }
  return parsed.map((value) => Number(value)).filter((value) => Number.isFinite(value));
};

const readRetryFailedIds = async (filePath) => {
  const raw = await fs.readFile(filePath, 'utf-8');
  return raw
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      try {
        const parsed = JSON.parse(line);
        if (typeof parsed === 'number') return parsed;
        if (typeof parsed === 'string') return Number(parsed);
        if (parsed && typeof parsed === 'object' && parsed.id != null) return Number(parsed.id);
        return null;
      } catch (error) {
        const asNumber = Number(line);
        return Number.isFinite(asNumber) ? asNumber : null;
      }
    })
    .filter((value) => Number.isFinite(value));
};

const createRateLimiter = (rps) => {
  if (!rps || rps <= 0) {
    return async () => {};
  }
  const intervalMs = Math.ceil(1000 / rps);
  let nextAllowed = Date.now();
  return async () => {
    const now = Date.now();
    const waitMs = Math.max(0, nextAllowed - now);
    nextAllowed = Math.max(now, nextAllowed) + intervalMs;
    if (waitMs > 0) {
      await sleep(waitMs);
    }
  };
};

const buildUrl = ({ baseUrl, id, language, fields }) => {
  const url = new URL(`/api/sheet/Item/${id}`, baseUrl);
  url.searchParams.set('fields', fields);
  url.searchParams.set('language', language);
  return url;
};

const fetchWithRetry = async ({
  baseUrl,
  fields,
  id,
  language,
  limiter,
  timeoutMs,
  maxRetries,
  logPath
}) => {
  let attempt = 0;
  let lastError = null;
  let lastStatus = null;
  while (attempt <= maxRetries) {
    await limiter();
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    let response;
    try {
      response = await fetch(buildUrl({ baseUrl, id, language, fields }), {
        headers: {
          'User-Agent': 'ffxiv-material-calculator/1.0',
          Accept: 'application/json'
        },
        signal: controller.signal
      });
      clearTimeout(timeout);
      lastStatus = response.status;
      if (response.ok) {
        const data = await response.json();
        const name = extractName(data);
        if (name) {
          return { ok: true, name, attempts: attempt + 1 };
        }
        lastError = `empty-name`;
        return { ok: false, error: lastError, status: response.status, attempts: attempt + 1 };
      }

      const retryable = response.status === 429 || response.status >= 500;
      lastError = `http-${response.status}`;
      if (!retryable) {
        return { ok: false, error: lastError, status: response.status, attempts: attempt + 1 };
      }
    } catch (error) {
      clearTimeout(timeout);
      lastError = error instanceof Error ? error.message : String(error);
      lastStatus = 'error';
    }

    if (attempt >= maxRetries) {
      break;
    }
    const baseDelay = 500 * 2 ** attempt;
    const jitter = Math.floor(Math.random() * 250);
    const waitMs = baseDelay + jitter;
    await appendLogLine({
      logPath,
      payload: {
        type: 'backoff',
        id,
        language,
        attempt: attempt + 1,
        waitMs,
        status: lastStatus,
        error: lastError,
        at: new Date().toISOString()
      }
    });
    await sleep(waitMs);
    attempt += 1;
  }
  return {
    ok: false,
    error: lastError,
    status: lastStatus,
    attempts: attempt + 1
  };
};

const run = async () => {
  const args = parseArgs(process.argv.slice(2));
  const idsArg = args.get('ids');
  if (!idsArg) {
    throw new Error('Missing required --ids argument. Historical XIVAPI tooling no longer reads src/data by default.');
  }
  const idsPath = path.resolve(idsArg);
  const incrementalPath = path.resolve(args.get('incremental') ?? DEFAULT_INCREMENTAL_PATH);
  const checkpointPath = path.resolve(args.get('checkpoint') ?? DEFAULT_CHECKPOINT_PATH);
  const failedPath = path.resolve(args.get('failed') ?? DEFAULT_FAILED_PATH);
  const retryFailedPath = args.get('retry-failed')
    ? path.resolve(args.get('retry-failed'))
    : null;
  const logDir = path.resolve(args.get('log-dir') ?? DEFAULT_LOG_DIR);
  const baseUrl = args.get('base-url') ?? DEFAULT_BASE_URL;
  const fields = args.get('fields') ?? DEFAULT_FIELDS;
  const rps = Number(args.get('rps') ?? DEFAULT_RPS);
  const concurrency = Number(args.get('concurrency') ?? DEFAULT_CONCURRENCY);
  const timeoutMs = Number(args.get('timeout-ms') ?? DEFAULT_TIMEOUT_MS);
  const maxRetries = Number(args.get('max-retries') ?? DEFAULT_MAX_RETRIES);

  await ensureDir(path.dirname(incrementalPath));
  await ensureDir(path.dirname(checkpointPath));
  await ensureDir(path.dirname(failedPath));
  await ensureDir(logDir);

  const logPath = getLogPath(logDir);
  const startedAt = Date.now();

  const ids = retryFailedPath ? await readRetryFailedIds(retryFailedPath) : await readIdsFromFile(idsPath);
  const checkpointIds = new Set(await readNdjsonIds(checkpointPath));
  const incrementalIds = new Set(await readNdjsonIds(incrementalPath));
  const completedIds = new Set([...checkpointIds, ...incrementalIds]);
  const targetIds = ids.filter((id) => Number.isFinite(id) && !completedIds.has(id));

  await appendLogLine({
    logPath,
    payload: {
      type: 'fetch-start',
      at: new Date(startedAt).toISOString(),
      idsPath: retryFailedPath ? retryFailedPath : idsPath,
      totalIds: ids.length,
      skippedIds: ids.length - targetIds.length,
      rps,
      concurrency,
      timeoutMs,
      maxRetries,
      baseUrl
    }
  });

  if (targetIds.length === 0) {
    await appendLogLine({
      logPath,
      payload: {
        type: 'fetch-complete',
        at: new Date().toISOString(),
        message: 'No new ids to fetch.'
      }
    });
    console.log('No new ids to fetch.');
    return;
  }

  const limiter = createRateLimiter(rps);
  const failed = [];
  const success = [];
  let cursor = 0;
  let completed = 0;

  const worker = async () => {
    while (true) {
      const index = cursor;
      cursor += 1;
      if (index >= targetIds.length) {
        return;
      }
      const id = targetIds[index];

      const [enResult, jaResult] = await Promise.all([
        fetchWithRetry({
          baseUrl,
          fields,
          id,
          language: 'en',
          limiter,
          timeoutMs,
          maxRetries,
          logPath
        }),
        fetchWithRetry({
          baseUrl,
          fields,
          id,
          language: 'ja',
          limiter,
          timeoutMs,
          maxRetries,
          logPath
        })
      ]);

      if (enResult.ok && jaResult.ok) {
        const entry = {
          id,
          en: enResult.name,
          ja: jaResult.name,
          fetchedAt: new Date().toISOString(),
          source: baseUrl
        };
        await fs.appendFile(incrementalPath, `${JSON.stringify(entry)}\n`, 'utf-8');
        await fs.appendFile(checkpointPath, `${JSON.stringify({ id, ok: true })}\n`, 'utf-8');
        success.push(id);
      } else {
        const reason = {
          en: enResult.ok ? null : enResult.error ?? enResult.status,
          ja: jaResult.ok ? null : jaResult.error ?? jaResult.status
        };
        failed.push({ id, reason });
        await appendLogLine({
          logPath,
          payload: {
            type: 'fetch-failed',
            id,
            reason,
            at: new Date().toISOString()
          }
        });
      }

      completed += 1;
      if (completed % 100 === 0 || completed === targetIds.length) {
        const percent = ((completed / targetIds.length) * 100).toFixed(1);
        console.log(`Progress: ${completed}/${targetIds.length} (${percent}%)`);
      }
    }
  };

  const workers = Array.from({ length: Math.max(1, concurrency) }, () => worker());
  await Promise.all(workers);

  if (failed.length > 0) {
    const failedLines = failed.map((entry) => JSON.stringify(entry)).join('\n');
    await fs.writeFile(failedPath, `${failedLines}\n`, 'utf-8');
  } else {
    await fs.writeFile(failedPath, '', 'utf-8');
  }

  const finishedAt = Date.now();
  await appendLogLine({
    logPath,
    payload: {
      type: 'fetch-complete',
      at: new Date(finishedAt).toISOString(),
      durationMs: finishedAt - startedAt,
      requestedIds: targetIds.length,
      successIds: success.length,
      failedIds: failed.length,
      failedPath
    }
  });

  console.log(`Fetch complete. Success: ${success.length}, Failed: ${failed.length}`);
  console.log(`Incremental NDJSON: ${incrementalPath}`);
  console.log(`Checkpoint NDJSON: ${checkpointPath}`);
  console.log(`Failed IDs file: ${failedPath}`);
  console.log(`Log file: ${logPath}`);
};

run();
