<template>
  <section class="rounded-2xl border border-[#3D3B4A] bg-[#3B3A47] p-5 shadow-[0_4px_16px_rgba(0,0,0,0.3)]">
    <div class="flex items-baseline justify-between gap-3">
      <h2 class="text-lg font-semibold tracking-tight text-[#EDE9F7]">{{ t("targets.title") }}</h2>

      <div class="flex items-center gap-2">
        <p class="text-xs text-[#9B96AD]">{{ t("targets.total", { count: targets.length }) }}</p>

        <button
          v-if="targets.length"
          type="button"
          class="inline-flex h-8 items-center justify-center rounded-xl border border-[#4A4858] bg-[#302F3B] px-3 text-xs text-[#9B96AD] hover:bg-[#4A4858] transition-colors"
          @click="onClear"
          :aria-label="t('targets.clearAria')"
          :title="t('targets.clearTitle')"
        >
          {{ t("targets.clear") }}
        </button>
      </div>
    </div>

    <div v-if="!targets.length" class="mt-4 flex items-center gap-3 rounded-xl bg-[#302F3B] px-3 py-2 text-sm text-[#9B96AD]">
      {{ t("targets.empty") }}
    </div>

    <ul v-else class="mt-4 space-y-2">
      <li
        v-for="target in targets"
        :key="target.id"
        class="flex items-center gap-3 rounded-xl bg-[#302F3B] px-3 py-2"
      >
        <div class="min-w-0 flex-1">
          <div class="truncate text-sm font-medium text-[#EDE9F7]">
            {{ target.name }}
          </div>
          <div class="text-xs text-[#9B96AD]">#{{ target.id }}</div>
        </div>

        <input
          class="h-9 w-20 rounded-xl border border-[#4A4858] bg-[#2D2C34] px-2 text-sm text-[#EDE9F7] outline-none focus:ring-2 focus:ring-[#B4A5C8]/30"
          type="number"
          min="1"
          step="1"
          :value="target.amount ?? 1"
          @input="onAmountInput(target.id, $event)"
          @blur="onAmountBlur(target.id, $event)"
        />

        <button
          type="button"
          class="inline-flex h-9 items-center justify-center rounded-xl border border-[#4A4858] bg-[#302F3B] px-3 text-sm text-[#9B96AD] hover:bg-[#4A4858] transition-colors"
          @click="onRemove(target.id)"
          :aria-label="t('targets.removeAria')"
          :title="t('targets.removeTitle')"
        >
          {{ t("targets.remove") }}
        </button>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps({
  targets: {
    type: Array,
    default: () => [],
  },
});

const { targets } = toRefs(props);
const { t } = useI18n();

const emit = defineEmits(["remove", "update-amount", "clear"]);

function clampAmount(raw) {
  const n = Number(raw);
  if (!Number.isFinite(n)) return 1;
  return Math.max(1, Math.floor(n));
}

function onRemove(id) {
  emit("remove", id);
}

function onClear() {
  emit("clear");
}

function onAmountInput(id, e) {
  const next = clampAmount(e.target.value);
  emit("update-amount", { id, amount: next });
}

function onAmountBlur(id, e) {
  const next = clampAmount(e.target.value);
  e.target.value = String(next);
  emit("update-amount", { id, amount: next });
}
</script>
