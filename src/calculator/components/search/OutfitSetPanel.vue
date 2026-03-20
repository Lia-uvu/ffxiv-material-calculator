<template>
  <section class="rounded-2xl border border-[#3D3B4A] bg-[#3B3A47] p-4 shadow-[0_4px_16px_rgba(0,0,0,0.3)]">
    <button
      type="button"
      class="flex w-full items-center justify-between gap-2"
      @click="expanded = !expanded"
    >
      <h2 class="text-sm font-semibold tracking-tight text-[#EDE9F7]">
        {{ t("outfitSets.title") }}
      </h2>
      <ChevronDown
        :size="16"
        class="shrink-0 text-[#9B96AD] transition-transform duration-200"
        :class="{ 'rotate-180': expanded }"
      />
    </button>

    <div v-if="expanded" class="mt-3 space-y-3">
      <div v-for="tier in tiers" :key="tier.level">
        <button
          type="button"
          class="mb-1.5 flex w-full items-center gap-1.5 text-xs font-medium text-[#B4A5C8]"
          @click="toggleTier(tier.level)"
        >
          <ChevronRight
            :size="12"
            class="shrink-0 transition-transform duration-150"
            :class="{ 'rotate-90': expandedTiers.has(tier.level) }"
          />
          {{ tier.label }}
          <span class="text-[#6B677A]">({{ tier.sets.length }})</span>
        </button>

        <div v-if="expandedTiers.has(tier.level)" class="flex flex-wrap gap-1.5 pl-4">
          <button
            v-for="set in tier.sets"
            :key="setKey(set)"
            type="button"
            class="group relative inline-flex items-center gap-1 rounded-lg border px-2 py-1 text-xs transition-colors"
            :class="
              selectedSet === set
                ? 'border-[#B4A5C8]/60 bg-[#4A4370] text-[#EDE9F7]'
                : 'border-[#4A4858] bg-[#302F3B] text-[#9B96AD] hover:border-[#5A5868] hover:bg-[#3B3A47] hover:text-[#EDE9F7]'
            "
            @click="toggleSet(set)"
          >
            {{ resolvePrefix(set) }}
            <span class="text-[#6B677A]">{{ set.itemIds.length }}</span>
          </button>
        </div>

        <!-- Expanded set detail -->
        <div
          v-if="expandedTiers.has(tier.level) && selectedSet && tier.sets.includes(selectedSet)"
          class="mt-2 ml-4 rounded-xl border border-[#4A4858] bg-[#302F3B] p-3"
        >
          <div class="mb-2 flex items-center justify-between gap-2">
            <div>
              <span class="text-sm font-medium text-[#EDE9F7]">{{ resolvePrefix(selectedSet) }}</span>
              <span class="ml-2 text-xs text-[#9B96AD]">
                ilvl {{ selectedSet.ilvl }} · {{ selectedSet.itemIds.length }} {{ t("outfitSets.pieces") }}
              </span>
            </div>
            <button
              type="button"
              class="inline-flex h-7 items-center gap-1 rounded-lg border border-[#B4A5C8]/40 bg-[#4A4370] px-2.5 text-xs font-medium text-[#EDE9F7] transition-colors hover:bg-[#5A5380]"
              @click="addSetToTargets(selectedSet)"
            >
              <Plus :size="12" />
              {{ t("outfitSets.addAll") }}
            </button>
          </div>

          <ul class="space-y-0.5">
            <li
              v-for="itemId in selectedSet.itemIds"
              :key="itemId"
              class="flex items-center justify-between rounded px-1.5 py-0.5 text-xs"
            >
              <span class="truncate text-[#C5C0D4]">{{ itemName(itemId) }}</span>
              <span v-if="targetAmounts.has(itemId)" class="shrink-0 ml-2 text-[#B4A5C8]">
                ×{{ targetAmounts.get(itemId) }}
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { ChevronDown, ChevronRight, Plus } from "lucide-vue-next";

const props = defineProps({
  sets: { type: Array, default: () => [] },
  itemById: { type: Map, default: () => new Map() },
  targetAmounts: { type: Map, default: () => new Map() },
});

const emit = defineEmits(["add-set"]);
const { t, locale } = useI18n();

const expanded = ref(false);
const expandedTiers = ref(new Set());
const selectedSet = ref(null);

const TIER_LABELS = {
  100: "Lv.100 — 7.x",
  90: "Lv.90 — 6.x",
  80: "Lv.80 — 5.x",
  70: "Lv.70 — 4.x",
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

function setKey(set) {
  return `${set.prefix["zh-CN"]}-${set.ilvl}`;
}

function resolvePrefix(set) {
  return set.prefix[locale.value] || set.prefix["zh-CN"];
}

function itemName(itemId) {
  const item = props.itemById.get(itemId);
  if (!item) return `#${itemId}`;
  const raw = item.name;
  if (typeof raw === "string") return raw;
  return raw?.[locale.value] ?? raw?.["zh-CN"] ?? `#${itemId}`;
}

function toggleTier(level) {
  const next = new Set(expandedTiers.value);
  if (next.has(level)) {
    next.delete(level);
    // Clear selected set if it belongs to collapsed tier
    if (selectedSet.value && selectedSet.value.crafterLevel === level) {
      selectedSet.value = null;
    }
  } else {
    next.add(level);
  }
  expandedTiers.value = next;
}

function toggleSet(set) {
  selectedSet.value = selectedSet.value === set ? null : set;
}

function addSetToTargets(set) {
  emit("add-set", set.itemIds);
}
</script>
