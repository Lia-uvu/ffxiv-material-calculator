// calcMaterials.js

/**
 * options:
 * - targets: Array<{ id: number, amount: number }>
 * - recipes: Array<{
 *     id: number,
 *     resultItemId: number,
 *     resultAmount: number,
 *     materials: Array<{ itemId: number, amount: number }>
 *   }>
 * - overrides?: Map<resultItemId, recipeId>   // optional, internal-use
 *
 * returns:
 * - materials: Map<itemId, amount>                       // leaf materials only
 * - crafts: Map<resultItemId, { recipeId: number, times: number }>
 * - picks: Map<resultItemId, recipeId>
 * - warnings: Array<{ kind: string, ... }>
 */
export function calcMaterials(options) {
  const { targets = [], recipes = [], overrides = new Map() } = options ?? {};

  // resultItemId -> Recipe[]
  const recipesByResultId = new Map();
  for (const r of recipes) {
    const list = recipesByResultId.get(r.resultItemId) ?? [];
    list.push(r);
    recipesByResultId.set(r.resultItemId, list);
  }

  const materials = new Map(); // itemId -> amount (leaf materials)
  const crafts = new Map();    // resultItemId -> { recipeId, times }
  const picks = new Map();     // resultItemId -> recipeId
  const warnings = [];

  // Track total demanded qty per craftable itemId, so we expand only delta crafts.
  const needs = new Map();     // itemId -> total required amount so far

  const path = [];
  const inPath = new Set();

  function addMaterial(itemId, qty) {
    if (qty <= 0) return;
    materials.set(itemId, (materials.get(itemId) ?? 0) + qty);
  }

  function pickRecipe(resultItemId, candidates) {
    if (!candidates || candidates.length === 0) return null;

    const overrideId = overrides.get(resultItemId);
    if (overrideId != null) {
      const hit = candidates.find((r) => r.id === overrideId);
      if (hit) return hit;
      warnings.push({ kind: "override-miss", resultItemId, recipeId: overrideId });
    }

    return candidates[0];
  }

  function need(itemId, qty) {
    if (qty <= 0) return;

    // cycle guard (safety belt)
    if (inPath.has(itemId)) {
      warnings.push({ kind: "cycle", path: [...path, itemId] });
      addMaterial(itemId, qty);
      return;
    }

    const candidates = recipesByResultId.get(itemId);
    const recipe = pickRecipe(itemId, candidates);

    // leaf material (not craftable)
    if (!recipe) {
      addMaterial(itemId, qty);
      return;
    }

    const yieldAmt = recipe.resultAmount ?? 1;
    if (yieldAmt <= 0) {
      warnings.push({
        kind: "invalid-yield",
        recipeId: recipe.id,
        resultItemId: recipe.resultItemId,
        resultAmount: yieldAmt,
      });
      addMaterial(itemId, qty);
      return;
    }

    // accumulate total demand
    const prevNeed = needs.get(itemId) ?? 0;
    const nextNeed = prevNeed + qty;
    needs.set(itemId, nextNeed);

    const prevTimes = crafts.get(itemId)?.times ?? 0;
    const nextTimes = Math.ceil(nextNeed / yieldAmt);
    const deltaTimes = nextTimes - prevTimes;

    // record chosen recipe + total craft times
    picks.set(itemId, recipe.id);
    crafts.set(itemId, { recipeId: recipe.id, times: nextTimes });

    // no extra crafts needed -> no expansion
    if (deltaTimes <= 0) return;

    // expand only newly required crafts
    path.push(itemId);
    inPath.add(itemId);

    for (const m of recipe.materials || []) {
      need(m.itemId, m.amount * deltaTimes);
    }

    inPath.delete(itemId);
    path.pop();
  }

  for (const t of targets) {
    need(t.id, t.amount);
  }

  return { materials, crafts, picks, warnings };
}
