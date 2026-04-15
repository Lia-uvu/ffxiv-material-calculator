# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FFXIV Material Calculator ("魔石精计算器" / msjcalc) — a Vue 3 SPA that breaks down FFXIV crafting targets into recipe trees and aggregates materials lists. Frontend-only, deployed to Cloudflare Pages at https://msjcalc.pages.dev.

UI supports three languages (zh-CN, en, ja) via vue-i18n; project docs are in Chinese and English.

## Commands

- **Dev server:** `npm run dev`
- **Build:** `npm run build`
- **Preview production build:** `npm run preview`
- **Run pipeline tests:** `python -m unittest discover -s tests -p "test_*.py"` (`python3` if `python` is unavailable locally)
- **Run stage 1 data pipeline locally:** `python scripts/pipeline/run_pipeline.py --cn-repo <path> --en-repo <path> --ja-repo <path>`
- **Run stage 2 outfit derivation locally:** `python scripts/pipeline/build_outfit_sets.py`

No JavaScript test framework is configured; there are no JS/Vue unit tests.

## Architecture

### Frontend (`src/`)

Vue 3 app using Composition API, Tailwind CSS v4, and vue-i18n. Entry: `main.js` → `App.vue` → `CalculatorPage.vue`.

- **`src/data/`** — Static JSON data (`items.json`, `recipes.json`, `outfitSets.json`, `outfitSetMeta.json`) loaded lazily via dynamic imports. `index.js` exports reactive refs (`items`, `recipes`, `outfitSets`, `dataReady`) and `resolveItemName()` for locale-aware name lookup.
- **`src/calculator/core/`** — Pure computation logic, no Vue dependencies:
  - `calcMaterials.js` — Core algorithm: recursive recipe tree expansion with cycle detection, override support, and expand/collapse control via `expandedIds`.
  - `recipeUtils.js` — Recipe lookup helpers (`buildRecipesByResultId`, `pickRecipe`).
  - `obtainMethodUtils.js` — Item obtain-method classification.
- **`src/calculator/composables/`** — Vue composables: `useItemSearch` (Fuse.js fuzzy search), `useMaterialsList`, `useMaterialsExport`, `useOnboarding`, `settingStore`.
- **`src/calculator/components/`** — Vue components organized by feature area: `search/`, `targets/`, `materials/`, `shell/`, `common/`.
- **`src/i18n/`** — Locale messages in `messages/{zh-CN,en,ja}.js`. Auto-generated outfit set name translations in `generated/outfitSetNames.json`, merged at i18n init time.

### Data Pipeline (`scripts/pipeline/`)

The published data flow is intentionally split into two stages:

- **Stage 1: canonical CSV pipeline** — `run_pipeline.py` processes upstream FFXIV datamining CSV repos (CN, EN, JA) into `items.json`, `recipes.json`, and `outfitSetMeta.json`. Steps are numbered `01_` through `07_`. Intermediate artifacts are written to `tmp/pipeline/`.
- **Stage 2: outfit-set derivation** — `build_outfit_sets.py` reads the stage-1 runtime outputs from `src/data/` and generates `outfitSets.json` plus `src/i18n/generated/outfitSetNames.json`.

GitHub Actions (`.github/workflows/update-data-pipeline.yml`) runs both stages in sequence, then builds the frontend and commits all changed runtime outputs. The workflow reruns when upstream SHAs change, when `force_run` is used, or when the current repository HEAD differs from `scripts/pipeline/state/last_successful_manifest.json`.

### Legacy Scripts (`scripts/xivapi/`)

Older Node.js scripts (`fetchNames.js`, `mergeIntoLocalJson.js`) for fetching data from XIVAPI. Superseded by the Python pipeline.

## Key Design Decisions

- `calcMaterials` uses incremental demand accumulation: top-level targets are force-expanded one level, sub-materials only expand if the user toggles them via `expandedIds`.
- Item names are stored as `{ "zh-CN": "...", "en": "...", "ja": "..." }` objects; `resolveItemName()` handles fallback chain.
- Data files (`items.json`, `recipes.json`, `outfitSetMeta.json`, `outfitSets.json`, and `src/i18n/generated/outfitSetNames.json`) are committed to the repo and auto-updated by CI — no runtime API calls.
- Outfit sets are derived data, not a second upstream source. Detection logic is in `build_outfit_sets.py`; metadata extraction is in `lib/outfit_meta.py`.

## Detailed Docs

- Architecture & data flow: `docs/zh-CN/01-architecture-dataflow.md` (or `docs/en/` for English)
- Module contracts: `docs/zh-CN/02-contracts.md`
- Deployment & data updates: `docs/zh-CN/03-deployment-data.md`
