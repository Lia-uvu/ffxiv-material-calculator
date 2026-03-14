<template>
  <div
    v-if="results.length"
    class="search-results-popover absolute left-0 right-0 top-full z-50 mt-2 overflow-hidden rounded-2xl border border-[#4A4858] bg-[#3B3A47] shadow-lg"
  >
    <ul class="results-list max-h-72 overflow-y-auto py-1">
      <li v-for="item in results" :key="item.id">
        <button
          type="button"
          class="flex w-full items-center justify-between gap-3 px-3 py-2 text-left text-sm text-[#EDE9F7] hover:bg-[#4A4858]/60 focus:bg-[#4A4858]/60 focus:outline-none"
          @click="onSelect(item.id, $event)"
        >
          <span class="flex min-w-0 flex-1 items-center gap-1.5 overflow-hidden">
            <span class="truncate">{{ item.name }}</span>
            <span
              v-if="targetAmounts.has(item.id)"
              class="shrink-0 rounded-full border border-[#B4A5C8]/40 bg-[#B4A5C8]/15 px-1.5 py-0.5 text-xs font-medium text-[#B4A5C8]"
            >
              ×{{ targetAmounts.get(item.id) }}
            </span>
          </span>

          <span class="shrink-0 rounded-full border border-[#4A4858] bg-[#302F3B] px-2 py-0.5 text-xs text-[#9B96AD]">
            #{{ item.id }}
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

defineProps({
  results: {
    type: Array,
    default: () => [],
  },
  targetAmounts: {
    type: Map,
    default: () => new Map(),
  },
});

const emit = defineEmits(["select"]);
const { t } = useI18n();

function onSelect(id, event) {
  emit("select", { id, ctrlKey: event.ctrlKey });
}
</script>

<style scoped>
.results-list {
  scrollbar-width: thin;
  scrollbar-color: #4a4858 transparent;
  overscroll-behavior-y: contain;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-y;
}

.search-results-popover {
  overscroll-behavior: contain;
}
.results-list::-webkit-scrollbar {
  width: 4px;
}
.results-list::-webkit-scrollbar-track {
  background: transparent;
}
.results-list::-webkit-scrollbar-thumb {
  background-color: #4a4858;
  border-radius: 9999px;
}
.results-list::-webkit-scrollbar-thumb:hover {
  background-color: #5c5a6a;
}
</style>
