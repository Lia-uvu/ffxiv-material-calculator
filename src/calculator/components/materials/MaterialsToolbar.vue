<template>
  <div class="flex items-center justify-between rounded-t-2xl border border-[#38364A] bg-[#252430] px-4 pt-2.5 pb-4">
    <div class="text-sm font-semibold text-[#EDE9F7]">{{ t("materials.title") }}</div>

    <div class="flex items-center gap-1">
      <button
        type="button"
        class="flex h-8 w-8 items-center justify-center rounded-xl transition-colors hover:bg-[#38364A]"
        :title="t('materials.collapseAll')"
        @click="$emit('collapse-all')"
      >
        <ChevronsUp :size="16" color="#9B96AD" />
      </button>

      <button
        type="button"
        class="flex h-8 w-8 items-center justify-center rounded-xl transition-colors hover:bg-[#38364A]"
        :title="t('materials.expandAll')"
        @click="$emit('expand-all')"
      >
        <ChevronsDown :size="16" color="#9B96AD" />
      </button>

      <button
        type="button"
        class="flex h-8 w-8 items-center justify-center rounded-xl transition-colors hover:bg-[#E07070]/10"
        :title="t('materials.resetProgress')"
        @click="$emit('reset-materials')"
      >
        <RotateCcw :size="16" color="#E07070" />
      </button>

      <button
        type="button"
        class="flex h-8 w-8 items-center justify-center rounded-xl transition-colors hover:bg-[#38364A]"
        :title="copySuccess ? t('materials.copySuccess') : t('materials.copyList')"
        @click="$emit('copy-materials')"
      >
        <Check v-if="copySuccess" :size="16" color="#B4A5C8" />
        <Copy v-else :size="16" color="#9B96AD" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from "vue-i18n";
import { ChevronsUp, ChevronsDown, RotateCcw, Copy, Check } from "lucide-vue-next";

defineProps({
  copySuccess: { type: Boolean, default: false },
});

defineEmits(["collapse-all", "expand-all", "reset-materials", "copy-materials"]);

const { t } = useI18n();
</script>
