<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/60 px-2 backdrop-blur-sm"
      >
        <div class="flex w-full max-w-sm items-center gap-2">
          <button
            v-if="page > 0"
            type="button"
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-[#9B96AD] transition-colors hover:bg-[#38364A] hover:text-[#EDE9F7]"
            @click="page--"
          >
            <ChevronLeft :size="20" />
          </button>
          <span v-else class="w-10 shrink-0" />

          <div class="flex-1 overflow-hidden rounded-2xl border border-[#4A4858] bg-[#2D2C34] shadow-[0_8px_40px_rgba(0,0,0,0.7)]">
            <div class="border-b border-[#38364A] px-5 pt-5 pb-3">
              <div class="text-sm font-semibold text-[#EDE9F7]">
                {{ page === 0 ? t('onboarding.page1Title') : t('onboarding.page2Title') }}
              </div>
              <div class="mt-2 flex items-center gap-1.5">
                <span
                  v-for="i in 2"
                  :key="i"
                  class="h-1.5 w-1.5 rounded-full transition-colors"
                  :class="page === i - 1 ? 'bg-[#B4A5C8]' : 'bg-[#4A4858]'"
                />
              </div>
            </div>

            <div class="px-5 py-4">
              <template v-if="page === 0">
                <div class="relative -ml-5">
                  <div class="rounded-r-2xl border border-[#5C5470] border-l-0 bg-[#4A4858] p-3 pl-5">
                    <div class="flex items-center gap-3">
                      <button class="h-5 w-5 shrink-0 rounded-full border-2 border-[#7A7589] bg-transparent" tabindex="-1" />
                      <div class="min-w-0 flex-1">
                        <div class="flex items-center gap-2">
                          <div class="truncate text-sm font-medium text-[#EDE9F7]">{{ t('onboarding.exampleItem') }}</div>
                          <span class="shrink-0 rounded-full bg-[#4A4560] px-1.5 py-0.5 text-[10px] text-[#C8BFDA]">
                            {{ t('materials.craftable.collapsed') }}
                          </span>
                        </div>
                        <div class="mt-0.5 text-xs text-[#9B96AD]">{{ t('jobs.BLACKSMITH') }}</div>
                      </div>
                      <div class="shrink-0 text-right tabular-nums leading-tight">
                        <div class="text-sm font-semibold text-[#EDE9F7]">{{ t('materials.needLabel', { n: 12 }) }}</div>
                        <div class="text-xs text-[#9B96AD]">{{ t('materials.craftLabel', { n: 4 }) }}</div>
                      </div>
                      <button class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl" tabindex="-1">
                        <Link2 :size="20" color="#B4A5C8" />
                      </button>
                    </div>
                  </div>
                  <div class="pointer-events-none absolute inset-y-0 left-0 w-28 bg-gradient-to-r from-[#2D2C34] to-transparent" />
                </div>

                <div class="flex items-center gap-2 py-2.5">
                  <div class="h-px flex-1 bg-[#38364A]" />
                  <div class="flex items-center gap-1 text-xs font-medium text-[#B4A5C8]">
                    <ChevronDown :size="13" />
                    <span>{{ t('onboarding.clickHint') }}</span>
                  </div>
                  <div class="h-px flex-1 bg-[#38364A]" />
                </div>

                <div class="relative -ml-5 mb-2">
                  <div class="rounded-r-2xl border border-[#38364A] border-l-0 bg-[#2A2933] p-3 pl-5">
                    <div class="flex items-center gap-3">
                      <button class="h-5 w-5 shrink-0 rounded-full border-2 border-[#7A7589] bg-transparent" tabindex="-1" />
                      <div class="min-w-0 flex-1">
                        <div class="flex items-center gap-2">
                          <div class="truncate text-sm font-medium text-[#EDE9F7]">{{ t('onboarding.exampleItem') }}</div>
                          <span class="shrink-0 rounded-full bg-[#2E2D3A] px-1.5 py-0.5 text-[10px] text-[#6B677A]">
                            {{ t('materials.craftable.expanded') }}
                          </span>
                        </div>
                        <div class="mt-0.5 text-xs text-[#9B96AD]">{{ t('jobs.BLACKSMITH') }}</div>
                      </div>
                      <div class="shrink-0 text-right tabular-nums leading-tight">
                        <div class="text-sm font-semibold text-[#EDE9F7]">{{ t('materials.craftLabel', { n: 4 }) }}</div>
                        <div class="text-xs text-[#9B96AD]">{{ t('materials.needLabel', { n: 12 }) }}</div>
                      </div>
                      <button class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl" tabindex="-1">
                        <Link2Off :size="20" color="#E8D07A" />
                      </button>
                    </div>
                  </div>
                  <div class="pointer-events-none absolute inset-y-0 left-0 w-28 bg-gradient-to-r from-[#2D2C34] to-transparent" />
                </div>

                <div class="mb-3 ml-4 space-y-1">
                  <div class="relative -mr-5">
                    <div class="rounded-l-2xl border border-[#5C5470] border-r-0 bg-[#4A4858] p-2 pr-5">
                      <div class="flex items-center gap-2">
                        <button class="h-4 w-4 shrink-0 rounded-full border border-[#7A7589] bg-transparent" tabindex="-1" />
                        <div class="min-w-0 flex-1">
                          <div class="truncate text-xs font-medium text-[#EDE9F7]">{{ t('onboarding.exampleSub1') }}</div>
                          <div class="mt-0.5 text-[10px] text-[#9B96AD]">{{ t('obtainMethods.GATHER_MINER') }}</div>
                        </div>
                        <div class="shrink-0 text-xs font-semibold tabular-nums text-[#EDE9F7]">24</div>
                      </div>
                    </div>
                    <div class="pointer-events-none absolute inset-y-0 right-0 w-24 bg-gradient-to-l from-[#2D2C34] to-transparent" />
                  </div>

                  <div class="relative -mr-5">
                    <div class="rounded-l-2xl border border-[#5C5470] border-r-0 bg-[#4A4858] p-2 pr-5">
                      <div class="flex items-center gap-2">
                        <button class="h-4 w-4 shrink-0 rounded-full border border-[#7A7589] bg-transparent" tabindex="-1" />
                        <div class="min-w-0 flex-1">
                          <div class="truncate text-xs font-medium text-[#EDE9F7]">{{ t('onboarding.exampleSub2') }}</div>
                          <div class="mt-0.5 text-[10px] text-[#9B96AD]">{{ t('obtainMethods.GATHER_MINER') }}</div>
                        </div>
                        <div class="shrink-0 text-xs font-semibold tabular-nums text-[#EDE9F7]">8</div>
                      </div>
                    </div>
                    <div class="pointer-events-none absolute inset-y-0 right-0 w-24 bg-gradient-to-l from-[#2D2C34] to-transparent" />
                  </div>
                </div>

                <p class="text-xs leading-relaxed text-[#9B96AD]">
                  {{ t('onboarding.page1Desc') }}
                </p>
              </template>

              <template v-else>
                <div class="mb-3 rounded-xl border border-[#4A4858] bg-[#3B3A47] px-4 py-3">
                  <div class="flex items-start gap-3">
                    <div class="shrink-0 pt-0.5">
                      <div class="flex items-center gap-1">
                        <kbd class="rounded border border-[#4A4858] bg-[#252430] px-1.5 py-0.5 font-mono text-[10px] leading-none text-[#B4A5C8]">Ctrl</kbd>
                        <span class="text-[10px] text-[#6B677A]">+</span>
                        <kbd class="rounded border border-[#4A4858] bg-[#252430] px-1.5 py-0.5 font-mono text-[10px] leading-none text-[#B4A5C8]">Click</kbd>
                      </div>
                      <div class="mt-1 space-y-1">
                        <div class="flex w-28 items-center gap-1.5 rounded-lg border border-[#4A4858] bg-[#252430] px-2 py-1">
                          <span class="h-1.5 w-1.5 shrink-0 rounded-full bg-[#B4A5C8]" />
                          <span class="truncate text-[10px] text-[#EDE9F7]">{{ t('onboarding.exampleItem') }}</span>
                        </div>
                        <div class="flex w-28 items-center gap-1.5 rounded-lg border border-[#38364A] bg-[#2D2C34] px-2 py-1">
                          <span class="h-1.5 w-1.5 shrink-0 rounded-full bg-[#4A4858]" />
                          <span class="truncate text-[10px] text-[#9B96AD]">{{ t('onboarding.exampleSub1') }}</span>
                        </div>
                      </div>
                    </div>
                    <div>
                      <div class="mb-1 text-xs font-medium text-[#EDE9F7]">{{ t('onboarding.shortcutCtrlTitle') }}</div>
                      <p class="text-[11px] leading-relaxed text-[#9B96AD]">{{ t('onboarding.shortcutCtrlDesc') }}</p>
                    </div>
                  </div>
                </div>

                <div class="rounded-xl border border-[#4A4858] bg-[#3B3A47] px-4 py-3">
                  <div class="flex items-start gap-3">
                    <div class="shrink-0 pt-0.5">
                      <div class="flex h-8 w-8 items-center justify-center rounded-xl border border-[#4A4858] bg-[#252430]">
                        <Copy :size="15" color="#9B96AD" />
                      </div>
                    </div>
                    <div>
                      <div class="mb-1 text-xs font-medium text-[#EDE9F7]">{{ t('onboarding.copyTitle') }}</div>
                      <p class="text-[11px] leading-relaxed text-[#9B96AD]">{{ t('onboarding.copyDesc') }}</p>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>

          <button
            v-if="page < 1"
            type="button"
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-[#9B96AD] transition-colors hover:bg-[#38364A] hover:text-[#EDE9F7]"
            @click="page++"
          >
            <ChevronRight :size="20" />
          </button>
          <span v-else class="w-10 shrink-0" />
        </div>

        <button
          type="button"
          class="mt-5 flex h-9 w-9 items-center justify-center rounded-full border border-[#4A4858] text-[#9B96AD] transition-colors hover:border-[#9B96AD] hover:text-[#EDE9F7]"
          @click="$emit('close')"
        >
          <X :size="16" />
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { Link2, Link2Off, ChevronDown, ChevronLeft, ChevronRight, X, Copy } from "lucide-vue-next";

const props = defineProps({
  isOpen: { type: Boolean, default: false },
});

defineEmits(["close"]);

const { t } = useI18n();
const page = ref(0);

watch(
  () => props.isOpen,
  (value) => {
    if (value) page.value = 0;
  }
);
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
