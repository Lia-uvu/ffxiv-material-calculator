<!-- CanCraftSection.vue -->
<template>
  <div>
    <div class="flex items-baseline justify-between mt-2 mb-2">
      <div class="text-sm font-semibold text-zinc-800">可制作材料</div>
      <div class="text-xs text-zinc-500">{{ rows.length }} 项</div>
    </div>

    <div v-if="rows.length === 0" class="text-sm text-zinc-500 mb-4">
      当前没有可制作材料。
    </div>

    <div v-else class="space-y-2 mb-4">
      <div
        v-for="r in rows"
        :key="'c-' + r.item.id"
        class="relative rounded-2xl border border-zinc-200 p-3 overflow-hidden"
        :class="[
          r.item.isExpanded ? 'bg-zinc-50' : 'bg-white',
          checkedIds.has(r.item.id) ? 'opacity-80' : ''
        ]"
      >
        <!-- 勾选蒙版（只影响视觉，不改变顺序） -->
        <div
          v-if="checkedIds.has(r.item.id)"
          class="absolute inset-0 rounded-2xl bg-violet-200/40 pointer-events-none flex items-center justify-center"
        >
          <div class="text-violet-900 font-semibold text-sm">✓ 已完成</div>
        </div>

        <div class="flex items-start gap-3">
          <button
            type="button"
            class="mt-0.5 h-5 w-5 rounded border border-zinc-300 flex items-center justify-center shrink-0 bg-white"
            @click="$emit('toggle-check', r.item.id)"
          >
            <span v-if="checkedIds.has(r.item.id)" class="text-sm">✓</span>
          </button>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <div class="text-sm font-medium text-zinc-900 truncate">
                {{ r.item.name }}
              </div>

              <span
                class="text-[11px] px-2 py-0.5 rounded-full"
                :class="r.item.isExpanded ? 'bg-violet-100 text-violet-700' : 'bg-zinc-100 text-zinc-700'"
              >
                {{ r.item.isExpanded ? '已拆' : '未拆' }}
              </span>
            </div>

            <div class="text-xs text-zinc-500 mt-1">
              制作职业：{{ r.item.job ?? "—" }}
              <template v-if="r.item.isExpanded"> · 需求：{{ r.item.needAmount }}</template>
            </div>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <div class="text-sm font-semibold tabular-nums text-zinc-900 w-16 text-right">
              {{ r.item.displayAmount }}{{ r.item.displaySuffix }}
            </div>

            <button
              type="button"
              class="h-8 w-8 rounded-xl border border-zinc-200 flex items-center justify-center hover:bg-zinc-50"
              @click="$emit('toggle-expand', r.item.id)"
              :title="r.item.isExpanded ? '锁回去（不拆）' : '拆开（展开）'"
            >
              <span v-if="r.item.isExpanded">🔓</span>
              <span v-else>🔗</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  craftable: { type: Array, default: () => [] },
  checkedIds: { type: Object, required: true }, // Set
});

defineEmits(["toggle-check", "toggle-expand"]);

/** 水晶不在此区显示 */
const items = computed(() => (props.craftable ?? []).filter((e) => !e?.isCrystal));

/**
 * 简单排序：
 * - 已拆（isExpanded=true）的放上面
 * - 未拆的放下面
 * - 组内保持原顺序（calcMaterials / composable 的排序结果不被破坏）
 */
const rows = computed(() => {
  const arr = items.value ?? [];
  const withIdx = arr.map((item, idx) => ({ item, idx }));
  withIdx.sort((a, b) => {
    const ea = a.item?.isExpanded ? 1 : 0;
    const eb = b.item?.isExpanded ? 1 : 0;
    if (ea !== eb) return eb - ea; // expanded first
    return a.idx - b.idx; // stable
  });
  return withIdx;
});
</script>