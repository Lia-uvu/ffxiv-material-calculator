<template>
  <div>
    <div class="mt-6 mb-3 flex items-baseline justify-between">
      <div class="text-sm font-semibold text-[#EDE9F7]">{{ t("materials.crystals") }}</div>
      <div class="text-xs text-[#9B96AD]">
        {{ t("common.itemCount", { count: crystals.length }) }}
      </div>
    </div>

    <div v-if="crystals.length === 0">
      <span class="inline-flex items-center rounded-full bg-[#3A3547] px-3 py-1 text-xs text-[#6B677A]">{{ t("materials.noCrystals") }}</span>
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="group in crystalGroups"
        :key="group.tier"
        class="flex items-start gap-3"
      >
        <span class="w-10 shrink-0 pt-1.5 text-xs text-[#9B96AD]">
          {{ group.label }}
        </span>
        <div class="flex flex-wrap gap-1.5">
          <span
            v-for="crystal in group.items"
            :key="crystal.id"
            class="inline-flex items-center gap-1 rounded-full bg-[#3A3547] px-3 py-1 text-xs text-[#B4A5C8]"
          >
            <span>{{ crystal.elementName }}</span>
            <span class="text-[#9B96AD]">×{{ crystal.needAmount }}</span>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { getCrystalElementName, getCrystalTier } from "../../utils/crystalUtils";

const props = defineProps({
  crystals: { type: Array, default: () => [] },
});

const { t, locale } = useI18n();

const TIER_ORDER = ["shard", "crystal", "cluster"];

const crystalGroups = computed(() => {
  const currentLocale = locale.value;
  const grouped = { shard: [], crystal: [], cluster: [] };

  for (const crystal of props.crystals ?? []) {
    const tier = getCrystalTier(crystal.id);
    grouped[tier].push({
      ...crystal,
      elementName: getCrystalElementName(crystal.name, currentLocale),
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
