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
      </div>
    </div>

    <!-- 可制作 -->
    <div class="flex items-baseline justify-between mt-2 mb-2">
      <div class="text-sm font-semibold text-zinc-800">可制作材料</div>
      <div class="text-xs text-zinc-500">{{ ui.craftable.length }} 项</div>
    </div>

    <div v-if="ui.craftable.length === 0" class="text-sm text-zinc-500 mb-4">
      当前没有可制作材料。
    </div>

    <div v-else class="space-y-2 mb-4">
      <div
        v-for="e in ui.craftable"
        :key="'c-' + e.id"
        class="relative rounded-2xl border border-zinc-200 p-3 transition"
        :class="[
          e.isExpanded ? 'bg-zinc-50' : 'bg-white',
          checkedIds.has(e.id) ? 'opacity-80' : ''
        ]"
      >
        <!-- 勾选蒙版 -->
        <div
          v-if="checkedIds.has(e.id)"
          class="absolute inset-0 rounded-2xl bg-violet-200/40 pointer-events-none flex items-center justify-center"
        >
          <div class="text-violet-900 font-semibold text-sm">✓ 已完成</div>
        </div>

        <div class="flex items-start gap-3">
          <!-- checkbox -->
          <button
            type="button"
            class="mt-0.5 h-5 w-5 rounded border border-zinc-300 flex items-center justify-center shrink-0 bg-white"
            @click="toggleCheck(e.id)"
          >
            <span v-if="checkedIds.has(e.id)" class="text-sm">✓</span>
          </button>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <div class="text-sm font-medium text-zinc-900 truncate">
                {{ e.name }}
              </div>

              <span
                v-if="e.isCrystal"
                class="text-[11px] px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-700"
              >
                水晶
              </span>

              <span
                class="text-[11px] px-2 py-0.5 rounded-full"
                :class="e.isExpanded ? 'bg-violet-100 text-violet-700' : 'bg-zinc-100 text-zinc-700'"
              >
                {{ e.isExpanded ? '已拆' : '未拆' }}
              </span>
            </div>

            <div class="text-xs text-zinc-500 mt-1">
              制作职业：{{ e.job ?? "—" }}
              <template v-if="e.isExpanded"> · 需求：{{ e.needAmount }}</template>
            </div>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <div class="text-sm font-semibold tabular-nums text-zinc-900 w-16 text-right">
              {{ e.displayAmount }}{{ e.displaySuffix }}
            </div>

            <button
              type="button"
              class="h-8 w-8 rounded-xl border border-zinc-200 flex items-center justify-center hover:bg-zinc-50"
              @click="$emit('toggle-expand', e.id)"
              :title="e.isExpanded ? '锁回去（不拆）' : '拆开（展开）'"
            >
              <span v-if="e.isExpanded">🔓</span>
              <span v-else>🔗</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 不可制作 -->
    <div class="flex items-baseline justify-between mt-2 mb-2">
      <div class="text-sm font-semibold text-zinc-800">不可制作材料</div>
      <div class="text-xs text-zinc-500">{{ ui.nonCraftable.length }} 项</div>
    </div>

    <div v-if="ui.nonCraftable.length === 0" class="text-sm text-zinc-500">
      当前没有不可制作材料。
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="e in ui.nonCraftable"
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
            @click="toggleCheck(e.id)"
          >
            <span v-if="checkedIds.has(e.id)" class="text-sm">✓</span>
          </button>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <div class="text-sm font-medium text-zinc-900 truncate">
                {{ e.name }}
              </div>

              <span
                v-if="e.isCrystal"
                class="text-[11px] px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-700"
              >
                水晶
              </span>
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
import { shallowReactive } from "vue";

defineProps({
  ui: {
    type: Object,
    required: true,
  },
});

defineEmits(["toggle-expand", "collapse-all", "expand-all"]);

const checkedIds = shallowReactive(new Set());

function toggleCheck(id) {
  if (checkedIds.has(id)) checkedIds.delete(id);
  else checkedIds.add(id);
}

function clearChecked() {
  checkedIds.clear();
}
</script>
