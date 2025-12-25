<template>
  <section class="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
    <div class="flex items-baseline justify-between gap-3">
      <h2 class="text-lg font-semibold tracking-tight">Targets</h2>
      <p class="text-xs text-zinc-500">Total: {{ targets.length }}</p>
    </div>

    <p v-if="!targets.length" class="mt-2 text-sm text-zinc-600">
      No targets yet. Search an item and add it.
    </p>

    <ul v-else class="mt-4 space-y-2">
      <li
        v-for="t in targets"
        :key="t.id"
        class="flex items-center gap-3 rounded-xl bg-zinc-50 px-3 py-2"
      >
        <!-- name -->
        <div class="min-w-0 flex-1">
          <div class="truncate text-sm font-medium text-zinc-900">
            {{ t.name }}
          </div>
          <div class="text-xs text-zinc-500">#{{ t.id }}</div>
        </div>

        <!-- qty -->
        <input
          class="h-9 w-20 rounded-xl border border-zinc-200 bg-white px-2 text-sm text-zinc-900 outline-none focus:ring-4 focus:ring-zinc-200"
          type="number"
          min="1"
          step="1"
          :value="t.amount ?? 1"
          @input="onAmountInput(t.id, $event)"
          @blur="onAmountBlur(t.id, $event)"
        />

        <!-- remove -->
        <button
          type="button"
          class="inline-flex h-9 items-center justify-center rounded-xl border border-zinc-200 bg-white px-3 text-sm text-zinc-700 hover:bg-zinc-100 active:bg-zinc-200"
          @click="onRemove(t.id)"
          aria-label="Remove target"
          title="Remove"
        >
          Remove
        </button>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { toRefs } from "vue";

const props = defineProps({
  targets: {
    type: Array,
    default: () => [],
  },
});

const { targets } = toRefs(props);

const emit = defineEmits(["remove", "update-amount"]);

function clampAmount(raw) {
  const n = Number(raw);
  if (!Number.isFinite(n)) return 1;
  return Math.max(1, Math.floor(n));
}

function onRemove(id) {
  emit("remove", id);
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
