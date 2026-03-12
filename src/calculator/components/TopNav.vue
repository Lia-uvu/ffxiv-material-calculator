<!-- TopNav.vue -->
<template>
  <header class="sticky top-0 z-10 bg-[#252430] border-b border-[#38364A] shadow-[0_2px_10px_rgba(0,0,0,0.4)]">
    <div class="mx-auto max-w-3xl px-4 py-3 flex items-center justify-between">
      <span class="text-sm font-semibold text-[#EDE9F7]">{{ t("app.title") }}</span>

      <div class="flex items-center gap-1">
        <!-- 使用说明按钮 -->
        <button
          type="button"
          class="mr-1 h-7 w-7 rounded-full flex items-center justify-center text-[#9B96AD] hover:text-[#EDE9F7] hover:bg-[#38364A] transition-colors"
          :title="t('onboarding.reopen')"
          @click="open()"
        >
          <Info :size="14" />
        </button>

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
import { Info } from "lucide-vue-next";
import { useOnboarding } from "../composables/useOnboarding.js";

const { t, locale } = useI18n();
const { open } = useOnboarding();

const langs = [
  { code: "zh-CN", label: "中文" },
  { code: "en", label: "EN" },
  { code: "ja", label: "日本語" },
];
</script>
