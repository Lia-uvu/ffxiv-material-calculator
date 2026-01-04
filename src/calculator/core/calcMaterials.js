// calcMaterials.js
import { buildRecipesByResultId, pickRecipe } from "./recipeUtils";

/**
 * options:
 * - targets: Array<{ id: number, amount: number }>
 * - recipes: Array<{ id, resultItemId, resultAmount, materials: Array<{ itemId, amount }> }>
 * - overrides?: Map<resultItemId, recipeId>
 * - expandedIds?: Set<resultItemId>
 *
 * returns:
 * - materials: Map<itemId, amount>   // 当前边界叶子（不可制作 + 未展开可制作）
 * - crafts: Map<resultItemId, { recipeId, times }>
 * - needs: Map<itemId, amount>       // 总需求（含 targets + 中间需求）
 * - rootNeeds: Map<itemId, amount>   // 来自 targets 的那份需求
 * - picks: Map<resultItemId, recipeId>
 * - warnings: Array
 */
export function calcMaterials(options) {
  const {
    targets = [],
    recipes = [],
    overrides = new Map(),
    expandedIds = new Set(),
  } = options ?? {};

  // resultItemId -> Recipe[]
  const recipesByResultId = buildRecipesByResultId(recipes);

  const materials = new Map(); // itemId -> amount（边界叶子：不可制作 + 未展开可制作）
  const crafts = new Map(); // resultItemId -> { recipeId, times }
  const picks = new Map(); // resultItemId -> recipeId
  const warnings = [];
  const needs = new Map(); // itemId -> total required amount
  const rootNeeds = new Map(); // itemId -> amount required by top-level targets only

  const path = [];
  const inPath = new Set();

  function addMaterial(itemId, qty) {
    if (qty <= 0) return;
    materials.set(itemId, (materials.get(itemId) ?? 0) + qty);
  }

  // forceExpand: 只用于“顶层 target 默认展开一层”
  function need(itemId, qty, forceExpand = false) {
    if (qty <= 0) return;

    // cycle guard
    if (inPath.has(itemId)) {
      warnings.push({ kind: "cycle", path: [...path, itemId] });
      addMaterial(itemId, qty);
      return;
    }

    const candidates = recipesByResultId.get(itemId);
    const recipe = pickRecipe(itemId, candidates, overrides, warnings);

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

    // ✅ 关键：不强制展开 && 用户没点锁链 => 当作边界叶子（锁住）
    if (!forceExpand && !expandedIds.has(itemId)) {
      addMaterial(itemId, qty);
      return;
    }

    // no extra crafts needed -> no expansion
    if (deltaTimes <= 0) return;

    // expand only newly required crafts
    path.push(itemId);
    inPath.add(itemId);

    for (const m of recipe.materials || []) {
      // ✅ 递归永远不 forceExpand：保证“默认只展开一层”
      need(m.itemId, m.amount * deltaTimes, false);
    }

    inPath.delete(itemId);
    path.pop();
  }

  // ✅ 顶层 targets：记录 rootNeeds，并 forceExpand=true（默认展开一层）
  for (const t of targets) {
    const id = t?.id;
    const amt = t?.amount ?? 0;
    if (id == null || amt <= 0) continue;

    rootNeeds.set(id, (rootNeeds.get(id) ?? 0) + amt);
    need(id, amt, true);
  }

  return { materials, crafts, needs, rootNeeds, picks, warnings };
}
