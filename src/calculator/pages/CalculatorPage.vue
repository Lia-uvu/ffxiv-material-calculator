<template>
  <div>
    <!-- 搜索框 -->
    <div class="mb-4 rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm relative">
      <ItemSearchBar
        :query="settings.searchQuery"
        @update:query="setSearchQuery"
      />

      <!-- 搜索结果 -->
      <ItemSearchResults
        :results="results"
        @select="selectResultById"
      />
    </div>

    <!-- 成品列表 -->
    <div>
      <TargetItemPanel
      :targets="targetEntries"
      @remove="targetsCtrl.remove"
      @update-amount="targetsCtrl.updateAmount"
      @clear="targetsCtrl.clear"
      />
    </div>

    <!-- 材料列表 -->
    <div>
      <MaterialsList
        :ui="ui"
        @toggle-expand="materialsCtrl.toggle"
        @collapse-all="materialsCtrl.collapseAll"
        @expand-all="handleExpandAll"
      />
    </div>
  </div>
</template>

<script setup>
import { toRef, computed } from "vue";

import itemsRaw from "../../data/items.json";
import recipesRaw from "../../data/recipes.json";

import ItemSearchBar from "../components/ItemSearchBar.vue";
import ItemSearchResults from "../components/ItemSearchResults.vue";
import TargetItemPanel from "../components/TargetItemPanel.vue";
import MaterialsList from "../components/MaterialsList.vue";

import { useSettingStore } from "../composables/settingStore.js";
import { useItemSearch } from "../composables/useItemSearch.js";
import { useMaterialsList } from "../composables/useMaterialsList.js";

const {
  settings,
  setSearchQuery,
  targetsCtrl,
  materialsCtrl, // 锁链要用
} = useSettingStore();

const queryRef = toRef(settings, "searchQuery");
const { results } = useItemSearch(itemsRaw, queryRef, 20);

// id -> item 的索引（给 page 内部用来映射）
const itemById = computed(() => {
  const map = new Map();
  for (const it of itemsRaw) map.set(it.id, it);
  return map;
});

// page 负责把 targets 映射成“可展示的数据”
const targetEntries = computed(() => {
  return targetsCtrl.targets.map((t) => {
    const item = itemById.value.get(t.id);
    return {
      id: t.id,
      amount: t.amount,
      name: item?.name ?? "Unknown",
    };
  });
});

// page 负责响应子组件事件，然后调用 store 接口
function selectResultById(id) {
  targetsCtrl.add(id);
  setSearchQuery(""); // 选中后清空输入（保留你的行为）
}

const { ui, reachableCraftableIds } = useMaterialsList({
  // calcResult是调试接口，要用自己加，记得这个文件👆 return里也加
  targets: targetsCtrl.targets,
  items: itemsRaw,
  recipes: recipesRaw,
  expandedIds: materialsCtrl.expandedIds,
});

function handleExpandAll() {
  materialsCtrl.expandMany([...reachableCraftableIds.value]);
}

// 需要调试时再打开：
// import { watchEffect } from "vue";
// watchEffect(() => {
//   console.log("targets =", targetsCtrl.targets);
//   console.log("materials size =", calcResult.value.materials?.size);
//   console.log("materials entries =", [...(calcResult.value.materials?.entries?.() ?? [])]);
// });
</script>
