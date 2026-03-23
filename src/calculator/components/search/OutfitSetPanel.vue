<template>
  <div>
    <button
      type="button"
      class="mt-1.5 flex w-full items-center gap-1.5 px-1 text-xs text-[#9B96AD] hover:text-[#B4A5C8] transition-colors"
      @click="expanded = !expanded"
    >
      <ChevronRight
        :size="12"
        class="shrink-0 transition-transform duration-150"
        :class="{ 'rotate-90': expanded }"
      />
      {{ t("outfitSets.title") }}
    </button>

    <div v-if="expanded" class="mt-2 rounded-xl border border-[#38364A] bg-[#252430] p-3 shadow-[0_2px_10px_rgba(0,0,0,0.4)]">
      <!-- Tier level -->
      <div v-for="tier in tiers" :key="tier.level" class="mb-2 last:mb-0">
        <button
          type="button"
          class="mb-1 flex w-full items-center gap-1.5 text-xs font-medium text-[#B4A5C8] hover:text-[#EDE9F7] transition-colors"
          @click="toggleTier(tier.level)"
        >
          <ChevronRight
            :size="11"
            class="shrink-0 transition-transform duration-150"
            :class="{ 'rotate-90': expandedTiers.has(tier.level) }"
          />
          {{ tier.label }}
          <span class="text-[#6B677A]">({{ tier.sets.length }})</span>
        </button>

        <div v-if="expandedTiers.has(tier.level)" class="ml-4 space-y-1.5">
          <!-- Set name + ilvl -->
          <div v-for="set in tier.sets" :key="set.key">
            <button
              type="button"
              class="flex w-full items-center gap-1.5 text-xs transition-colors"
              :class="selectedSetKey === set.key
                ? 'text-[#EDE9F7]'
                : 'text-[#9B96AD] hover:text-[#EDE9F7]'"
              @click="toggleSet(set.key)"
            >
              <ChevronRight
                :size="10"
                class="shrink-0 transition-transform duration-150"
                :class="{ 'rotate-90': selectedSetKey === set.key }"
              />
              <span>{{ t("outfitSets.set." + set.key) }}</span>
              <span class="text-[#6B677A]">ilvl {{ set.ilvl }}</span>
            </button>

            <!-- Job buttons grouped by role -->
            <div v-if="selectedSetKey === set.key" class="mt-1 ml-4 space-y-1">
              <div v-for="group in jobGroupsForSet(set)" :key="group.role" class="flex flex-wrap items-center gap-1">
                <span class="w-14 shrink-0 text-[10px] text-[#6B677A]">{{ group.label }}</span>
                <button
                  v-for="job in group.jobs"
                  :key="job.key"
                  type="button"
                  class="rounded-md border border-[#38364A] bg-[#2D2C34] px-1.5 py-0.5 text-[11px] text-[#9B96AD] transition-colors hover:border-[#B4A5C8]/40 hover:bg-[#3B3A47] hover:text-[#EDE9F7]"
                  @click.stop="addJobItems(set, group.itemIds, job.key)"
                >
                  {{ t("jobs." + job.key) }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { ChevronRight } from "lucide-vue-next";

const props = defineProps({
  sets: { type: Array, default: () => [] },
});

const emit = defineEmits(["add-set"]);
const { t } = useI18n();

const expanded = ref(false);
const expandedTiers = ref(new Set());
const selectedSetKey = ref(null);

const TIER_LABELS = {
  100: "Lv.100 — 7.x",
  90: "Lv.90 — 6.x",
  80: "Lv.80 — 5.x",
  70: "Lv.70 — 4.x",
};

// Role key → { label, jobs: [{ key }] }
const ROLE_JOBS = {
  tank: { label: "Tank", jobs: [
    { key: "PLD" }, { key: "WAR" }, { key: "DRK" }, { key: "GNB" },
  ]},
  healer: { label: "Healer", jobs: [
    { key: "WHM" }, { key: "SCH" }, { key: "AST" }, { key: "SGE" },
  ]},
  maiming: { label: "Maiming", jobs: [
    { key: "DRG" }, { key: "RPR" },
  ]},
  striking: { label: "Striking", jobs: [
    { key: "MNK" }, { key: "SAM" },
  ]},
  scouting: { label: "Scouting", jobs: [
    { key: "NIN" }, { key: "VPR" },
  ]},
  aiming: { label: "Aiming", jobs: [
    { key: "BRD" }, { key: "MCH" }, { key: "DNC" },
  ]},
  casting: { label: "Casting", jobs: [
    { key: "BLM" }, { key: "SMN" }, { key: "RDM" }, { key: "PCT" },
  ]},
  crafter: { label: "Crafter", jobs: [
    { key: "CRP" }, { key: "BSM" }, { key: "ARM" }, { key: "GSM" },
    { key: "LTW" }, { key: "WVR" }, { key: "ALC" }, { key: "CUL" },
  ]},
  gatherer: { label: "Gatherer", jobs: [
    { key: "MIN" }, { key: "BTN" }, { key: "FSH" },
  ]},
};

const tiers = computed(() => {
  const grouped = new Map();
  for (const set of props.sets) {
    const lvl = set.crafterLevel;
    if (!grouped.has(lvl)) grouped.set(lvl, []);
    grouped.get(lvl).push(set);
  }
  return [...grouped.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([level, sets]) => ({
      level,
      label: TIER_LABELS[level] || `Lv.${level}`,
      sets,
    }));
});

function jobGroupsForSet(set) {
  const groups = [];
  for (const [role, itemIds] of Object.entries(set.roles)) {
    const meta = ROLE_JOBS[role];
    if (!meta) continue;
    groups.push({
      role,
      label: meta.label,
      jobs: meta.jobs,
      itemIds,
    });
  }
  return groups;
}

function toggleTier(level) {
  const next = new Set(expandedTiers.value);
  if (next.has(level)) {
    next.delete(level);
    selectedSetKey.value = null;
  } else {
    next.add(level);
  }
  expandedTiers.value = next;
}

function toggleSet(key) {
  selectedSetKey.value = selectedSetKey.value === key ? null : key;
}

function addJobItems(set, roleItemIds, jobKey) {
  const weaponIds = (set.weapons && set.weapons[jobKey]) || [];
  emit("add-set", [...roleItemIds, ...weaponIds]);
}
</script>
