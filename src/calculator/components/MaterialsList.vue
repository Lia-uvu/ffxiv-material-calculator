<!-- MaterialsList.vue -->
<template>
  <div class="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
    <div class="flex items-center justify-between mb-3">
      <div class="text-base font-semibold text-zinc-900">材料列表</div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          class="px-3 py-1.5 rounded-xl border border-zinc-200 text-sm hover:bg-zinc-50"
          @click="$emit('collapse-all')"
        >
          折叠到顶层
        </button>

        <button
          type="button"
          class="px-3 py-1.5 rounded-xl border border-zinc-200 text-sm hover:bg-zinc-50"
          @click="$emit('expand-all')"
        >
          拆到底
        </button>

        <button
          type="button"
          class="px-3 py-1.5 rounded-xl border border-zinc-200 text-sm hover:bg-zinc-50"
          @click="clearChecked"
        >
          清空勾选
        </button>

        <button
          type="button"
          class="px-3 py-1.5 rounded-xl border border-red-200 text-sm text-red-700 hover:bg-red-50"
          @click="onResetMaterials"
        >
          重置材料进度
        </button>

        <button
          type="button"
          class="px-3 py-1.5 rounded-xl border border-zinc-200 text-sm hover:bg-zinc-50"
          @click="$emit('copy-materials')"
        >
          复制材料清单
        </button>

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
      <div class="text-sm font-semibold text-zinc-800">水晶</div>
      <div class="text-xs text-zinc-500">{{ crystals.length }} 项</div>
    </div>

    <div v-if="crystals.length === 0" class="text-sm text-zinc-500">
      当前没有水晶消耗。
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
                水晶
              </span>
            </div>

            <div class="text-xs text-zinc-500 mt-1">
              <template v-if="e.job">制作职业：{{ e.job }}</template>
              <template v-else-if="e.source">获取来源：{{ e.source }}</template>
              <template v-else>—</template>
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
  const ok = window.confirm(
    "确定要重置材料列表进度吗？\n（会清空：已拆/拆的先后顺序/勾选，不影响目标列表）"
  );
  if (!ok) return;
  emit("reset-materials");
}

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
