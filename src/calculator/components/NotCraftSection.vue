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

    <div v-if="displayList.length === 0" class="text-sm text-[#9B96AD]">
      {{ t("materials.nonCraftable.empty") }}
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="e in displayList"
        :key="'n-' + e.id"
        class="rounded-2xl border border-[#3C3A4A] p-3 bg-[#302F3B] cursor-default"
      >
        <div class="flex items-center gap-3">
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-[#9B96AD] truncate">
              {{ e.name }}
            </div>
            <div class="text-xs text-[#6B677A] mt-0.5">
              {{ e.source ?? t("common.placeholder") }}
            </div>
          </div>

          <div class="text-sm font-semibold tabular-nums text-[#6B677A] shrink-0">
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

const props = defineProps({
  nonCraftable: { type: Array, default: () => [] },
});

const { t } = useI18n();

const displayList = computed(() => props.nonCraftable.filter((e) => !e?.isCrystal));
</script>
