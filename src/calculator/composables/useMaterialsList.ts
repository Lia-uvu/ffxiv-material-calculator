import { computed, unref, type Ref, type ComputedRef } from "vue";
import { calcMaterials, type Recipe, type Target, type CalcResult } from "../core/calcMaterials"; // 或 calcMaterials（看你文件名）

export type Item = {
  id: number;
  name: string;
  isCrystal: boolean;
  obtainMethods: string[];
};

type MaybeRef<T> = T | Ref<T> | ComputedRef<T>;

export function useMaterialsList(params: {
  targets: MaybeRef<Target[]>;
  overrides?: MaybeRef<Map<number, number>>;
  items: MaybeRef<Item[]>;
  recipes: MaybeRef<Recipe[]>;
})
{
  const itemById = computed(() => {
    const map = new Map<number, Item>();
    for (const it of unref(params.items)) map.set(it.id, it);
    return map;
  });

  const calcResult = computed<CalcResult>(() => {
    return calcMaterials({
      targets: unref(params.targets),
      recipes: unref(params.recipes),
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

    // 你想怎么排都行：按名字/按数量/水晶优先……
    entries.sort((a, b) => a.name.localeCompare(b.name));

    return entries;
  });

  return {
    itemById,
    calcResult,       // 有 crafts/picks/warnings，后续做“配方覆盖 UI”会用到
    materialEntries,  // MaterialList 直接吃这个就能渲染
  };
}
