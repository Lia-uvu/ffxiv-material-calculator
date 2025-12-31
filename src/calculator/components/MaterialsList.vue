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
              <div class="flex items-center gap-2 min-w-0">
                <span class="truncate text-sm text-zinc-900">
                  {{ m.name }}
                </span>

                <!-- small i -->
                <button
                  v-if="hasBreakdown(m)"
                  type="button"
                  class="shrink-0 rounded-full border border-zinc-200 bg-white px-2 py-0.5 text-xs text-zinc-600 hover:bg-zinc-100"
                  title="Show breakdown"
                  @click="openBreakdown(m)"
                >
                  i
                </button>
              </div>
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
              <div class="flex items-center gap-2 min-w-0">
                <span class="truncate text-sm text-zinc-900">
                  {{ m.name }}
                </span>

                <!-- small i -->
                <button
                  v-if="hasBreakdown(m)"
                  type="button"
                  class="shrink-0 rounded-full border border-zinc-200 bg-white px-2 py-0.5 text-xs text-zinc-600 hover:bg-zinc-100"
                  title="Show breakdown"
                  @click="openBreakdown(m)"
                >
                  i
                </button>
              </div>
            </div>

            <span class="ml-4 shrink-0 text-sm font-medium text-zinc-900">
              × {{ m.amount }}
            </span>
          </li>
        </ul>
      </div>
    </template>

    <!-- Internal modal (future: can be extracted as a child component) -->
    <teleport to="body">
      <div
        v-if="dialog.open"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="closeDialog"
      >
        <div class="absolute inset-0 bg-black/40"></div>

        <div class="relative w-full max-w-md rounded-2xl bg-white shadow-lg border border-zinc-200">
          <div class="flex items-start justify-between gap-3 p-4 border-b border-zinc-100">
            <div class="min-w-0">
              <p class="text-sm font-semibold text-zinc-900 truncate">
                {{ dialog.materialName }}
              </p>
              <p class="mt-1 text-xs text-zinc-500">
                Total: × {{ dialog.totalAmount }}
              </p>
            </div>

            <button
              type="button"
              class="shrink-0 rounded-xl px-2 py-1 text-sm text-zinc-600 hover:bg-zinc-100"
              @click="closeDialog"
            >
              ✕
            </button>
          </div>

          <div class="p-4">
            <p v-if="!dialog.rows.length" class="text-sm text-zinc-600">
              No breakdown info.
            </p>

            <ul v-else class="space-y-2">
              <li
                v-for="r in dialog.rows"
                :key="r.parentId"
                class="flex items-center justify-between rounded-xl bg-zinc-50 px-3 py-2"
              >
                <span class="min-w-0 flex-1 truncate text-sm text-zinc-900">
                  {{ r.parentName }}
                </span>
                <span class="ml-4 shrink-0 text-sm font-medium text-zinc-900">
                  × {{ r.amount }}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </teleport>
  </section>
</template>

<script setup lang="ts">
import { computed, PropType, reactive, onMounted, onBeforeUnmount } from "vue";

type MaterialEntry = {
  id: number;
  name: string;
  amount: number;
  isCrystal?: boolean;
  hasBreakdown?: boolean; // <- from composable
};

type BreakdownRow = {
  parentId: number;
  parentName: string;
  amount: number;
};

const props = defineProps({
  entries: {
    type: Array as PropType<MaterialEntry[]>,
    required: true,
  },
  // page will pass: :get-breakdown-rows="getMaterialBreakdownRows"
  getBreakdownRows: {
    type: Function as PropType<(materialId: number) => BreakdownRow[]>,
    required: true,
  },
});

const emit = defineEmits<{
  (e: "open-breakdown", payload: { material: MaterialEntry; rows: BreakdownRow[] }): void;
}>();

const crystals = computed(() => props.entries.filter((e) => e.isCrystal));
const others = computed(() => props.entries.filter((e) => !e.isCrystal));

function hasBreakdown(m: MaterialEntry) {
  // Prefer the precomputed flag; fallback to checking rows
  if (m.hasBreakdown != null) return m.hasBreakdown;
  return props.getBreakdownRows(m.id).length > 0;
}

// internal modal state (future: extract to child component easily)
const dialog = reactive({
  open: false,
  materialId: 0,
  materialName: "",
  totalAmount: 0,
  rows: [] as BreakdownRow[],
});

function openBreakdown(m: MaterialEntry) {
  const rows = props.getBreakdownRows(m.id) ?? [];
  emit("open-breakdown", { material: m, rows });

  dialog.open = true;
  dialog.materialId = m.id;
  dialog.materialName = m.name;
  dialog.totalAmount = m.amount;
  dialog.rows = rows;
}

function closeDialog() {
  dialog.open = false;
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape" && dialog.open) closeDialog();
}

onMounted(() => window.addEventListener("keydown", onKeydown));
onBeforeUnmount(() => window.removeEventListener("keydown", onKeydown));
</script>
