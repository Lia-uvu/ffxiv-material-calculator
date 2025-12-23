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

  const materials = new Map(); // itemId -> amount
  const crafts = new Map();    // resultItemId -> { recipeId, times }
  const picks = new Map();     // resultItemId -> recipeId
  const warnings = [];

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

    if (inPath.has(itemId)) {
      warnings.push({ kind: "cycle", path: [...path, itemId] });
      addMaterial(itemId, qty);
      return;
    }

    const candidates = recipesByResultId.get(itemId);
    const recipe = pickRecipe(itemId, candidates);

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

    const times = Math.ceil(qty / yieldAmt);

    picks.set(itemId, recipe.id);
    const prev = crafts.get(itemId);
    if (prev && prev.recipeId === recipe.id) {
      prev.times += times;
    } else if (!prev) {
      crafts.set(itemId, { recipeId: recipe.id, times });
    } else {
      prev.times += times;
    }

    path.push(itemId);
    inPath.add(itemId);

    for (const m of recipe.materials || []) {
      need(m.itemId, m.amount * times);
    }

    inPath.delete(itemId);
    path.pop();
  }

  for (const t of targets || []) {
    need(t.id, t.amount);
  }

  return { materials, crafts, picks, warnings };
}
