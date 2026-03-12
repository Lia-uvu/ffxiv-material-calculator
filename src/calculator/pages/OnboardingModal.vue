<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/60 backdrop-blur-sm px-2"
      >
        <!-- 卡片行：左箭头 + 卡片 + 右箭头 -->
        <div class="flex items-center gap-2 w-full max-w-sm">

          <!-- 左箭头 -->
          <button
            v-if="page > 0"
            type="button"
            class="shrink-0 h-10 w-10 rounded-full flex items-center justify-center text-[#9B96AD] hover:text-[#EDE9F7] hover:bg-[#38364A] transition-colors"
            @click="page--"
          >
            <ChevronLeft :size="20" />
          </button>
          <span v-else class="shrink-0 w-10" />

          <!-- 卡片本体 -->
          <div class="flex-1 rounded-2xl bg-[#2D2C34] border border-[#4A4858] shadow-[0_8px_40px_rgba(0,0,0,0.7)] overflow-hidden">

            <!-- 标题栏 -->
            <div class="px-5 pt-5 pb-3 border-b border-[#38364A]">
              <div class="text-sm font-semibold text-[#EDE9F7]">
                {{ page === 0 ? t('onboarding.page1Title') : t('onboarding.page2Title') }}
              </div>
              <div class="flex items-center gap-1.5 mt-2">
                <span
                  v-for="i in 2"
                  :key="i"
                  class="w-1.5 h-1.5 rounded-full transition-colors"
                  :class="page === i - 1 ? 'bg-[#B4A5C8]' : 'bg-[#4A4858]'"
                />
              </div>
            </div>

            <!-- 内容区 -->
            <div class="px-5 py-4">

              <!-- ── Page 0：拆开说明 ── -->
              <template v-if="page === 0">

                <!-- 状态一：未拆 — 真实可制作材料行，右侧（链条图标端）可见 -->
                <div class="relative -ml-5">
                  <div class="rounded-r-2xl border border-[#5C5470] border-l-0 p-3 pl-5 bg-[#4A4858]">
                    <div class="flex items-center gap-3">
                      <button class="shrink-0 h-5 w-5 rounded-full border-2 border-[#7A7589] bg-transparent" tabindex="-1" />
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2">
                          <div class="text-sm font-medium truncate text-[#EDE9F7]">{{ t('onboarding.exampleItem') }}</div>
                          <span class="text-[10px] px-1.5 py-0.5 rounded-full shrink-0 bg-[#4A4560] text-[#C8BFDA]">
                            {{ t('materials.craftable.collapsed') }}
                          </span>
                        </div>
                        <div class="text-xs text-[#9B96AD] mt-0.5">{{ t('jobs.BLACKSMITH') }}</div>
                      </div>
                      <div class="text-right shrink-0 tabular-nums leading-tight">
                        <div class="text-sm font-semibold text-[#EDE9F7]">{{ t('materials.needLabel', { n: 12 }) }}</div>
                        <div class="text-xs text-[#9B96AD]">{{ t('materials.craftLabel', { n: 4 }) }}</div>
                      </div>
                      <button class="shrink-0 h-9 w-9 flex items-center justify-center rounded-xl" tabindex="-1">
                        <Link2 :size="20" color="#B4A5C8" />
                      </button>
                    </div>
                  </div>
                  <!-- 左侧虚焦遮罩：backdrop-blur 模糊 + 渐变淡出 -->
                  <div class="absolute inset-y-0 left-0 w-28 backdrop-blur-sm bg-gradient-to-r from-[#4A4858] via-[#4A4858]/80 to-transparent pointer-events-none" />
                </div>

                <!-- 过渡提示 -->
                <div class="flex items-center gap-2 py-2.5">
                  <div class="h-px flex-1 bg-[#38364A]" />
                  <div class="flex items-center gap-1 text-xs text-[#B4A5C8] font-medium">
                    <ChevronDown :size="13" />
                    <span>{{ t('onboarding.clickHint') }}</span>
                  </div>
                  <div class="h-px flex-1 bg-[#38364A]" />
                </div>

                <!-- 状态二：已拆 — 展开样式（深色背景）+ Link2Off -->
                <div class="relative -ml-5 mb-3">
                  <div class="rounded-r-2xl border border-[#38364A] border-l-0 p-3 pl-5 bg-[#2A2933]">
                    <div class="flex items-center gap-3">
                      <button class="shrink-0 h-5 w-5 rounded-full border-2 border-[#7A7589] bg-transparent" tabindex="-1" />
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2">
                          <div class="text-sm font-medium truncate text-[#EDE9F7]">{{ t('onboarding.exampleItem') }}</div>
                          <span class="text-[10px] px-1.5 py-0.5 rounded-full shrink-0 bg-[#2E2D3A] text-[#6B677A]">
                            {{ t('materials.craftable.expanded') }}
                          </span>
                        </div>
                        <div class="text-xs text-[#9B96AD] mt-0.5">{{ t('jobs.BLACKSMITH') }}</div>
                      </div>
                      <div class="text-right shrink-0 tabular-nums leading-tight">
                        <div class="text-sm font-semibold text-[#EDE9F7]">{{ t('materials.craftLabel', { n: 4 }) }}</div>
                        <div class="text-xs text-[#9B96AD]">{{ t('materials.needLabel', { n: 12 }) }}</div>
                      </div>
                      <button class="shrink-0 h-9 w-9 flex items-center justify-center rounded-xl" tabindex="-1">
                        <Link2Off :size="20" color="#E8D07A" />
                      </button>
                    </div>
                  </div>
                  <!-- 左侧虚焦遮罩：深色背景版本 -->
                  <div class="absolute inset-y-0 left-0 w-28 backdrop-blur-sm bg-gradient-to-r from-[#2A2933] via-[#2A2933]/80 to-transparent pointer-events-none" />
                </div>

                <!-- 展开后的子材料 — 真实不可制作材料行样式，左侧（名称端）可见，缩小表达从属层级 -->
                <div class="space-y-1 mb-4 ml-3">
                  <div class="relative -mr-5">
                    <div class="rounded-l-2xl border border-[#5C5470] border-r-0 p-2 pr-5 bg-[#4A4858]">
                      <div class="flex items-center gap-2">
                        <button class="shrink-0 h-4 w-4 rounded-full border border-[#7A7589] bg-transparent" tabindex="-1" />
                        <div class="flex-1 min-w-0">
                          <div class="text-xs font-medium text-[#EDE9F7] truncate">{{ t('onboarding.exampleSub1') }}</div>
                          <div class="text-[10px] text-[#9B96AD] mt-0.5">{{ t('obtainMethods.GATHER_MINER') }}</div>
                        </div>
                        <div class="text-xs font-semibold text-[#EDE9F7] shrink-0 tabular-nums">24</div>
                      </div>
                    </div>
                    <!-- 右侧虚焦遮罩 -->
                    <div class="absolute inset-y-0 right-0 w-20 backdrop-blur-sm bg-gradient-to-l from-[#4A4858] via-[#4A4858]/80 to-transparent pointer-events-none" />
                  </div>

                  <div class="relative -mr-5">
                    <div class="rounded-l-2xl border border-[#5C5470] border-r-0 p-2 pr-5 bg-[#4A4858]">
                      <div class="flex items-center gap-2">
                        <button class="shrink-0 h-4 w-4 rounded-full border border-[#7A7589] bg-transparent" tabindex="-1" />
                        <div class="flex-1 min-w-0">
                          <div class="text-xs font-medium text-[#EDE9F7] truncate">{{ t('onboarding.exampleSub2') }}</div>
                          <div class="text-[10px] text-[#9B96AD] mt-0.5">{{ t('obtainMethods.GATHER_MINER') }}</div>
                        </div>
                        <div class="text-xs font-semibold text-[#EDE9F7] shrink-0 tabular-nums">8</div>
                      </div>
                    </div>
                    <!-- 右侧虚焦遮罩 -->
                    <div class="absolute inset-y-0 right-0 w-20 backdrop-blur-sm bg-gradient-to-l from-[#4A4858] via-[#4A4858]/80 to-transparent pointer-events-none" />
                  </div>
                </div>

                <!-- 说明文字 -->
                <p class="text-xs text-[#9B96AD] leading-relaxed">
                  {{ t('onboarding.page1Desc') }}
                </p>

              </template>

              <!-- ── Page 1：快捷键说明 ── -->
              <template v-else>

                <!-- Ctrl 多选 -->
                <div class="rounded-xl bg-[#3B3A47] border border-[#4A4858] px-4 py-3 mb-3">
                  <div class="flex items-start gap-3">
                    <div class="shrink-0 flex flex-col gap-1 pt-0.5">
                      <div class="flex items-center gap-1">
                        <kbd class="px-1.5 py-0.5 rounded bg-[#252430] border border-[#4A4858] text-[10px] text-[#B4A5C8] font-mono leading-none">Ctrl</kbd>
                        <span class="text-[10px] text-[#6B677A]">+</span>
                        <kbd class="px-1.5 py-0.5 rounded bg-[#252430] border border-[#4A4858] text-[10px] text-[#B4A5C8] font-mono leading-none">Click</kbd>
                      </div>
                      <div class="mt-1 space-y-1">
                        <div class="rounded-lg bg-[#252430] border border-[#4A4858] px-2 py-1 flex items-center gap-1.5 w-28">
                          <span class="w-1.5 h-1.5 rounded-full bg-[#B4A5C8] shrink-0" />
                          <span class="text-[10px] text-[#EDE9F7] truncate">{{ t('onboarding.exampleItem') }}</span>
                        </div>
                        <div class="rounded-lg bg-[#2D2C34] border border-[#38364A] px-2 py-1 flex items-center gap-1.5 w-28">
                          <span class="w-1.5 h-1.5 rounded-full bg-[#4A4858] shrink-0" />
                          <span class="text-[10px] text-[#9B96AD] truncate">{{ t('onboarding.exampleSub1') }}</span>
                        </div>
                      </div>
                    </div>
                    <div>
                      <div class="text-xs font-medium text-[#EDE9F7] mb-1">{{ t('onboarding.shortcutCtrlTitle') }}</div>
                      <p class="text-[11px] text-[#9B96AD] leading-relaxed">{{ t('onboarding.shortcutCtrlDesc') }}</p>
                    </div>
                  </div>
                </div>

                <!-- 复制按钮 -->
                <div class="rounded-xl bg-[#3B3A47] border border-[#4A4858] px-4 py-3">
                  <div class="flex items-start gap-3">
                    <div class="shrink-0 pt-0.5">
                      <div class="h-8 w-8 rounded-xl bg-[#252430] border border-[#4A4858] flex items-center justify-center">
                        <Copy :size="15" color="#9B96AD" />
                      </div>
                    </div>
                    <div>
                      <div class="text-xs font-medium text-[#EDE9F7] mb-1">{{ t('onboarding.copyTitle') }}</div>
                      <p class="text-[11px] text-[#9B96AD] leading-relaxed">{{ t('onboarding.copyDesc') }}</p>
                    </div>
                  </div>
                </div>

              </template>
            </div>
          </div>

          <!-- 右箭头 -->
          <button
            v-if="page < 1"
            type="button"
            class="shrink-0 h-10 w-10 rounded-full flex items-center justify-center text-[#9B96AD] hover:text-[#EDE9F7] hover:bg-[#38364A] transition-colors"
            @click="page++"
          >
            <ChevronRight :size="20" />
          </button>
          <span v-else class="shrink-0 w-10" />

        </div>

        <!-- X 关闭按钮 -->
        <button
          type="button"
          class="mt-5 h-9 w-9 rounded-full border border-[#4A4858] flex items-center justify-center text-[#9B96AD] hover:text-[#EDE9F7] hover:border-[#9B96AD] transition-colors"
          @click="close()"
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
import { useOnboarding } from "../composables/useOnboarding.js";

const { t } = useI18n();
const { isOpen, close } = useOnboarding();

const page = ref(0);

watch(isOpen, (val) => {
  if (val) page.value = 0;
});
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
