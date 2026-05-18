<template>
  <header class="sticky top-0 z-10 border-b border-[#38364A] bg-[#252430] shadow-[0_2px_10px_rgba(0,0,0,0.4)]">
    <div class="mx-auto flex max-w-3xl items-center justify-between px-4 py-3">
      <span class="text-sm font-semibold text-[#EDE9F7]">{{ t("app.title") }}</span>

      <div class="flex items-center gap-1">
        <button
          type="button"
          class="mr-1 flex h-7 w-7 items-center justify-center rounded-full text-[#9B96AD] transition-colors hover:bg-[#38364A] hover:text-[#EDE9F7]"
          :title="t('onboarding.reopen')"
          @click="$emit('open-help')"
        >
          <Info :size="14" />
        </button>

        <button
          v-for="lang in langs"
          :key="lang.code"
          type="button"
          class="rounded-lg px-2.5 py-1 text-xs transition-colors"
          :class="locale === lang.code
            ? 'bg-[#4A4858] text-[#EDE9F7]'
            : 'text-[#9B96AD] hover:bg-[#38364A] hover:text-[#EDE9F7]'"
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

defineEmits(["open-help"]);

const { t, locale } = useI18n();

const langs = [
  { code: "zh-CN", label: "中文" },
  { code: "en", label: "EN" },
  { code: "ja", label: "日本語" },
];
</script>
