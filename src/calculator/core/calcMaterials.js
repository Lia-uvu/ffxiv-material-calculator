// calcMaterials.js

/**
 * options:
 * - targets: Array<{ id: number, amount: number }>
 * - recipes: Array<{
 *     id: number,
 *     resultItemId: number,
 *     resultAmount: number,
 *     job: string,
 *     itemLevel?: number,
 *     patch?: string,
 *     materials: Array<{ itemId: number, amount: number }>
 *   }>
 * - overrides?: Map<resultItemId, recipeId>
 */
export function calcMaterials(options) {
  const { targets, recipes, overrides = new Map() } = options;

  // resultItemId -> Recipe[]
  const recipesByResultId = new Map();
  for (const r of recipes || []) {
    const list = recipesByResultId.get(r.resultItemId) ?? [];
    list.push(r);
    recipesByResultId.set(r.resultItemId, list);
  }

  const materials = new Map(); // itemId -> amount (leaf materials)
  const crafts = new Map();    // resultItemId -> { recipeId, times }
  const picks = new Map();     // resultItemId -> recipeId
  const warnings = [];

  // NEW: childItemId -> Map<parentItemId, amount>
  const sources = new Map();

  // NEW: track total demanded qty per itemId (for correct ceil + delta expansion)
  const needs = new Map();

  const path = [];
  const inPath = new Set();

  function addMaterial(itemId, qty) {
    if (qty <= 0) return;
    materials.set(itemId, (materials.get(itemId) ?? 0) + qty);
  }

  function addSource(childItemId, parentItemId, qty) {
    if (qty <= 0) return;
    let byParent = sources.get(childItemId);
    if (!byParent) {
      byParent = new Map();
      sources.set(childItemId, byParent);
    }
    byParent.set(parentItemId, (byParent.get(parentItemId) ?? 0) + qty);
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

  // NOTE: parentItemId is used only for sources tracking (direct parent)
  function need(itemId, qty, parentItemId = null) {
    if (qty <= 0) return;

    // record direct parent contribution (optional for roots)
    if (parentItemId != null) {
      addSource(itemId, parentItemId, qty);
    }

    // cycle guard (still needed as safety belt)
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

    // accumulate total demand first
    const prevNeed = needs.get(itemId) ?? 0;
    const nextNeed = prevNeed + qty;
    needs.set(itemId, nextNeed);

    const prevCraft = crafts.get(itemId);
    const prevTimes = prevCraft?.times ?? 0;

    const nextTimes = Math.ceil(nextNeed / yieldAmt);
    const deltaTimes = nextTimes - prevTimes;

    // record pick + crafts using the TOTAL times
    picks.set(itemId, recipe.id);
    crafts.set(itemId, { recipeId: recipe.id, times: nextTimes });

    // If this call doesn't increase required craft times, do NOT expand materials again.
    if (deltaTimes <= 0) return;

    // Only expand newly required crafts (deltaTimes) to avoid repeated ceil explosion
    path.push(itemId);
    inPath.add(itemId);

    for (const m of recipe.materials || []) {
      need(m.itemId, m.amount * deltaTimes, itemId);
    }

    inPath.delete(itemId);
    path.pop();
  }

  for (const t of targets || []) {
    need(t.id, t.amount, null);
  }

  return { materials, crafts, picks, warnings, sources };
}
