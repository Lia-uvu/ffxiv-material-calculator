<!-- MaterialsList.vue -->
<template>
  <section class="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
    <div class="flex items-baseline justify-between gap-3">
      <h2 class="text-lg font-semibold tracking-tight">Materials List</h2>

      <p class="text-xs text-zinc-500">
        Total: {{ props.entries.length }} items
      </p>
    </div>

    <p v-if="!props.entries.length" class="mt-2 text-sm text-zinc-600">
      No materials yet. Add a target item to see the list.
    </p>

    <template v-else>
      <!-- Crystals -->
      <div v-if="crystals.length" class="mt-4">
        <div class="mb-2 flex items-center justify-between">
          <h3 class="text-sm font-medium text-zinc-700">Crystals</h3>
          <span class="text-xs text-zinc-500">{{ crystals.length }}</span>
        </div>

        <ul class="space-y-2">
          <li
            v-for="m in crystals"
            :key="m.id"
            class="flex items-center justify-between rounded-xl bg-zinc-50 px-3 py-2"
          >
            <div class="min-w-0 flex-1">
              <span class="truncate text-sm text-zinc-900">
                {{ m.name }}
              </span>
            </div>

            <span class="ml-4 shrink-0 text-sm font-medium text-zinc-900">
              × {{ m.amount }}
            </span>
          </li>
        </ul>
      </div>

      <!-- Materials -->
      <div v-if="others.length" class="mt-6">
        <div class="mb-2 flex items-center justify-between">
          <h3 class="text-sm font-medium text-zinc-700">Materials</h3>
          <span class="text-xs text-zinc-500">{{ others.length }}</span>
        </div>

        <ul class="space-y-2">
          <li
            v-for="m in others"
            :key="m.id"
            class="flex items-center justify-between rounded-xl bg-zinc-50 px-3 py-2"
          >
            <div class="min-w-0 flex-1">
              <span class="truncate text-sm text-zinc-900">
                {{ m.name }}
              </span>
            </div>

            <span class="ml-4 shrink-0 text-sm font-medium text-zinc-900">
              × {{ m.amount }}
            </span>
          </li>
        </ul>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, PropType } from "vue";

type MaterialEntry = {
  id: number;
  name: string;
  amount: number;
  isCrystal?: boolean;
};

const props = defineProps({
  entries: {
    type: Array as PropType<MaterialEntry[]>,
    required: true,
  },
});

const crystals = computed(() => props.entries.filter((e) => e.isCrystal));
const others = computed(() => props.entries.filter((e) => !e.isCrystal));
</script>
