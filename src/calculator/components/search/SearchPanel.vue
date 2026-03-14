<template>
  <div ref="searchContainerRef" class="relative">
    <ItemSearchBar :query="query" @update:query="emit('update:query', $event)" />

    <p v-if="!query" class="mt-1.5 px-1 text-xs text-[#9B96AD]">
      {{ t("search.hintCtrl") }}
    </p>

    <ItemSearchResults
      :results="results"
      :target-amounts="targetAmounts"
      :ctrl-pressed="ctrlPressed"
      @select="emit('select', $event)"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";
import ItemSearchBar from "./ItemSearchBar.vue";
import ItemSearchResults from "./ItemSearchResults.vue";

const props = defineProps({
  query: { type: String, default: "" },
  results: { type: Array, default: () => [] },
  targetAmounts: { type: Map, default: () => new Map() },
});

const emit = defineEmits(["update:query", "select"]);
const { t } = useI18n();

const ctrlPressed = ref(false);
const searchContainerRef = ref(null);

function onKeyDown(e) {
  if (e.key === "Control") ctrlPressed.value = true;
}

function onKeyUp(e) {
  if (e.key === "Control") ctrlPressed.value = false;
}

function onDocumentClick(e) {
  if (!props.query) return;
  if (searchContainerRef.value?.contains(e.target)) return;
  emit("update:query", "");
}

onMounted(() => {
  window.addEventListener("keydown", onKeyDown);
  window.addEventListener("keyup", onKeyUp);
  document.addEventListener("click", onDocumentClick);
});

onUnmounted(() => {
  window.removeEventListener("keydown", onKeyDown);
  window.removeEventListener("keyup", onKeyUp);
  document.removeEventListener("click", onDocumentClick);
});
</script>
