<template>
  <div
    v-if="results.length"
    class="absolute left-0 right-0 top-full z-50 mt-2 overflow-hidden rounded-2xl border border-[#4A4858] bg-[#3B3A47] shadow-lg"
  >
    <ul class="max-h-72 overflow-auto py-1">
      <li v-for="it in results" :key="it.id">
        <button
          type="button"
          class="flex w-full items-center justify-between gap-3 px-3 py-2 text-left text-sm text-[#EDE9F7] hover:bg-[#4A4858]/60 focus:bg-[#4A4858]/60 focus:outline-none"
          @click="onSelect(it.id)"
        >
          <span class="min-w-0 flex-1 truncate">{{ it.name }}</span>
          <span
            class="shrink-0 rounded-full border border-[#4A4858] bg-[#302F3B] px-2 py-0.5 text-xs text-[#9B96AD]"
          >
            #{{ it.id }}
          </span>
        </button>
      </li>
    </ul>

    <div class="border-t border-[#4A4858] px-3 py-2 text-xs text-[#6B677A]">
      {{ t("search.hint") }}
    </div>
  </div>
</template>

<script setup>
import { useI18n } from "vue-i18n";

const props = defineProps({
  results: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["select"]);
const { t } = useI18n();

function onSelect(id) {
  emit("select", id);
}
</script>
