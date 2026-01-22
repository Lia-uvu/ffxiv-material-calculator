<template>
  <section class="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
    <div class="flex items-baseline justify-between gap-3">
      <h2 class="text-lg font-semibold tracking-tight">{{ t("targets.title") }}</h2>

      <div class="flex items-center gap-2">
        <p class="text-xs text-zinc-500">{{ t("targets.total", { count: targets.length }) }}</p>

        <button
          v-if="targets.length"
          type="button"
          class="inline-flex h-8 items-center justify-center rounded-xl border border-zinc-200 bg-white px-3 text-xs text-zinc-700 hover:bg-zinc-100 active:bg-zinc-200"
          @click="onClear"
          :aria-label="t('targets.clearAria')"
          :title="t('targets.clearTitle')"
        >
          {{ t("targets.clear") }}
        </button>
      </div>
    </div>

    <p v-if="!targets.length" class="mt-2 text-sm text-zinc-600">
      {{ t("targets.empty") }}
    </p>

    <ul v-else class="mt-4 space-y-2">
      <li
        v-for="target in targets"
        :key="target.id"
        class="flex items-center gap-3 rounded-xl bg-zinc-50 px-3 py-2"
      >
        <!-- name -->
        <div class="min-w-0 flex-1">
          <div class="truncate text-sm font-medium text-zinc-900">
            {{ t.name }}
          </div>
          <div class="text-xs text-zinc-500">#{{ target.id }}</div>
        </div>

        <!-- qty -->
        <input
          class="h-9 w-20 rounded-xl border border-zinc-200 bg-white px-2 text-sm text-zinc-900 outline-none focus:ring-4 focus:ring-zinc-200"
          type="number"
          min="1"
          step="1"
          :value="t.amount ?? 1"
          @input="onAmountInput(target.id, $event)"
          @blur="onAmountBlur(target.id, $event)"
        />

        <!-- remove -->
        <button
          type="button"
          class="inline-flex h-9 items-center justify-center rounded-xl border border-zinc-200 bg-white px-3 text-sm text-zinc-700 hover:bg-zinc-100 active:bg-zinc-200"
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

// ✅ 新增 clear
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
