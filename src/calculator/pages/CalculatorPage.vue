<template>
  <div style="display: grid; gap: 12px; max-width: 520px;">
    <ItemSearchBar :query="settings.searchQuery" @update:query="setSearchQuery" />

    <!-- 搜索结果 -->
    <div>
      <div style="margin-bottom: 6px;">Search results</div>
      <ul>
        <li v-for="it in results" :key="it.id">
          <button @click="selectResult(it)">
            {{ it.name }} ({{ it.id }})
          </button>
        </li>
      </ul>
    </div>

    <!-- 成品列表（暂时简陋版） -->
    <div>
      <div style="margin-bottom: 6px;">Targets</div>
      <ul>
        <li v-for="id in targets" :key="id">
          {{ itemById.get(id)?.name ?? "Unknown" }} ({{ id }})
          <button @click="removeTarget(id)">remove</button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { shallowRef, toRef, computed } from "vue";

import itemsRaw from "../../data/items.json";

import ItemSearchBar from "../components/ItemSearchBar.vue";
import { useCalculatorSettings } from "../composables/settingStore.js";
import { useItemSearch } from "../composables/useItemSearch.js";

const items = shallowRef(itemsRaw);

const { settings, targets, setSearchQuery, addTarget, removeTarget } =
  useCalculatorSettings();

const queryRef = toRef(settings, "searchQuery");
const { results } = useItemSearch(items, queryRef, 20);

// 方便把 targets(id[]) 映射成可显示的条目
const itemById = computed(() => {
  const map = new Map();
  for (const it of items.value) map.set(it.id, it);
  return map;
});

function selectResult(item) {
  addTarget(item.id);
  setSearchQuery(""); // 选中后清空输入（你也可以不清空）
}
</script>
