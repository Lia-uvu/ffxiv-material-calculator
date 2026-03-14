<template>
  <div class="relative">
    <MaterialsToolbar
      :copy-success="copySuccess"
      @collapse-all="emit('collapse-all')"
      @expand-all="emit('expand-all')"
      @reset-materials="onResetMaterials"
      @copy-materials="handleCopyMaterials"
    />

    <div class="relative z-10 -mt-4 rounded-2xl border border-[#4A4858] bg-[#3B3A47] px-4 pt-3 pb-5 shadow-[0_0_16px_rgba(0,0,0,0.45)]">
      <CanCraftSection
        :craftable="ui.craftable"
        :checked-ids="checkedIds"
        :expand-order="expandOrder"
        @toggle-check="emit('toggle-check', $event)"
        @toggle-expand="emit('toggle-expand', $event)"
      />

      <NotCraftSection
        :non-craftable="ui.nonCraftable"
        :checked-ids="checkedIds"
        @toggle-check="emit('toggle-check', $event)"
      />

      <CrystalsSection :crystals="crystals" />
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import { useI18n } from "vue-i18n";
import MaterialsToolbar from "./MaterialsToolbar.vue";
import CanCraftSection from "./CanCraftSection.vue";
import NotCraftSection from "./NotCraftSection.vue";
import CrystalsSection from "./CrystalsSection.vue";

const props = defineProps({
  ui: { type: Object, required: true },
  checkedIds: { type: Object, required: true },
  expandOrder: { type: Object, default: () => new Map() },
  exportText: { type: String, default: "" },
});

const emit = defineEmits(["toggle-expand", "collapse-all", "expand-all", "toggle-check", "reset-materials"]);
const { t } = useI18n();

const copySuccess = ref(false);
let copyTimer = null;

const crystals = computed(() => {
  const craftable = props.ui?.craftable ?? [];
  const nonCraftable = props.ui?.nonCraftable ?? [];
  const out = [];
  const seen = new Set();

  function push(entry) {
    if (!entry?.isCrystal) return;
    if (seen.has(entry.id)) return;
    seen.add(entry.id);
    out.push(entry);
  }

  for (const entry of craftable) push(entry);
  for (const entry of nonCraftable) push(entry);

  return out;
});

function fallbackCopy(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "readonly");
  textarea.style.position = "absolute";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}

async function handleCopyMaterials() {
  const text = props.exportText?.trim();
  if (!text) return;

  if (navigator?.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      fallbackCopy(text);
    }
  } else {
    fallbackCopy(text);
  }

  showCopySuccess();
}

function showCopySuccess() {
  copySuccess.value = true;
  if (copyTimer) window.clearTimeout(copyTimer);
  copyTimer = window.setTimeout(() => {
    copySuccess.value = false;
  }, 2000);
}

function onResetMaterials() {
  const ok = window.confirm(t("materials.resetConfirm"));
  if (!ok) return;
  emit("reset-materials");
}

onBeforeUnmount(() => {
  if (copyTimer) window.clearTimeout(copyTimer);
});
</script>
