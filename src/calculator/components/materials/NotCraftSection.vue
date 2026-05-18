<template>
  <div>
    <div class="mt-2 mb-2 flex items-baseline justify-between">
      <div class="text-sm font-semibold text-[#EDE9F7]">
        {{ t("materials.nonCraftable.title") }}
      </div>
      <div class="text-xs text-[#9B96AD]">
        {{ t("common.itemCount", { count: displayList.length }) }}
      </div>
    </div>

    <div v-if="displayList.length === 0" class="rounded-2xl border border-[#5C5470] bg-[#4A4858] p-3 text-sm text-[#9B96AD]">
      {{ t("materials.nonCraftable.empty") }}
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="entry in displayList"
        :key="'n-' + entry.id"
        class="cursor-default rounded-2xl border border-[#5C5470] bg-[#4A4858] p-3"
      >
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 transition-colors"
            :class="checkedIds.has(entry.id)
              ? 'bg-[#B4A5C8] border-[#B4A5C8]'
              : 'border-[#7A7589] bg-transparent hover:border-[#B4A5C8]'"
            :title="t('common.completed')"
            @click="$emit('toggle-check', entry.id)"
          >
            <Check v-if="checkedIds.has(entry.id)" :size="11" color="#2D2C34" :stroke-width="3" />
          </button>

          <div class="min-w-0 flex-1">
            <div
              class="truncate text-sm font-medium"
              :class="checkedIds.has(entry.id) ? 'line-through text-[#9B96AD]' : 'text-[#EDE9F7]'"
            >
              {{ entry.name }}
            </div>
            <div class="mt-0.5 text-xs" :class="checkedIds.has(entry.id) ? 'text-[#9B96AD] opacity-40' : 'text-[#9B96AD]'">
              {{ entry.source ?? t("common.placeholder") }}
            </div>
          </div>

          <div
            class="shrink-0 text-sm font-semibold tabular-nums"
            :class="checkedIds.has(entry.id) ? 'text-[#9B96AD]' : 'text-[#EDE9F7]'"
          >
            {{ entry.needAmount }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { Check } from "lucide-vue-next";

const props = defineProps({
  nonCraftable: { type: Array, default: () => [] },
  checkedIds: { type: Object, required: true },
});

defineEmits(["toggle-check"]);

const { t } = useI18n();

const displayList = computed(() => props.nonCraftable.filter((entry) => !entry?.isCrystal));
</script>
