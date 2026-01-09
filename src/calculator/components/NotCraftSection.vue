<!-- NotCraftSection.vue -->
<template>
  <div>
    <div class="flex items-baseline justify-between mt-2 mb-2">
      <div class="text-sm font-semibold text-zinc-800">不可制作材料</div>
      <div class="text-xs text-zinc-500">{{ displayList.length }} 项</div>
    </div>

    <div v-if="displayList.length === 0" class="text-sm text-zinc-500">
      当前没有不可制作材料。
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="e in displayList"
        :key="'n-' + e.id"
        class="relative rounded-2xl border border-zinc-200 p-3 bg-white transition"
        :class="checkedIds.has(e.id) ? 'opacity-80' : ''"
      >
        <div
          v-if="checkedIds.has(e.id)"
          class="absolute inset-0 rounded-2xl bg-violet-200/40 pointer-events-none flex items-center justify-center"
        >
          <div class="text-violet-900 font-semibold text-sm">✓ 已完成</div>
        </div>

        <div class="flex items-start gap-3">
          <button
            type="button"
            class="mt-0.5 h-5 w-5 rounded border border-zinc-300 flex items-center justify-center shrink-0 bg-white"
            @click="$emit('toggle-check', e.id)"
          >
            <span v-if="checkedIds.has(e.id)" class="text-sm">✓</span>
          </button>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <div class="text-sm font-medium text-zinc-900 truncate">
                {{ e.name }}
              </div>
            </div>

            <div class="text-xs text-zinc-500 mt-1">
              获取来源：{{ e.source ?? "—" }}
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

const props = defineProps({
  nonCraftable: { type: Array, default: () => [] },
  checkedIds: { type: Object, required: true }, // Set
});

defineEmits(["toggle-check"]);

const nonCraftableNonCrystal = computed(() => props.nonCraftable.filter((e) => !e?.isCrystal));

// 未完成在上，已完成沉底；保持“添加进来”的顺序（不按名字排序）
const displayList = computed(() => {
  const pending = [];
  const done = [];
  for (const e of nonCraftableNonCrystal.value) {
    (props.checkedIds.has(e.id) ? done : pending).push(e);
  }
  return [...pending, ...done];
});
</script>
