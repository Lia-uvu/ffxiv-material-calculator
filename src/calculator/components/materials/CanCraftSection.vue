<template>
  <div>
    <div class="mt-2 mb-2 flex items-baseline justify-between">
      <div class="text-sm font-semibold text-[#EDE9F7]">{{ t("materials.craftable.title") }}</div>
      <div class="text-xs text-[#9B96AD]">
        {{ t("common.itemCount", { count: rows.length }) }}
      </div>
    </div>

    <div v-if="rows.length === 0" class="mb-4 rounded-2xl border border-[#5C5470] bg-[#4A4858] p-3 text-sm text-[#9B96AD]">
      {{ t("materials.craftable.empty") }}
    </div>

    <div v-else class="mb-4 space-y-2">
      <div
        v-for="row in rows"
        :key="'c-' + row.item.id"
        :class="['rounded-2xl border p-3', row.item.isExpanded ? 'bg-[#2A2933] border-[#38364A]' : 'bg-[#4A4858] border-[#5C5470]']"
      >
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 transition-colors"
            :class="checkedIds.has(row.item.id)
              ? 'bg-[#B4A5C8] border-[#B4A5C8]'
              : 'border-[#7A7589] bg-transparent hover:border-[#B4A5C8]'"
            :title="t('common.completed')"
            @click="$emit('toggle-check', row.item.id)"
          >
            <Check v-if="checkedIds.has(row.item.id)" :size="11" color="#2D2C34" :stroke-width="3" />
          </button>

          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <div
                class="truncate text-sm font-medium"
                :class="checkedIds.has(row.item.id) ? 'line-through text-[#9B96AD]' : 'text-[#EDE9F7]'"
              >
                {{ row.item.name }}
              </div>
              <span
                class="shrink-0 rounded-full px-1.5 py-0.5 text-[10px]"
                :class="row.item.isExpanded
                  ? 'bg-[#2E2D3A] text-[#6B677A]'
                  : 'bg-[#4A4560] text-[#C8BFDA]'"
              >
                {{ row.item.isExpanded ? t("materials.craftable.expanded") : t("materials.craftable.collapsed") }}
              </span>
            </div>
            <div class="mt-0.5 text-xs" :class="checkedIds.has(row.item.id) ? 'text-[#9B96AD] opacity-40' : 'text-[#9B96AD]'">
              {{ row.item.job ? (te(`jobs.${row.item.job}`) ? t(`jobs.${row.item.job}`) : row.item.job) : t("common.placeholder") }}
            </div>
          </div>

          <div class="shrink-0 text-right tabular-nums leading-tight" :class="checkedIds.has(row.item.id) ? 'opacity-40' : ''">
            <div class="text-sm font-semibold text-[#EDE9F7]">
              {{ row.item.isExpanded
                ? t("materials.craftLabel", { n: row.item.craftTimes })
                : t("materials.needLabel", { n: row.item.needAmount }) }}
            </div>
            <div class="text-xs text-[#9B96AD]">
              {{ row.item.isExpanded
                ? t("materials.needLabel", { n: row.item.needAmount })
                : t("materials.craftLabel", { n: row.item.craftTimes }) }}
            </div>
          </div>

          <button
            type="button"
            class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl transition-opacity hover:opacity-70"
            :title="row.item.isExpanded ? t('materials.craftable.collapse') : t('materials.craftable.expand')"
            @click="$emit('toggle-expand', row.item.id)"
          >
            <Link2Off v-if="row.item.isExpanded" :size="20" color="#E8D07A" />
            <Link2 v-else :size="20" color="#B4A5C8" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { Check, Link2, Link2Off } from "lucide-vue-next";

const props = defineProps({
  craftable: { type: Array, default: () => [] },
  checkedIds: { type: Object, required: true },
  expandOrder: { type: Object, default: () => new Map() },
});

defineEmits(["toggle-check", "toggle-expand"]);

const { t, te } = useI18n();

const items = computed(() => (props.craftable ?? []).filter((entry) => !entry?.isCrystal));

const rows = computed(() => {
  const entries = items.value ?? [];
  return entries.map((item, idx) => ({ item, idx }));
});
</script>
