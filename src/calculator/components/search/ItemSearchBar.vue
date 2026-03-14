<template>
  <div class="relative flex items-center gap-2">
    <button
      type="button"
      class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[#4A4858] outline-none transition-colors duration-150"
      :class="props.pinned
        ? 'bg-[#3B3A47] text-[#E8D07A] hover:bg-[#3B3A47]'
        : 'bg-[#302F3B] text-[#9B96AD] opacity-85 hover:bg-[#3B3A47]'"
      :title="t('search.pinToggle', { state: props.pinned ? t('search.multiSelectStateOn') : t('search.multiSelectStateOff') })"
      @click="emit('toggle-pinned')"
    >
      <Pin :size="15" :stroke-width="props.pinned ? 2.4 : 2" />
    </button>

    <div class="relative min-w-0 flex-1">
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
  </div>
</template>

<script setup>
import { Search, Pin } from "lucide-vue-next";
import { useI18n } from "vue-i18n";

const props = defineProps({
  query: { type: String, default: "" },
  pinned: { type: Boolean, default: false },
});

const emit = defineEmits(["update:query", "toggle-pinned"]);
const { t } = useI18n();

function onInput(e) {
  emit("update:query", e.target.value);
}
</script>
