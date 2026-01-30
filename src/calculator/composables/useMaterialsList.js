// useMaterialsList.js
import { computed, unref } from "vue";
import { useI18n } from "vue-i18n";
import { resolveItemName } from "../../data";
import { calcMaterials } from "../core/calcMaterials";
import { buildRecipesByResultId, pickRecipe } from "../core/recipeUtils";

export function useMaterialsList(params) {
  const { locale, t } = useI18n();
  const itemsArr = computed(() => unref(params.items) || []);
  const recipesArr = computed(() => unref(params.recipes) || []);
  const targetsArr = computed(() => unref(params.targets) || []);
  const expandedIdsSet = computed(() => unref(params.expandedIds) || new Set());
  const overridesMap = computed(() => (params.overrides ? unref(params.overrides) : new Map()));

  const itemById = computed(() => {
    const map = new Map();
    for (const it of itemsArr.value) map.set(it.id, it);
    return map;
  });

  const recipeById = computed(() => {
    const map = new Map();
    for (const r of recipesArr.value) map.set(r.id, r);
    return map;
  });

  const calcResult = computed(() => {
    return calcMaterials({
      targets: targetsArr.value,
      recipes: recipesArr.value,
      overrides: overridesMap.value,
      expandedIds: expandedIdsSet.value,
    });
  });

  // ✅ 给 page 用：真·拆到底（不依赖 expandedIds）
  const recipesByResultId = computed(() => buildRecipesByResultId(recipesArr.value));

  const reachableCraftableIds = computed(() => {
    const byResult = recipesByResultId.value;
    const overrides = overridesMap.value;

    const reachable = new Set();
    const visiting = new Set();

    function dfs(resultItemId) {
      if (visiting.has(resultItemId)) return;

      const candidates = byResult.get(resultItemId);
      const recipe = pickRecipe(resultItemId, candidates, overrides /* warnings可不传 */);
      if (!recipe) return;

      if (reachable.has(resultItemId)) return;
      reachable.add(resultItemId);

      visiting.add(resultItemId);
      for (const m of recipe.materials || []) dfs(m.itemId);
      visiting.delete(resultItemId);
    }

    for (const target of targetsArr.value) dfs(target.id);
    return reachable;
  });

  const ui = computed(() => {
    const byId = itemById.value;
    const byRecipeId = recipeById.value;
    const expanded = expandedIdsSet.value;
    const currentLocale = locale.value;
    const placeholder = t("common.placeholder");
    const fallbackName = t("common.unknown");

    const { materials, crafts, needs, rootNeeds, picks } = calcResult.value;

    const entryById = new Map();

    function formatObtainMethods(item) {
      const methods = item?.obtainMethods;
      if (!Array.isArray(methods) || methods.length === 0) {
        return item?.source ?? null;
      }

      return methods.filter(Boolean).join(" / ");
    }

    function resolveJob(itemId, fallbackRecipeId) {
      const recipeId = fallbackRecipeId ?? picks?.get?.(itemId) ?? null;
      if (recipeId == null) return null;
      const recipe = byRecipeId.get(recipeId);
      return recipe?.job ?? null;
    }

    // 1) 边界叶子：不可制作 + 未展开可制作
    for (const [id, amount] of (materials?.entries?.() ?? [])) {
      const item = byId.get(id);
      entryById.set(id, {
        id,
        name: resolveItemName(item, currentLocale) ?? fallbackName,
        isCrystal: item?.isCrystal ?? false,

        isCraftable: false,
        isExpanded: false,

        needAmount: amount,
        craftTimes: 0,
        recipeId: null,

        job: resolveJob(id, null),
        source: formatObtainMethods(item) ?? placeholder,
      });
    }

    // 2) craftable：用 taskNeed（总需求 - rootTargets需求）来显示
    for (const [id, info] of (crafts?.entries?.() ?? [])) {
      const totalNeed = needs?.get(id) ?? 0;
      const rootNeed = rootNeeds?.get(id) ?? 0;
      const taskNeed = totalNeed - rootNeed;

      // taskNeed<=0：只来自 targets（顶层成品），不在材料任务里显示
      if (taskNeed <= 0) continue;

      const item = byId.get(id);

      const recipeId = info?.recipeId ?? picks?.get(id) ?? null;
      const recipe = recipeId != null ? byRecipeId.get(recipeId) : null;
      const yieldAmtRaw = recipe?.resultAmount ?? 1;
      const yieldAmt = yieldAmtRaw > 0 ? yieldAmtRaw : 1;
      const taskTimes = Math.ceil(taskNeed / yieldAmt);

      const base = entryById.get(id) ?? {
        id,
        name: resolveItemName(item, currentLocale) ?? fallbackName,
        isCrystal: item?.isCrystal ?? false,

        needAmount: taskNeed,
        craftTimes: taskTimes,
        recipeId,

        job: resolveJob(id, recipeId),
        source: formatObtainMethods(item) ?? placeholder,
      };

      entryById.set(id, {
        ...base,
        isCraftable: true,
        isExpanded: expanded.has(id),
        needAmount: taskNeed,
        craftTimes: taskTimes,
        recipeId,
      });
    }

    const allEntries = [...entryById.values()].map((e) => {
      const displayAmount = e.isCraftable && e.isExpanded ? e.craftTimes : e.needAmount;
      const displaySuffix =
        e.isCraftable && e.isExpanded ? t("materials.craftTimesSuffix") : "";
      return { ...e, displayAmount, displaySuffix };
    });

    const craftable = allEntries
      .filter((e) => e.isCraftable)
      .sort((a, b) => a.name.localeCompare(b.name, currentLocale));

    const nonCraftable = allEntries
      .filter((e) => !e.isCraftable)
      .sort((a, b) => {
        if (a.isCrystal !== b.isCrystal) return a.isCrystal ? -1 : 1;
        return a.name.localeCompare(b.name, currentLocale);
      });

    return { craftable, nonCraftable };
  });

  return { itemById, ui, reachableCraftableIds };
}
