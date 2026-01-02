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
        @remove="removeTarget"
        @update-amount="updateTargetAmount"
      />
    </div>
    <!-- 材料列表 -->
    <div>
      <MaterialsList
        :entries="materialEntries"
      />
    </div>
  </div>
</template>

<script setup>
import { toRef, computed, watchEffect } from "vue";

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
  targets,
  setSearchQuery,
  addTarget,
  removeTarget,
  updateTargetAmount,
} = useSettingStore();


const queryRef = toRef(settings, "searchQuery");
const { results } = useItemSearch(itemsRaw, queryRef, 20);

// id -> item 的索引（给 page 内部用来映射）
const itemById = computed(() => {
  const map = new Map();
  for (const it of itemsRaw) map.set(it.id, it);
  return map;
});

// page 负责把 targets(id[]) 映射成“可展示的数据”
const targetEntries = computed(() => {
  return targets.map((t) => {
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
  addTarget(id);
  setSearchQuery(""); // 选中后清空输入（保留你的行为）
}

const { materialEntries, calcResult } = useMaterialsList({
  targets,     // composable 里会 unref
  items: itemsRaw,
  recipes: recipesRaw,
});



watchEffect(() => {
  console.log("targets =", settings.targets);
  console.log("materials size =", calcResult.value.materials?.size);
  console.log("materials entries =", [...(calcResult.value.materials?.entries?.() ?? [])]);
});
</script>