<template>
  <div class="relative">
    <Search
      class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[#6B677A]"
      :size="15"
    />
    <input
      class="h-10 w-full rounded-xl border border-[#5A5868] bg-[#302F3B] pl-8 pr-3 text-sm text-[#EDE9F7] placeholder-[#6B677A] outline-none shadow-[0_0_0_1px_rgba(90,88,104,0.35)] transition-shadow duration-150 focus:border-[#B4A5C8]/70 focus:shadow-[0_0_0_3px_rgba(180,165,200,0.2)]"
      :placeholder="t('search.placeholder')"
      :value="props.query"
      @input="onInput"
    />
  </div>
</template>

<script setup>
import { Search } from "lucide-vue-next";
import { useI18n } from "vue-i18n";

const props = defineProps({
  query: { type: String, default: "" },
});

const emit = defineEmits(["update:query"]);
const { t } = useI18n();

function onInput(e) {
  emit("update:query", e.target.value);
}
</script>
