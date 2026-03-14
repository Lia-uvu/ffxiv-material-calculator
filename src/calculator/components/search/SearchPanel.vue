<template>
  <div ref="searchContainerRef" class="relative">
    <ItemSearchBar
      :query="query"
      :pinned="selectionPinned"
      @update:query="emit('update:query', $event)"
      @toggle-pinned="togglePinned"
    />

    <p v-if="!query" class="mt-1.5 px-1 text-xs text-[#9B96AD]">
      {{ t("search.hintCtrl") }}
    </p>

    <ItemSearchResults
      :results="results"
      :target-amounts="targetAmounts"
      :multi-select-mode="multiSelectMode"
      @select="onSelect"
    />
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from "vue";
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
const selectionPinned = ref(false);
const searchContainerRef = ref(null);

const multiSelectMode = computed(() => {
  if (selectionPinned.value) return "pinned";
  if (ctrlPressed.value) return "ctrl";
  return null;
});

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

function togglePinned() {
  selectionPinned.value = !selectionPinned.value;
}

function onSelect({ id, ctrlKey }) {
  emit("select", { id, keepOpen: selectionPinned.value || ctrlKey });
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
