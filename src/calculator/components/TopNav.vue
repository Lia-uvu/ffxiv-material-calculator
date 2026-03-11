<!-- TopNav.vue -->
<template>
  <header class="sticky top-0 z-10 bg-[#252430] border-b border-[#38364A] shadow-[0_2px_10px_rgba(0,0,0,0.4)]">
    <div class="mx-auto max-w-3xl px-4 py-3 flex items-center justify-between">
      <span class="text-sm font-semibold text-[#EDE9F7]">{{ t("app.title") }}</span>

      <div class="flex items-center gap-1">
        <button
          v-for="lang in langs"
          :key="lang.code"
          type="button"
          class="px-2.5 py-1 rounded-lg text-xs transition-colors"
          :class="locale === lang.code
            ? 'bg-[#4A4858] text-[#EDE9F7]'
            : 'text-[#9B96AD] hover:text-[#EDE9F7] hover:bg-[#38364A]'"
          @click="locale = lang.code"
        >
          {{ lang.label }}
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useI18n } from "vue-i18n";

const { t, locale } = useI18n();

const langs = [
  { code: "zh-CN", label: "中文" },
  { code: "en", label: "EN" },
  { code: "ja", label: "日本語" },
];
</script>
