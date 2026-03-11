<!-- MaterialsList.vue -->
<template>
  <div class="relative">
    <!-- 标题栏：完整圆角卡片，在下层，被内容卡片从下方压住只露出顶部 -->
    <div class="rounded-2xl bg-[#252430] border border-[#38364A] px-4 py-3 flex items-center justify-between">
      <div class="text-sm font-semibold text-[#EDE9F7]">{{ t("materials.title") }}</div>

      <div class="flex items-center gap-1">
        <button
          type="button"
          class="h-8 w-8 rounded-xl flex items-center justify-center hover:bg-[#38364A] transition-colors"
          :title="t('materials.collapseAll')"
          @click="$emit('collapse-all')"
        >
          <ChevronsUp :size="16" color="#9B96AD" />
        </button>

        <button
          type="button"
          class="h-8 w-8 rounded-xl flex items-center justify-center hover:bg-[#38364A] transition-colors"
          :title="t('materials.expandAll')"
          @click="$emit('expand-all')"
        >
          <ChevronsDown :size="16" color="#9B96AD" />
        </button>

        <button
          type="button"
          class="h-8 w-8 rounded-xl flex items-center justify-center hover:bg-[#E07070]/10 transition-colors"
          :title="t('materials.resetProgress')"
          @click="onResetMaterials"
        >
          <RotateCcw :size="16" color="#E07070" />
        </button>

        <button
          type="button"
          class="h-8 w-8 rounded-xl flex items-center justify-center hover:bg-[#38364A] transition-colors"
          :title="copySuccess ? t('materials.copySuccess') : t('materials.copyList')"
          @click="$emit('copy-materials')"
        >
          <Check v-if="copySuccess" :size="16" color="#B4A5C8" />
          <Copy v-else :size="16" color="#9B96AD" />
        </button>
      </div>
    </div>

    <!-- 内容卡片：z-10 在上层，-mt-2 压住标题卡片底部 -->
    <div class="relative z-10 rounded-2xl border border-[#4A4858] bg-[#3B3A47] -mt-2 pt-4 px-4 pb-4 shadow-[0_0_16px_rgba(0,0,0,0.45)]">
      <CanCraftSection
        :craftable="ui.craftable"
        :checked-ids="checkedIds"
        :expand-order="expandOrder"
        @toggle-check="toggleCheck"
        @toggle-expand="(id) => $emit('toggle-expand', id)"
      />

      <NotCraftSection
        :non-craftable="ui.nonCraftable"
        :checked-ids="checkedIds"
        @toggle-check="toggleCheck"
      />

      <!-- 水晶 -->
      <div class="flex items-baseline justify-between mt-6 mb-3">
        <div class="text-sm font-semibold text-[#EDE9F7]">{{ t("materials.crystals") }}</div>
        <div class="text-xs text-[#9B96AD]">
          {{ t("common.itemCount", { count: crystals.length }) }}
        </div>
      </div>

      <div v-if="crystals.length === 0">
        <span class="inline-flex items-center bg-[#3A3547] text-[#6B677A] rounded-full px-3 py-1 text-xs">无</span>
      </div>

      <div v-else class="space-y-2">
        <div
          v-for="group in crystalGroups"
          :key="group.tier"
          class="flex items-start gap-3"
        >
          <span class="text-xs text-[#9B96AD] w-10 shrink-0 pt-1.5">
            {{ group.label }}
          </span>
          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="c in group.items"
              :key="c.id"
              class="inline-flex items-center gap-1 bg-[#3A3547] text-[#B4A5C8] rounded-full px-3 py-1 text-xs"
            >
              <span>{{ c.elementName }}</span>
              <span class="text-[#9B96AD]">×{{ c.needAmount }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { ChevronsUp, ChevronsDown, RotateCcw, Copy, Check } from "lucide-vue-next";
import CanCraftSection from "./CanCraftSection.vue";
import NotCraftSection from "./NotCraftSection.vue";

const props = defineProps({
  ui: { type: Object, required: true },
  checkedIds: { type: Object, required: true },
  expandOrder: { type: Object, default: () => new Map() },
  copySuccess: { type: Boolean, default: false },
});

const emit = defineEmits([
  "toggle-expand",
  "collapse-all",
  "expand-all",
  "toggle-check",
  "clear-checked",
  "reset-materials",
  "copy-materials",
]);

function toggleCheck(id) {
  emit("toggle-check", id);
}

function onResetMaterials() {
  const ok = window.confirm(t("materials.resetConfirm"));
  if (!ok) return;
  emit("reset-materials");
}

const { t, locale } = useI18n();

const crystals = computed(() => {
  const craftable = props.ui?.craftable ?? [];
  const nonCraftable = props.ui?.nonCraftable ?? [];
  const out = [];
  const seen = new Set();
  const push = (e) => {
    if (!e?.isCrystal) return;
    if (seen.has(e.id)) return;
    seen.add(e.id);
    out.push(e);
  };
  for (const e of craftable) push(e);
  for (const e of nonCraftable) push(e);
  return out;
});

function getTier(id) {
  if (id <= 7) return "shard";
  if (id <= 13) return "crystal";
  return "cluster";
}

function getElementName(name, loc) {
  if (loc === "zh-CN") return name.split("之")[0];
  if (loc === "ja") return name.replace(/シャード|クリスタル|クラスター$/, "");
  return name.split(" ")[0];
}

const TIER_ORDER = ["shard", "crystal", "cluster"];

const crystalGroups = computed(() => {
  const loc = locale.value;
  const grouped = { shard: [], crystal: [], cluster: [] };

  for (const c of crystals.value) {
    const tier = getTier(c.id);
    grouped[tier].push({
      ...c,
      elementName: getElementName(c.name, loc),
    });
  }

  return TIER_ORDER
    .filter((tier) => grouped[tier].length > 0)
    .map((tier) => ({
      tier,
      label: t(`materials.crystalTiers.${tier}`),
      items: grouped[tier].sort((a, b) => a.id - b.id),
    }));
});
</script>
