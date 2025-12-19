export type Target = { itemId: number; amount: number };

export type RecipeMaterial = { itemId: number; amount: number };

export type Recipe = {
  id: number;
  resultItemId: number;
  resultAmount: number;
  job: string;
  itemLevel?: number;
  patch?: string;
  materials: RecipeMaterial[];
};


export type CalcWarning =
  | { kind: "cycle"; path: number[] }
  | { kind: "override-miss"; resultItemId: number; recipeId: number }
  | { kind: "invalid-yield"; recipeId: number; resultItemId: number; resultAmount: number };

export type CalcResult = {
  // 最终“叶子材料”汇总：itemId -> amount
  materials: Map<number, number>;

  // 对每个“被制作的物品”：做了几次（用于将来展示步骤/调试）
  crafts: Map<number, { recipeId: number; times: number }>;

  // 这次计算里每个 resultItemId 最终选中的 recipeId（用于 UI 做“配方覆盖”）
  picks: Map<number, number>;

  warnings: CalcWarning[];
};

export type CalcOptions = {
  targets: Target[];
  recipes: Recipe[];
  // C 模式：少数物品手动覆盖（resultItemId -> recipeId）
  overrides?: Map<number, number>;
};

export function calcMaterials(options: CalcOptions): CalcResult {
  const { targets, recipes, overrides = new Map() } = options;

  // resultItemId -> Recipe[]
  const recipesByResultId = new Map<number, Recipe[]>();
  for (const r of recipes) {
    const list = recipesByResultId.get(r.resultItemId) ?? [];
    list.push(r);
    recipesByResultId.set(r.resultItemId, list);
  }

  const materials = new Map<number, number>();
  const crafts = new Map<number, { recipeId: number; times: number }>();
  const picks = new Map<number, number>();
  const warnings: CalcWarning[] = [];

  const path: number[] = [];
  const inPath = new Set<number>();

  function addMaterial(itemId: number, qty: number) {
    if (qty <= 0) return;
    materials.set(itemId, (materials.get(itemId) ?? 0) + qty);
  }

  function pickRecipe(resultItemId: number, candidates: Recipe[] | undefined): Recipe | null {
    if (!candidates || candidates.length === 0) return null;

    const overrideId = overrides.get(resultItemId);
    if (overrideId != null) {
      const hit = candidates.find((r) => r.id === overrideId);
      if (hit) return hit;
      warnings.push({ kind: "override-miss", resultItemId, recipeId: overrideId });
      // 覆盖没命中就回退默认规则
    }

    // 默认规则（先简单）：拿 candidates[0]
    // 你以后想按职业优先级/最少材料/最低等级等，都在这里改
    return candidates[0];
  }

  function need(itemId: number, qty: number) {
    if (qty <= 0) return;

    // cycle：递归路上再次遇到同一个 itemId → 直接截断为“叶子材料”，避免死循环
    if (inPath.has(itemId)) {
      warnings.push({ kind: "cycle", path: [...path, itemId] });
      addMaterial(itemId, qty);
      return;
    }

    const candidates = recipesByResultId.get(itemId);
    const recipe = pickRecipe(itemId, candidates);

    // 没有 recipe → 当作叶子材料
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

    // 需要做几次（考虑 resultAmount）
    const times = Math.ceil(qty / yieldAmt);

    // 记录 picks & crafts
    picks.set(itemId, recipe.id);
    const prev = crafts.get(itemId);
    if (prev && prev.recipeId === recipe.id) {
      prev.times += times;
    } else if (!prev) {
      crafts.set(itemId, { recipeId: recipe.id, times });
    } else {
      // 理论上同一次计算不该出现（除非你将来做“多路线混合”）
      // 先粗暴合并：保留第一次的 recipeId，times 累加
      prev.times += times;
    }

    // 递归展开
    path.push(itemId);
    inPath.add(itemId);

    for (const m of recipe.materials) {
      need(m.itemId, m.amount * times);
    }

    inPath.delete(itemId);
    path.pop();
  }

  for (const t of targets) {
    need(t.itemId, t.amount);
  }

  return { materials, crafts, picks, warnings };
}
