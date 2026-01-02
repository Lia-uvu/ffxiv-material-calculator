// useMaterialsList.js
import { computed, unref } from "vue";
import { calcMaterials } from "../core/calcMaterials";

/**
 * JS 版 useMaterialsList（MVP）
 * - 支持 params.targets/items/recipes 传 ref / computed / 普通值
 * - 返回 itemById / calcResult / materialEntries
 */
export function useMaterialsList(params) {
  const itemById = computed(() => {
    const map = new Map();
    for (const it of unref(params.items) || []) map.set(it.id, it);
    return map;
  });

  const calcResult = computed(() => {
    return calcMaterials({
      targets: unref(params.targets) || [],
      recipes: unref(params.recipes) || [],
      // overrides 保留在 core 内部可用，但外部 MVP 不主动依赖它
      overrides: params.overrides ? unref(params.overrides) : new Map(),
    });
  });

  const materialEntries = computed(() => {
    const byId = itemById.value;

    const entries = [...calcResult.value.materials.entries()].map(([id, amount]) => {
      const item = byId.get(id);
      return {
        id,
        amount,
        name: item?.name ?? "Unknown",
        isCrystal: item?.isCrystal ?? false,
      };
    });

    entries.sort((a, b) => a.name.localeCompare(b.name));
    return entries;
  });

  return {
    itemById,
    calcResult,
    materialEntries,
  };
}
