<template>
  <LoadingState v-if="!dataReady" />
  <div v-else class="space-y-4">
    <SearchPanel
      :query="settings.searchQuery"
      :results="results"
      :target-amounts="targetAmountsMap"
      @update:query="setSearchQuery"
      @select="selectResultById"
    />

    <OutfitSetPanel
      :sets="outfitSets"
      @add-set="addSetToTargets"
    />

    <TargetItemPanel
      :targets="targetEntries"
      @remove="targetsCtrl.remove"
      @update-amount="targetsCtrl.updateAmount"
      @clear="targetsCtrl.clear"
    />

    <MaterialsPanel
      :ui="ui"
      :checked-ids="materialsCtrl.checkedIds"
      :expand-order="materialsCtrl.expandOrder"
      :export-text="exportText"
      @toggle-expand="materialsCtrl.toggle"
      @collapse-all="materialsCtrl.collapseAll"
      @expand-all="handleExpandAll"
      @toggle-check="materialsCtrl.toggleCheck"
      @reset-materials="materialsCtrl.resetMaterials"
    />
  </div>
</template>

<script setup>
import { toRef, computed } from "vue";
import { useI18n } from "vue-i18n";

import { items, recipes, outfitSets, resolveItemName, dataReady, loadData } from "../../data";

import LoadingState from "../components/common/LoadingState.vue";
import OutfitSetPanel from "../components/search/OutfitSetPanel.vue";
import SearchPanel from "../components/search/SearchPanel.vue";
import TargetItemPanel from "../components/targets/TargetItemPanel.vue";
import MaterialsPanel from "../components/materials/MaterialsPanel.vue";

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

loadData();

const queryRef = toRef(settings, "searchQuery");
const { results } = useItemSearch(items, queryRef, 20);

const itemById = computed(() => {
  const map = new Map();
  for (const item of items.value) map.set(item.id, item);
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

const targetAmountsMap = computed(() => {
  const map = new Map();
  for (const target of targetsCtrl.targets) map.set(target.id, target.amount);
  return map;
});

function selectResultById({ id, keepOpen }) {
  targetsCtrl.add(id);
  if (!keepOpen) setSearchQuery("");
}

function addSetToTargets(itemIds) {
  for (const id of itemIds) {
    targetsCtrl.add(id);
  }
}

const { ui, reachableCraftableIds } = useMaterialsList({
  targets: targetsCtrl.targets,
  items,
  recipes,
  expandedIds: materialsCtrl.expandedIds,
});
const { exportText } = useMaterialsExport(ui);

function handleExpandAll() {
  materialsCtrl.expandMany([...reachableCraftableIds.value]);
}
</script>
