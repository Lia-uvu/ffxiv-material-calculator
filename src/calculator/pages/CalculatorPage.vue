<template>
  <div>
    <!-- 搜索框 -->
    <div>
      <ItemSearchBar 
				:query="settings.searchQuery" 
				@update:query="setSearchQuery" 
			/>
    </div>
    <!-- 搜索结果 -->
    <div> 
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
      />
    </div>
    <!-- 材料列表 -->
    <div>
      <!-- <MaterialsList
        :entries="materialEntries"
      /> -->
    </div>
  </div>
</template>

<script setup>
import { shallowRef, toRef, computed } from "vue";

import itemsRaw from "../../data/items.json";
import recipesRaw from "../../data/recipes.json";

import ItemSearchBar from "../components/ItemSearchBar.vue";
import ItemSearchResults from "../components/ItemSearchResults.vue";
import TargetItemPanel from "../components/TargetItemPanel.vue";
import MaterialsList from "../components/MaterialsList.vue";

import { useCalculatorSettings } from "../composables/settingStore.js";
import { useItemSearch } from "../composables/useItemSearch.js";
import { useMaterialsList } from "../composables/useMaterialsList";

const items = shallowRef(itemsRaw);

const { settings, targets, setSearchQuery, addTarget, removeTarget } =
  useCalculatorSettings();

const queryRef = toRef(settings, "searchQuery");
const { results } = useItemSearch(items, queryRef, 20);

// id -> item 的索引（给 page 内部用来映射）
const itemById = computed(() => {
  const map = new Map();
  for (const it of items.value) map.set(it.id, it);
  return map;
});

// page 负责把 targets(id[]) 映射成“可展示的数据”
const targetEntries = computed(() => {
  return targets.map((id) => {
    const item = itemById.value.get(id);
    return {
      id,
      name: item?.name ?? "Unknown",
    };
  });
});

// page 负责响应子组件事件，然后调用 store 接口
function selectResultById(id) {
  addTarget(id);
  setSearchQuery(""); // 选中后清空输入（保留你的行为）
}

// const { materialEntries, calcResult } = useMaterialsList({
//   targets: computed(() => settings.targets),          // targets: [{itemId, amount}]
//   overrides: computed(() => settings.recipeOverrides),// Map<resultItemId, recipeId>（先没有也行）
//   items:itemsRaw,
//   recipes:recipesRaw,
// });

</script>