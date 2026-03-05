<!-- ItemSearchInput.vue -->
<template>
  <input
    class="h-10 w-full rounded-xl border border-[#4A4858] bg-[#302F3B] px-3 text-sm text-[#EDE9F7] placeholder-[#6B677A] outline-none focus:ring-2 focus:ring-[#B4A5C8]/30"
    :placeholder="t('search.placeholder')"
    :value="props.query"
    @input="onInput"
  />
</template>

<script setup>
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
