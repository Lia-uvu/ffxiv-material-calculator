<template>
  <div class="overflow-hidden rounded-xl border border-[#38364A] bg-[#252430] shadow-[0_2px_10px_rgba(0,0,0,0.35)]">
    <!-- Tab corner: always-visible strip -->
    <button
      type="button"
      class="flex w-full items-center gap-2 px-3 py-2 text-left transition-colors hover:bg-[#2D2C34]"
      @click="togglePanel"
    >
      <span class="text-xs font-medium text-[#9B96AD]">{{ t("outfitSets.title") }}</span>
      <ChevronUp
        :size="13"
        class="ml-auto shrink-0 text-[#6B677A] transition-transform duration-200"
        :class="panelOpen ? 'rotate-180' : 'animate-hint-up'"
      />
    </button>

    <!-- Expandable content: "pulled out" reveal -->
    <Transition name="outfit-reveal">
      <div v-if="panelOpen" class="border-t border-[#38364A]">
        <!-- Breadcrumb nav -->
        <nav
          v-if="selectedTierLevel !== null"
          class="flex flex-wrap items-center gap-x-1 gap-y-0.5 border-b border-[#2D2C34] px-3 py-1.5"
          aria-label="outfit set navigation"
        >
          <button
            type="button"
            class="text-[11px] text-[#9B96AD] transition-colors hover:text-[#B4A5C8]"
            @click="resetToRoot"
          >
            {{ t("outfitSets.title") }}
          </button>
          <ChevronRight :size="9" class="shrink-0 text-[#4A4858]" />
          <template v-if="selectedSetKey === null">
            <span class="text-[11px] text-[#EDE9F7]">{{ currentTierLabel }}</span>
          </template>
          <template v-else>
            <button
              type="button"
              class="text-[11px] text-[#9B96AD] transition-colors hover:text-[#B4A5C8]"
              @click="resetToTier"
            >
              {{ currentTierLabel }}
            </button>
            <ChevronRight :size="9" class="shrink-0 text-[#4A4858]" />
            <span class="text-[11px] text-[#EDE9F7]">{{ currentSetLabel }}</span>
          </template>
        </nav>

        <div class="p-3">
          <!-- Level 0: tier list -->
          <div v-if="selectedTierLevel === null" class="space-y-0.5">
            <button
              v-for="tier in tiers"
              :key="tier.level"
              type="button"
              class="flex w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-xs text-[#9B96AD] transition-colors hover:bg-[#2D2C34] hover:text-[#EDE9F7]"
              @click="selectTier(tier.level)"
            >
              <span class="font-medium">{{ tier.label }}</span>
              <span class="text-[#6B677A]">({{ tier.sets.length }})</span>
              <ChevronRight :size="10" class="ml-auto shrink-0 text-[#4A4858]" />
            </button>
          </div>

          <!-- Level 1: set list for selected tier -->
          <div v-else-if="selectedSetKey === null" class="space-y-0.5">
            <button
              v-for="set in currentTierSets"
              :key="set.key"
              type="button"
              class="flex w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-xs text-[#9B96AD] transition-colors hover:bg-[#2D2C34] hover:text-[#EDE9F7]"
              @click="selectedSetKey = set.key"
            >
              <span>{{ t("outfitSets.set." + set.key) }}</span>
              <span class="text-[#6B677A]">ilvl {{ set.ilvl }}</span>
              <ChevronRight :size="10" class="ml-auto shrink-0 text-[#4A4858]" />
            </button>
          </div>

          <!-- Level 2: job groups for selected set -->
          <div v-else class="space-y-2">
            <div
              v-for="group in currentJobGroups"
              :key="group.role"
              class="flex flex-wrap items-center gap-1"
            >
              <span class="w-14 shrink-0 text-[10px] text-[#6B677A]">{{ group.label }}</span>
              <button
                v-for="job in group.jobs"
                :key="job.key"
                type="button"
                class="rounded-md border border-[#38364A] bg-[#2D2C34] px-1.5 py-0.5 text-[11px] text-[#9B96AD] transition-colors hover:border-[#B4A5C8]/40 hover:bg-[#3B3A47] hover:text-[#EDE9F7]"
                @click="addJobItems(job.key)"
              >
                {{ t("jobs." + job.key) }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { ChevronRight, ChevronUp } from "lucide-vue-next";

const props = defineProps({
  sets: { type: Array, default: () => [] },
});

const emit = defineEmits(["add-set"]);
const { t } = useI18n();

const panelOpen = ref(false);
const selectedTierLevel = ref(null);
const selectedSetKey = ref(null);

const TIER_LABELS = {
  100: "Lv.100 — 7.x",
  90: "Lv.90 — 6.x",
  80: "Lv.80 — 5.x",
  70: "Lv.70 — 4.x",
};

const ROLE_JOBS = {
  tank:     { label: "Tank",    jobs: [{ key: "PLD" }, { key: "WAR" }, { key: "DRK" }, { key: "GNB" }] },
  healer:   { label: "Healer",  jobs: [{ key: "WHM" }, { key: "SCH" }, { key: "AST" }, { key: "SGE" }] },
  maiming:  { label: "Maiming", jobs: [{ key: "DRG" }, { key: "RPR" }] },
  striking: { label: "Striking",jobs: [{ key: "MNK" }, { key: "SAM" }] },
  scouting: { label: "Scouting",jobs: [{ key: "NIN" }, { key: "VPR" }] },
  aiming:   { label: "Aiming",  jobs: [{ key: "BRD" }, { key: "MCH" }, { key: "DNC" }] },
  casting:  { label: "Casting", jobs: [{ key: "BLM" }, { key: "SMN" }, { key: "RDM" }, { key: "PCT" }] },
  crafter:  { label: "Crafter", jobs: [{ key: "CRP" }, { key: "BSM" }, { key: "ARM" }, { key: "GSM" }, { key: "LTW" }, { key: "WVR" }, { key: "ALC" }, { key: "CUL" }] },
  gatherer: { label: "Gatherer",jobs: [{ key: "MIN" }, { key: "BTN" }, { key: "FSH" }] },
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

const currentTierLabel = computed(
  () => TIER_LABELS[selectedTierLevel.value] || `Lv.${selectedTierLevel.value}`
);

const currentTierSets = computed(() => {
  if (selectedTierLevel.value === null) return [];
  return tiers.value.find((t) => t.level === selectedTierLevel.value)?.sets ?? [];
});

const currentSet = computed(() =>
  selectedSetKey.value
    ? currentTierSets.value.find((s) => s.key === selectedSetKey.value) ?? null
    : null
);

const currentSetLabel = computed(() =>
  currentSet.value ? t("outfitSets.set." + currentSet.value.key) : ""
);

const currentJobGroups = computed(() => {
  if (!currentSet.value) return [];
  return Object.entries(currentSet.value.roles).flatMap(([role, itemIds]) => {
    const meta = ROLE_JOBS[role];
    if (!meta) return [];
    return [{ role, label: meta.label, jobs: meta.jobs, itemIds }];
  });
});

function togglePanel() {
  if (panelOpen.value) {
    panelOpen.value = false;
    selectedTierLevel.value = null;
    selectedSetKey.value = null;
  } else {
    panelOpen.value = true;
  }
}

function selectTier(level) {
  selectedTierLevel.value = level;
  selectedSetKey.value = null;
}

function resetToRoot() {
  selectedTierLevel.value = null;
  selectedSetKey.value = null;
}

function resetToTier() {
  selectedSetKey.value = null;
}

function addJobItems(jobKey) {
  if (!currentSet.value) return;
  const group = currentJobGroups.value.find((g) => g.jobs.some((j) => j.key === jobKey));
  const weaponIds = currentSet.value.weapons?.[jobKey] || [];
  emit("add-set", [...(group?.itemIds ?? []), ...weaponIds]);
}
</script>

<style scoped>
/* Gentle upward hint bounce when panel is closed */
@keyframes hint-up {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}
.animate-hint-up {
  animation: hint-up 1.8s ease-in-out infinite;
}

/* Smooth pull-out reveal */
.outfit-reveal-enter-active {
  overflow: hidden;
  transition: max-height 0.28s ease, opacity 0.2s ease;
  max-height: 480px;
}
.outfit-reveal-leave-active {
  overflow: hidden;
  transition: max-height 0.22s ease, opacity 0.18s ease;
  max-height: 480px;
}
.outfit-reveal-enter-from,
.outfit-reveal-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
