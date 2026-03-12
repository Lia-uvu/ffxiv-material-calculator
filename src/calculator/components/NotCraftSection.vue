<!-- NotCraftSection.vue -->
<template>
  <div>
    <div class="flex items-baseline justify-between mt-2 mb-2">
      <div class="text-sm font-semibold text-[#EDE9F7]">
        {{ t("materials.nonCraftable.title") }}
      </div>
      <div class="text-xs text-[#9B96AD]">
        {{ t("common.itemCount", { count: displayList.length }) }}
      </div>
    </div>

    <div v-if="displayList.length === 0" class="rounded-2xl border border-[#5C5470] p-3 bg-[#4A4858] text-sm text-[#9B96AD]">
      {{ t("materials.nonCraftable.empty") }}
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="e in displayList"
        :key="'n-' + e.id"
        class="rounded-2xl border border-[#5C5470] p-3 bg-[#4A4858] cursor-default"
      >
        <div class="flex items-center gap-3">
          <!-- Checkbox (circle) -->
          <button
            type="button"
            class="shrink-0 h-5 w-5 rounded-full border-2 flex items-center justify-center transition-colors"
            :class="checkedIds.has(e.id)
              ? 'bg-[#B4A5C8] border-[#B4A5C8]'
              : 'border-[#7A7589] bg-transparent hover:border-[#B4A5C8]'"
            @click="$emit('toggle-check', e.id)"
            :title="t('common.completed')"
          >
            <Check v-if="checkedIds.has(e.id)" :size="11" color="#2D2C34" :stroke-width="3" />
          </button>

          <div class="flex-1 min-w-0">
            <div
              class="text-sm font-medium truncate"
              :class="checkedIds.has(e.id) ? 'line-through text-[#9B96AD]' : 'text-[#EDE9F7]'"
            >
              {{ e.name }}
            </div>
            <div class="text-xs mt-0.5" :class="checkedIds.has(e.id) ? 'text-[#9B96AD] opacity-40' : 'text-[#9B96AD]'">
              {{ e.source ?? t("common.placeholder") }}
            </div>
          </div>

          <div
            class="text-sm font-semibold tabular-nums shrink-0"
            :class="checkedIds.has(e.id) ? 'text-[#9B96AD]' : 'text-[#EDE9F7]'"
          >
            {{ e.needAmount }}
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
  checkedIds: { type: Object, required: true }, // Set
});

defineEmits(["toggle-check"]);

const { t } = useI18n();

const displayList = computed(() => props.nonCraftable.filter((e) => !e?.isCrystal));
</script>
