<!-- CanCraftSection.vue -->
<template>
  <div>
    <div class="flex items-baseline justify-between mt-2 mb-2">
      <div class="text-sm font-semibold text-[#EDE9F7]">{{ t("materials.craftable.title") }}</div>
      <div class="text-xs text-[#9B96AD]">
        {{ t("common.itemCount", { count: rows.length }) }}
      </div>
    </div>

    <div v-if="rows.length === 0" class="rounded-xl bg-[#2A2933] px-3 py-2 text-sm text-[#6B677A] mb-4">
      {{ t("materials.craftable.empty") }}
    </div>

    <div v-else class="space-y-2 mb-4">
      <div
        v-for="r in rows"
        :key="'c-' + r.item.id"
        :class="['rounded-2xl border p-3', r.item.isExpanded ? 'bg-[#2A2933] border-[#38364A]' : 'bg-[#4A4858] border-[#5C5470]']"
      >
        <div class="flex items-center gap-3">
          <!-- Checkbox (circle) -->
          <button
            type="button"
            class="shrink-0 h-5 w-5 rounded-full border-2 flex items-center justify-center transition-colors"
            :class="checkedIds.has(r.item.id)
              ? 'bg-[#B4A5C8] border-[#B4A5C8]'
              : 'border-[#7A7589] bg-transparent hover:border-[#B4A5C8]'"
            @click="$emit('toggle-check', r.item.id)"
            :title="t('common.completed')"
          >
            <Check v-if="checkedIds.has(r.item.id)" :size="11" color="#2D2C34" :stroke-width="3" />
          </button>

          <!-- Name + info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <div
                class="text-sm font-medium truncate"
                :class="checkedIds.has(r.item.id) ? 'line-through text-[#9B96AD]' : 'text-[#EDE9F7]'"
              >
                {{ r.item.name }}
              </div>
              <span
                class="text-[10px] px-1.5 py-0.5 rounded-full shrink-0"
                :class="r.item.isExpanded
                  ? 'bg-[#2E2D3A] text-[#6B677A]'
                  : 'bg-[#4A4560] text-[#C8BFDA]'"
              >
                {{ r.item.isExpanded ? t("materials.craftable.expanded") : t("materials.craftable.collapsed") }}
              </span>
            </div>
            <div class="text-xs text-[#9B96AD] mt-0.5">
              {{ r.item.job ? (te(`jobs.${r.item.job}`) ? t(`jobs.${r.item.job}`) : r.item.job) : t("common.placeholder") }}
            </div>
          </div>

          <!-- Amount (dual line) -->
          <div class="text-right shrink-0 tabular-nums leading-tight">
            <div class="text-sm font-semibold text-[#EDE9F7]">
              {{ r.item.isExpanded
                ? t("materials.craftLabel", { n: r.item.craftTimes })
                : t("materials.needLabel", { n: r.item.needAmount }) }}
            </div>
            <div class="text-xs text-[#9B96AD]">
              {{ r.item.isExpanded
                ? t("materials.needLabel", { n: r.item.needAmount })
                : t("materials.craftLabel", { n: r.item.craftTimes }) }}
            </div>
          </div>

          <!-- Chain icon button -->
          <button
            type="button"
            class="shrink-0 h-9 w-9 flex items-center justify-center rounded-xl transition-opacity hover:opacity-70"
            @click="$emit('toggle-expand', r.item.id)"
            :title="r.item.isExpanded ? t('materials.craftable.collapse') : t('materials.craftable.expand')"
          >
            <Link2Off v-if="r.item.isExpanded" :size="20" color="#E8D07A" />
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
  checkedIds: { type: Object, required: true }, // Set
  expandOrder: { type: Object, default: () => new Map() },
});

defineEmits(["toggle-check", "toggle-expand"]);

const { t, te } = useI18n();

const items = computed(() => (props.craftable ?? []).filter((e) => !e?.isCrystal));

const rows = computed(() => {
  const arr = items.value ?? [];
  return arr.map((item, idx) => ({ item, idx }));
});
</script>
