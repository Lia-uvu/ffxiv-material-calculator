<template>
  <section class="rounded-2xl border border-[#3D3B4A] bg-[#3B3A47] p-5 shadow-[0_4px_16px_rgba(0,0,0,0.3)]">
    <div class="flex items-baseline justify-between gap-3">
      <h2 class="text-lg font-semibold tracking-tight text-[#EDE9F7]">{{ t("targets.title") }}</h2>

      <div class="flex items-center gap-2">
        <p class="text-xs text-[#9B96AD]">{{ t("targets.total", { count: totalAmount }) }}</p>

        <button
          v-if="targets.length || outfitBundles.length"
          type="button"
          class="inline-flex h-8 items-center justify-center rounded-xl border border-[#4A4858] bg-[#302F3B] px-3 text-xs text-[#9B96AD] transition-colors hover:bg-[#4A4858]"
          :aria-label="t('targets.clearAria')"
          :title="t('targets.clearTitle')"
          @click="onClear"
        >
          {{ t("targets.clear") }}
        </button>
      </div>
    </div>

    <div
      v-if="!targets.length && !outfitBundles.length"
      class="mt-4 flex items-center gap-3 rounded-xl bg-[#302F3B] px-3 py-2 text-sm text-[#9B96AD]"
    >
      {{ t("targets.empty") }}
    </div>

    <div v-else class="mt-4 space-y-2">
      <!-- Outfit bundles (from set selector) -->
      <div
        v-for="bundle in outfitBundles"
        :key="bundle.uid"
        class="overflow-hidden rounded-xl border border-[#4A4858] bg-[#302F3B]"
      >
        <!-- Bundle header row -->
        <div class="flex items-center gap-2 px-3 py-2">
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-1.5">
              <span class="truncate text-sm font-medium text-[#EDE9F7]">{{ bundle.setLabel }}</span>
              <!-- Job badge -->
              <span class="shrink-0 rounded border border-[#5C5470] bg-[#3B3A47] px-1.5 py-0.5 text-[10px] font-medium text-[#B4A5C8]">
                {{ bundle.jobKey }}
              </span>
              <!-- Item count badge -->
              <span class="shrink-0 text-[10px] text-[#6B677A]">
                {{ bundle.itemCount }}{{ t("outfitSets.pieces") }}
              </span>
            </div>
          </div>

          <div class="flex shrink-0 items-center gap-1">
            <!-- Weapon toggle (only if weapons exist for this job) -->
            <button
              v-if="bundle.hasWeapon"
              type="button"
              class="rounded border px-1.5 py-1 text-[11px] transition-colors"
              :class="bundle.includeWeapon
                ? 'border-[#B4A5C8]/40 bg-[#3B3A47] text-[#EDE9F7]'
                : 'border-[#38364A] bg-transparent text-[#6B677A]'"
              :title="t('targets.includeWeapon')"
              @click="$emit('toggle-weapon', bundle.uid)"
            >
              {{ t("targets.includeWeapon") }}
            </button>

            <!-- Expand toggle -->
            <button
              type="button"
              class="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-[#4A4858] text-[#6B677A] transition-colors hover:bg-[#4A4858] hover:text-[#9B96AD]"
              :title="bundle.expanded ? t('targets.bundleCollapse') : t('targets.bundleExpand')"
              @click="$emit('toggle-bundle-expand', bundle.uid)"
            >
              <ChevronDown
                :size="13"
                class="transition-transform duration-150"
                :class="{ 'rotate-180': bundle.expanded }"
              />
            </button>

            <!-- Remove bundle -->
            <button
              type="button"
              class="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-[#4A4858] text-[#6B677A] transition-colors hover:border-[#E07070]/40 hover:bg-[#E07070]/10 hover:text-[#E07070]"
              :aria-label="t('targets.removeAria')"
              :title="t('targets.removeTitle')"
              @click="$emit('remove-bundle', bundle.uid)"
            >
              <X :size="13" />
            </button>
          </div>
        </div>

        <!-- Expanded: individual item list -->
        <Transition name="bundle-expand">
          <div v-if="bundle.expanded" class="border-t border-[#3D3B4A]">
            <ul class="divide-y divide-[#3D3B4A]">
              <li
                v-for="item in bundle.items"
                :key="item.id"
                class="flex items-center gap-2 px-3 py-1.5"
              >
                <span class="min-w-0 flex-1 truncate text-xs text-[#9B96AD]">{{ item.name }}</span>
                <span
                  v-if="item.isWeapon"
                  class="shrink-0 rounded bg-[#3B3A47] px-1 py-0.5 text-[9px] text-[#6B677A]"
                >
                  {{ t("targets.weaponLabel") }}
                </span>
              </li>
            </ul>
          </div>
        </Transition>
      </div>

      <!-- Individual item targets -->
      <ul v-if="targets.length" class="space-y-2">
        <li
          v-for="target in targets"
          :key="target.id"
          class="flex items-center gap-3 rounded-xl border border-[#4A4858] bg-[#302F3B] px-3 py-2"
        >
          <span class="min-w-0 flex-1 truncate text-sm font-medium text-[#EDE9F7]">{{ target.name }}</span>

          <input
            class="h-9 w-20 rounded-xl border border-[#4A4858] bg-[#2D2C34] px-2 text-sm text-[#EDE9F7] outline-none focus:ring-2 focus:ring-[#B4A5C8]/30"
            type="number"
            min="1"
            step="1"
            :value="target.amount ?? 1"
            @input="onAmountInput(target.id, $event)"
            @blur="onAmountBlur(target.id, $event)"
          />

          <button
            type="button"
            class="inline-flex h-9 items-center justify-center rounded-xl border border-[#4A4858] bg-[#302F3B] px-3 text-sm text-[#9B96AD] transition-colors hover:bg-[#4A4858]"
            :aria-label="t('targets.removeAria')"
            :title="t('targets.removeTitle')"
            @click="onRemove(target.id)"
          >
            {{ t("targets.remove") }}
          </button>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { computed, toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { ChevronDown, X } from "lucide-vue-next";
import { clampPositiveInteger } from "../../utils/amountUtils";

const props = defineProps({
  targets: {
    type: Array,
    default: () => [],
  },
  outfitBundles: {
    type: Array,
    default: () => [],
  },
});

const { targets, outfitBundles } = toRefs(props);
const { t } = useI18n();

const totalAmount = computed(() => {
  const individualTotal = targets.value.reduce((sum, item) => sum + (item.amount ?? 1), 0);
  const bundleTotal = outfitBundles.value.reduce((sum, b) => sum + b.itemCount, 0);
  return individualTotal + bundleTotal;
});

const emit = defineEmits([
  "remove",
  "update-amount",
  "clear",
  "remove-bundle",
  "toggle-weapon",
  "toggle-bundle-expand",
]);

function onRemove(id) {
  emit("remove", id);
}

function onClear() {
  emit("clear");
}

function onAmountInput(id, e) {
  const next = clampPositiveInteger(e.target.value);
  emit("update-amount", { id, amount: next });
}

function onAmountBlur(id, e) {
  const next = clampPositiveInteger(e.target.value);
  e.target.value = String(next);
  emit("update-amount", { id, amount: next });
}
</script>

<style scoped>
.bundle-expand-enter-active,
.bundle-expand-leave-active {
  overflow: hidden;
  transition: max-height 0.2s ease, opacity 0.15s ease;
  max-height: 400px;
}
.bundle-expand-enter-from,
.bundle-expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
