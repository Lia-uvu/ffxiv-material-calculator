import fs from "node:fs";
import { performance } from "node:perf_hooks";

export const DEFAULT_USER_AGENT =
  "ffxiv-material-calculator/1.0 (+https://github.com/unknown/ffxiv-material-calculator)";

export function toNumber(value) {
  if (value == null) return null;
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

export function extractId(value) {
  if (value == null) return null;
  if (typeof value === "number") return value;
  if (typeof value === "string") {
    const num = Number(value);
    return Number.isFinite(num) ? num : null;
  }
  if (typeof value === "object") {
    const candidate = value.row_id ?? value.id ?? value.ID;
    if (candidate != null) return extractId(candidate);
  }
  return null;
}

export function readJsonlLines(filePath) {
  if (!fs.existsSync(filePath)) return [];
  const content = fs.readFileSync(filePath, "utf-8");
  if (!content.trim()) return [];
  return content
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

export function countJsonlLines(filePath) {
  if (!fs.existsSync(filePath)) return 0;
  const content = fs.readFileSync(filePath, "utf-8");
  if (!content.trim()) return 0;
  return content.split("\n").filter((line) => line.trim()).length;
}

export function ensureDir(filePath) {
  fs.mkdirSync(filePath, { recursive: true });
}

export function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function fetchJsonWithRetry(url, options, config) {
  const {
    maxRetries = 5,
    baseDelayMs = 1000,
    jitterMs = 250,
    retryStatuses = new Set([429, 500, 502, 503, 504]),
  } = config ?? {};

  let lastError = null;
  let attempt = 0;

  while (attempt <= maxRetries) {
    const started = performance.now();
    try {
      const response = await fetch(url, options);
      const durationMs = Math.round(performance.now() - started);

      if (!response.ok) {
        if (retryStatuses.has(response.status)) {
          lastError = new Error(`HTTP ${response.status}`);
          const waitMs = Math.min(baseDelayMs * 2 ** attempt, 30000);
          const jitter = Math.floor(Math.random() * jitterMs);
          await delay(waitMs + jitter);
          attempt += 1;
          continue;
        }
        const body = await response.text();
        const error = new Error(`HTTP ${response.status}: ${body}`);
        error.status = response.status;
        throw error;
      }

      const payload = await response.json();
      return { payload, retries: attempt, durationMs };
    } catch (error) {
      lastError = error;
      if (error?.status && !retryStatuses.has(error.status)) {
        throw error;
      }
      if (attempt >= maxRetries) break;
      const waitMs = Math.min(baseDelayMs * 2 ** attempt, 30000);
      const jitter = Math.floor(Math.random() * jitterMs);
      await delay(waitMs + jitter);
      attempt += 1;
    }
  }

  throw lastError ?? new Error("Request failed after retries");
}

export function normalizeAfterToken(payload, lastRow) {
  if (payload?.next != null) return payload.next;
  if (payload?.next_page != null) return payload.next_page;
  if (payload?.after != null) return payload.after;
  const id = extractId(lastRow?.row_id ?? lastRow?.ID ?? lastRow?.id ?? lastRow);
  return id != null ? id : null;
}

export function readCheckpoint(checkpointPath) {
  if (!fs.existsSync(checkpointPath)) return null;
  try {
    return JSON.parse(fs.readFileSync(checkpointPath, "utf-8"));
  } catch (error) {
    console.warn(`Failed to read checkpoint at ${checkpointPath}:`, error.message);
    return null;
  }
}

export function writeCheckpoint(checkpointPath, data) {
  fs.writeFileSync(checkpointPath, JSON.stringify(data, null, 2));
}

export function writeJsonlLine(stream, data) {
  stream.write(`${JSON.stringify(data)}\n`);
}

export function toPatchString(value) {
  if (value == null) return null;
  const num = Number(value);
  if (!Number.isFinite(num)) return null;
  const rounded = Math.round(num * 100) / 100;
  return rounded % 1 === 0 ? rounded.toFixed(1) : String(rounded);
}

export function uniqueSorted(items) {
  return Array.from(new Set(items)).sort();
}
