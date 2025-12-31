import { computed, unref } from "vue";
import { calcMaterials } from "../core/calcMaterials";

/**
 * JS 版 useMaterialsList
 * - 支持 params.targets/items/recipes/overrides 传 ref / computed / 普通值
 * - 返回 itemById / calcResult / materialEntries
 * - 新增：sourcesBreakdowns（给小 i 弹层）/ childrenByParentId（给树模式）
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
      overrides: params.overrides ? unref(params.overrides) : new Map(),
    });
  });

  // 兼容：如果 core 还没加 sources，就当空
  const sources = computed(() => {
    return calcResult.value.sources ?? new Map();
  });

  // 给“列表模式小 i”用：materialId -> [{ parentId, parentName, amount }]
  const sourcesBreakdowns = computed(() => {
    const byId = itemById.value;
    const out = new Map();

    for (const [childId, byParent] of sources.value.entries()) {
      const rows = [];
      for (const [parentId, amount] of byParent.entries()) {
        const parent = byId.get(parentId);
        rows.push({
          parentId,
          parentName: parent?.name ?? "Unknown",
          amount,
        });
      }
      // 你要“合并后显示一次最终合计”——这里就是合并后的结果
      // 顺便排序一下，弹层里更好看
      rows.sort((a, b) => b.amount - a.amount);
      out.set(childId, rows);
    }

    return out;
  });

  // 给“树模式”用：parentId -> [{ childId, childName, amount }]
  // 这是把 sources 的 child->parent 反过来，树渲染会顺手很多
  const childrenByParentId = computed(() => {
    const byId = itemById.value;
    const out = new Map();

    for (const [childId, byParent] of sources.value.entries()) {
      const child = byId.get(childId);
      for (const [parentId, amount] of byParent.entries()) {
        const list = out.get(parentId) ?? [];
        list.push({
          childId,
          childName: child?.name ?? "Unknown",
          amount,
        });
        out.set(parentId, list);
      }
    }

    // 可选：每个 parent 的 children 也排一下序（数量多的在前）
    for (const [parentId, list] of out.entries()) {
      list.sort((a, b) => b.amount - a.amount);
      out.set(parentId, list);
    }

    return out;
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
        // 给列表模式一个“是否有来源信息”的标记，小 i 用得上
        hasBreakdown: sourcesBreakdowns.value.has(id),
      };
    });

    entries.sort((a, b) => a.name.localeCompare(b.name));
    return entries;
  });

  // 小工具：组件用起来更舒服（可选）
  function getMaterialBreakdownRows(materialId) {
    return sourcesBreakdowns.value.get(materialId) ?? [];
  }

  function getChildrenRows(parentId) {
    return childrenByParentId.value.get(parentId) ?? [];
  }

  return {
    itemById,
    calcResult,
    materialEntries,

    // 新增：列表弹层 + 树模式
    sourcesBreakdowns,
    childrenByParentId,
    getMaterialBreakdownRows,
    getChildrenRows,
  };
}
