// core/recipeUtils.js

export function buildRecipesByResultId(recipes = []) {
  const map = new Map();
  for (const r of recipes || []) {
    const list = map.get(r.resultItemId) ?? [];
    list.push(r);
    map.set(r.resultItemId, list);
  }
  return map;
}

/**
 * 选择配方：override 优先，否则 candidates[0]
 * warnings 可选：如果 override miss，则 push 一条
 */
export function pickRecipe(resultItemId, candidates, overrides = new Map(), warnings) {
  if (!candidates || candidates.length === 0) return null;

  const overrideId = overrides?.get?.(resultItemId);
  if (overrideId != null) {
    const hit = candidates.find((r) => r.id === overrideId);
    if (hit) return hit;
    if (warnings) warnings.push({ kind: "override-miss", resultItemId, recipeId: overrideId });
  }

  return candidates[0];
}
