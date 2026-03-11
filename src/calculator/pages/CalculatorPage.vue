<template>
  <div class="space-y-4">
    <!-- 搜索框 -->
    <div class="relative" ref="searchContainerRef">
      <ItemSearchBar
        :query="settings.searchQuery"
        @update:query="setSearchQuery"
      />

      <!-- 空状态提示：未输入时可见 -->
      <p v-if="!settings.searchQuery" class="mt-1.5 px-1 text-xs text-[#9B96AD]">
        {{ t('search.hintCtrl') }}
      </p>

      <!-- 搜索结果 -->
      <ItemSearchResults
        :results="results"
        :target-amounts="targetAmountsMap"
        @select="selectResultById"
      />
    </div>

    <!-- 成品列表 -->
    <TargetItemPanel
      :targets="targetEntries"
      @remove="targetsCtrl.remove"
      @update-amount="targetsCtrl.updateAmount"
      @clear="targetsCtrl.clear"
    />

    <!-- 材料列表 -->
    <MaterialsList
      :ui="ui"
      :checked-ids="materialsCtrl.checkedIds"
      :expand-order="materialsCtrl.expandedOrder"
      :copy-success="copySuccess"
      @toggle-expand="materialsCtrl.toggle"
      @collapse-all="materialsCtrl.collapseAll"
      @expand-all="handleExpandAll"
      @toggle-check="materialsCtrl.toggleCheck"
      @clear-checked="materialsCtrl.clearChecked"
      @reset-materials="materialsCtrl.resetMaterials"
      @copy-materials="handleCopyMaterials"
    />
  </div>
</template>

<script setup>
import { toRef, computed, ref, onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";

import { items as itemsRaw, recipes as recipesRaw, resolveItemName } from "../../data";

import ItemSearchBar from "../components/ItemSearchBar.vue";
import ItemSearchResults from "../components/ItemSearchResults.vue";
import TargetItemPanel from "../components/TargetItemPanel.vue";
import MaterialsList from "../components/MaterialsList.vue";

import { useSettingStore } from "../composables/settingStore.js";
import { useItemSearch } from "../composables/useItemSearch.js";
import { useMaterialsList } from "../composables/useMaterialsList.js";
import { useMaterialsExport } from "../composables/useMaterialsExport.js";

const {
  settings,
  setSearchQuery,
  targetsCtrl,
  materialsCtrl,
} = useSettingStore();

const { locale, t } = useI18n();

const queryRef = toRef(settings, "searchQuery");
const { results } = useItemSearch(itemsRaw, queryRef, 20);

const itemById = computed(() => {
  const map = new Map();
  for (const it of itemsRaw) map.set(it.id, it);
  return map;
});

const targetEntries = computed(() => {
  return targetsCtrl.targets.map((target) => {
    const item = itemById.value.get(target.id);
    return {
      id: target.id,
      amount: target.amount,
      name: resolveItemName(item, locale.value) ?? t("common.unknown"),
    };
  });
});

/** Map<itemId, amount> 用于在搜索结果中显示已添加数量角标 */
const targetAmountsMap = computed(() => {
  const map = new Map();
  for (const tgt of targetsCtrl.targets) map.set(tgt.id, tgt.amount);
  return map;
});

const searchContainerRef = ref(null);

function onDocumentClick(e) {
  if (!settings.searchQuery) return;
  if (searchContainerRef.value?.contains(e.target)) return;
  setSearchQuery("");
}

onMounted(() => document.addEventListener("click", onDocumentClick));
onUnmounted(() => document.removeEventListener("click", onDocumentClick));

function selectResultById({ id, ctrlKey }) {
  targetsCtrl.add(id);
  if (!ctrlKey) setSearchQuery("");
}

const { ui, reachableCraftableIds } = useMaterialsList({
  targets: targetsCtrl.targets,
  items: itemsRaw,
  recipes: recipesRaw,
  expandedIds: materialsCtrl.expandedIds,
});
const { exportText } = useMaterialsExport(ui);

const copySuccess = ref(false);
let copyTimer = null;

function handleExpandAll() {
  materialsCtrl.expandMany([...reachableCraftableIds.value]);
}

function fallbackCopy(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "readonly");
  textarea.style.position = "absolute";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}

async function handleCopyMaterials() {
  const text = exportText.value?.trim();
  if (!text) return;
  let copied = false;

  if (navigator?.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      copied = true;
    } catch (error) {
      fallbackCopy(text);
      copied = true;
    }
  } else {
    fallbackCopy(text);
    copied = true;
  }

  if (copied) showCopySuccess();
}

function showCopySuccess() {
  copySuccess.value = true;
  if (copyTimer) window.clearTimeout(copyTimer);
  copyTimer = window.setTimeout(() => {
    copySuccess.value = false;
  }, 2000);
}
</script>
