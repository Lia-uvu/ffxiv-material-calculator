<!-- MaterialsList.vue -->
<template>
  <div class="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
    <div class="flex items-center justify-between mb-3">
      <div class="text-base font-semibold text-zinc-900">{{ t("materials.title") }}</div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          class="px-3 py-1.5 rounded-xl border border-zinc-200 text-sm hover:bg-zinc-50"
          @click="$emit('collapse-all')"
        >
          {{ t("materials.collapseAll") }}
        </button>

        <button
          type="button"
          class="px-3 py-1.5 rounded-xl border border-zinc-200 text-sm hover:bg-zinc-50"
          @click="$emit('expand-all')"
        >
          {{ t("materials.expandAll") }}
        </button>

        <button
          type="button"
          class="px-3 py-1.5 rounded-xl border border-zinc-200 text-sm hover:bg-zinc-50"
          @click="clearChecked"
        >
          {{ t("materials.clearChecked") }}
        </button>

        <button
          type="button"
          class="px-3 py-1.5 rounded-xl border border-red-200 text-sm text-red-700 hover:bg-red-50"
          @click="onResetMaterials"
        >
          {{ t("materials.resetProgress") }}
        </button>

        <button
          type="button"
          class="px-3 py-1.5 rounded-xl border border-zinc-200 text-sm hover:bg-zinc-50"
          @click="$emit('copy-materials')"
        >
          {{ t("materials.copyList") }}
        </button>

        <span
          v-if="copySuccess"
          class="text-xs text-emerald-600"
        >
          {{ t("materials.copySuccess") }}
        </span>

      </div>
    </div>

    <CanCraftSection
      :craftable="ui.craftable"
      :checked-ids="checkedIds"
      :expand-order="expandOrder"
      @toggle-check="toggleCheck"
      @toggle-expand="(id) => $emit('toggle-expand', id)"
    />

    <NotCraftSection
      :non-craftable="ui.nonCraftable"
      :checked-ids="checkedIds"
      @toggle-check="toggleCheck"
    />

    <!-- 水晶（独立区域：不参与勾选；emoji 占位） -->
    <div class="flex items-baseline justify-between mt-6 mb-2">
      <div class="text-sm font-semibold text-zinc-800">{{ t("materials.crystals") }}</div>
      <div class="text-xs text-zinc-500">
        {{ t("common.itemCount", { count: crystals.length }) }}
      </div>
    </div>

    <div v-if="crystals.length === 0" class="text-sm text-zinc-500">
      {{ t("materials.noCrystals") }}
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="e in crystals"
        :key="'x-' + e.id"
        class="rounded-2xl border border-zinc-200 p-3 bg-white"
      >
        <div class="flex items-start gap-3">
          <div class="mt-0.5 h-5 w-5 flex items-center justify-center shrink-0">
            💎
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <div class="text-sm font-medium text-zinc-900 truncate">
                {{ e.name }}
              </div>
              <span class="text-[11px] px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-700">
                {{ t("materials.crystals") }}
              </span>
            </div>

            <div class="text-xs text-zinc-500 mt-1">
              <template v-if="e.job">{{ t("materials.jobLabel") }}：{{ e.job }}</template>
              <template v-else-if="e.source">
                {{ t("materials.sourceLabel") }}：{{ e.source }}
              </template>
              <template v-else>{{ t("common.placeholder") }}</template>
            </div>
          </div>

          <div class="text-sm font-semibold tabular-nums text-zinc-900 w-16 text-right shrink-0">
            {{ e.displayAmount }}{{ e.displaySuffix }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import CanCraftSection from "./CanCraftSection.vue";
import NotCraftSection from "./NotCraftSection.vue";

const props = defineProps({
  ui: {
    type: Object,
    required: true,
  },

  // ✅ 由 page/store 传入：持久化勾选状态
  checkedIds: {
    type: Object,
    required: true,
  },

  // ✅ 由 page/store 传入：已拆顺序（可选，用于 CanCraftSection 排序）
  expandOrder: {
    type: Object,
    default: () => new Map(),
  },

  copySuccess: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "toggle-expand",
  "collapse-all",
  "expand-all",
  "toggle-check",
  "clear-checked",
  "reset-materials",
  "copy-materials",
]);

function toggleCheck(id) {
  emit("toggle-check", id);
}

function clearChecked() {
  emit("clear-checked");
}

function onResetMaterials() {
  const ok = window.confirm(t("materials.resetConfirm"));
  if (!ok) return;
  emit("reset-materials");
}

const { t } = useI18n();

const crystals = computed(() => {
  const craftable = props.ui?.craftable ?? [];
  const nonCraftable = props.ui?.nonCraftable ?? [];

  const out = [];
  const seen = new Set();
  const push = (e) => {
    if (!e?.isCrystal) return;
    if (seen.has(e.id)) return;
    seen.add(e.id);
    out.push(e);
  };

  for (const e of craftable) push(e);
  for (const e of nonCraftable) push(e);

  return out;
});
</script>
