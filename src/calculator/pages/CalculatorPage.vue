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
      @add-set="addSetBundle"
    />

    <TargetItemPanel
      :targets="targetEntries"
      :outfit-bundles="outfitBundleEntries"
      @remove="targetsCtrl.remove"
      @update-amount="targetsCtrl.updateAmount"
      @clear="handleClear"
      @remove-bundle="outfitTargetsCtrl.remove"
      @update-bundle-amount="outfitTargetsCtrl.updateAmount"
      @toggle-bundle-expand="outfitTargetsCtrl.toggleExpanded"
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
  outfitTargetsCtrl,
  materialsCtrl,
} = useSettingStore();

const { locale, t, te } = useI18n();

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

const outfitSetByKey = computed(() => {
  const map = new Map();
  for (const set of outfitSets.value) map.set(set.key, set);
  return map;
});

/** Outfit bundles enriched with resolved item names for display */
const outfitBundleEntries = computed(() => {
  return outfitTargetsCtrl.outfitTargets.map((bundle) => {
    const set = outfitSetByKey.value.get(bundle.setKey);
    const roleKey = bundle.roleKey ?? inferOutfitRoleKey(set, bundle.itemIds);
    const roleLabel = roleKey && te("outfitSets.roles." + roleKey)
      ? t("outfitSets.roles." + roleKey)
      : "";
    const baseSetLabel = t("outfitSets.set." + bundle.setKey);
    const effectiveItemIds = [
      ...(bundle.includeWeapon ? bundle.weaponIds : []),
      ...bundle.itemIds,
    ];
    const weaponIdSet = new Set(bundle.weaponIds);

    const items_ = effectiveItemIds.map((id) => {
      const item = itemById.value.get(id);
      return {
        id,
        name: resolveItemName(item, locale.value) ?? t("common.unknown"),
        isWeapon: weaponIdSet.has(id),
      };
    });

    return {
      uid: bundle.uid,
      setLabel: roleLabel ? t("outfitSets.setWithRole", { set: baseSetLabel, role: roleLabel }) : baseSetLabel,
      ilvl: set?.ilvl ?? bundle.tierLevel,
      jobLabel: te("jobs." + bundle.jobKey) ? t("jobs." + bundle.jobKey) : bundle.jobKey,
      amount: bundle.amount ?? 1,
      expanded: bundle.expanded,
      itemCount: effectiveItemIds.length,
      items: items_,
    };
  });
});

function inferOutfitRoleKey(set, itemIds) {
  if (!set?.roles) return null;
  for (const [roleKey, roleItemIds] of Object.entries(set.roles)) {
    if (sameNumberList(roleItemIds, itemIds)) return roleKey;
  }
  return null;
}

function sameNumberList(a, b) {
  if (!a || !b || a.length !== b.length) return false;
  for (let i = 0; i < a.length; i += 1) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}

/** Combined targets for materials calculation: individual + outfit bundle items */
const combinedTargets = computed(() => {
  const totals = new Map();

  for (const t of targetsCtrl.targets) {
    totals.set(t.id, (totals.get(t.id) ?? 0) + t.amount);
  }

  for (const bundle of outfitTargetsCtrl.outfitTargets) {
    const ids = [
      ...bundle.itemIds,
      ...(bundle.includeWeapon ? bundle.weaponIds : []),
    ];
    const amount = bundle.amount ?? 1;
    for (const id of ids) {
      totals.set(id, (totals.get(id) ?? 0) + amount);
    }
  }

  return [...totals.entries()].map(([id, amount]) => ({ id, amount }));
});

function selectResultById({ id, keepOpen }) {
  targetsCtrl.add(id);
  if (!keepOpen) setSearchQuery("");
}

function addSetBundle({ setKey, tierLevel, roleKey, jobKey, itemIds, weaponIds }) {
  outfitTargetsCtrl.add({ setKey, tierLevel, roleKey, jobKey, itemIds, weaponIds });
}

function handleClear() {
  targetsCtrl.clear();
  outfitTargetsCtrl.clear();
}

const { ui, reachableCraftableIds } = useMaterialsList({
  targets: combinedTargets,
  items,
  recipes,
  expandedIds: materialsCtrl.expandedIds,
});
const { exportText } = useMaterialsExport(ui);

function handleExpandAll() {
  materialsCtrl.expandMany([...reachableCraftableIds.value]);
}
</script>
