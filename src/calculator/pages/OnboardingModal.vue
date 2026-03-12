<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
      >
        <!-- 卡片 -->
        <div class="relative w-full max-w-sm rounded-2xl bg-[#2D2C34] border border-[#4A4858] shadow-[0_8px_40px_rgba(0,0,0,0.7)] flex flex-col overflow-hidden">

          <!-- 标题栏 -->
          <div class="px-5 pt-5 pb-3 border-b border-[#38364A]">
            <div class="text-sm font-semibold text-[#EDE9F7]">
              {{ page === 0 ? t('onboarding.page1Title') : t('onboarding.page2Title') }}
            </div>
            <!-- 页码点 -->
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
          <div class="px-5 py-4 flex-1 overflow-y-auto">

            <!-- ── Page 0：拆开说明 ── -->
            <template v-if="page === 0">
              <p class="text-xs text-[#9B96AD] leading-relaxed mb-4">
                {{ t('onboarding.page1Desc') }}
              </p>

              <!-- 两种状态对比 -->
              <div class="space-y-3">

                <!-- 状态一：未拆 -->
                <div>
                  <div class="text-[10px] text-[#6B677A] uppercase tracking-wide mb-1.5">
                    {{ t('onboarding.stateBefore') }}
                  </div>
                  <div class="rounded-xl bg-[#3B3A47] border border-[#4A4858] px-3 py-2.5">
                    <div class="flex items-center gap-2">
                      <!-- 职业徽章 -->
                      <span class="shrink-0 text-[10px] text-[#9B96AD] bg-[#2D2C34] rounded-md px-1.5 py-0.5">BSM</span>
                      <!-- 名称 -->
                      <span class="flex-1 text-sm text-[#EDE9F7] truncate">{{ t('onboarding.exampleItem') }}</span>
                      <!-- 数量 -->
                      <span class="text-xs text-[#9B96AD]">×12</span>
                      <!-- 链条按钮（未拆状态） -->
                      <button
                        type="button"
                        class="shrink-0 h-9 w-9 flex items-center justify-center rounded-xl opacity-60"
                        tabindex="-1"
                      >
                        <Link2 :size="20" color="#B4A5C8" />
                      </button>
                    </div>
                  </div>
                </div>

                <!-- 箭头 + 提示 -->
                <div class="flex items-center gap-2 pl-1">
                  <ChevronDown :size="14" color="#6B677A" />
                  <span class="text-[11px] text-[#6B677A]">{{ t('onboarding.clickHint') }}</span>
                </div>

                <!-- 状态二：已拆 -->
                <div>
                  <div class="text-[10px] text-[#6B677A] uppercase tracking-wide mb-1.5">
                    {{ t('onboarding.stateAfter') }}
                  </div>
                  <div class="rounded-xl bg-[#3B3A47] border border-[#4A4858] px-3 py-2.5 space-y-2.5">
                    <!-- 主条目 -->
                    <div class="flex items-center gap-2">
                      <span class="shrink-0 text-[10px] text-[#9B96AD] bg-[#2D2C34] rounded-md px-1.5 py-0.5">BSM</span>
                      <span class="flex-1 text-sm text-[#EDE9F7] truncate">{{ t('onboarding.exampleItem') }}</span>
                      <span class="text-xs text-[#9B96AD]">×12</span>
                      <!-- 链条按钮（已拆状态） -->
                      <button
                        type="button"
                        class="shrink-0 h-9 w-9 flex items-center justify-center rounded-xl opacity-60"
                        tabindex="-1"
                      >
                        <Link2Off :size="20" color="#E8D07A" />
                      </button>
                    </div>

                    <!-- 分割线 -->
                    <div class="border-t border-[#4A4858]" />

                    <!-- 子材料 -->
                    <div class="space-y-1.5 pl-2">
                      <div class="flex items-center gap-2">
                        <span class="w-1 h-1 rounded-full bg-[#6B677A] shrink-0" />
                        <span class="flex-1 text-xs text-[#B4A5C8]">{{ t('onboarding.exampleSub1') }}</span>
                        <span class="text-xs text-[#9B96AD]">×24</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="w-1 h-1 rounded-full bg-[#6B677A] shrink-0" />
                        <span class="flex-1 text-xs text-[#B4A5C8]">{{ t('onboarding.exampleSub2') }}</span>
                        <span class="text-xs text-[#9B96AD]">×8</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <!-- ── Page 1：快捷键说明 ── -->
            <template v-else>

              <!-- Ctrl 多选 -->
              <div class="rounded-xl bg-[#3B3A47] border border-[#4A4858] px-4 py-3 mb-3">
                <div class="flex items-start gap-3">
                  <!-- 仿真搜索条目 + Ctrl badge -->
                  <div class="shrink-0 flex flex-col gap-1 pt-0.5">
                    <div class="flex items-center gap-1">
                      <kbd class="px-1.5 py-0.5 rounded bg-[#252430] border border-[#4A4858] text-[10px] text-[#B4A5C8] font-mono leading-none">Ctrl</kbd>
                      <span class="text-[10px] text-[#6B677A]">+</span>
                      <kbd class="px-1.5 py-0.5 rounded bg-[#252430] border border-[#4A4858] text-[10px] text-[#B4A5C8] font-mono leading-none">Click</kbd>
                    </div>
                    <!-- 仿真搜索结果小条 -->
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
                  <!-- 说明文字 -->
                  <div>
                    <div class="text-xs font-medium text-[#EDE9F7] mb-1">{{ t('onboarding.shortcutCtrlTitle') }}</div>
                    <p class="text-[11px] text-[#9B96AD] leading-relaxed">{{ t('onboarding.shortcutCtrlDesc') }}</p>
                  </div>
                </div>
              </div>

              <!-- 复制按钮 -->
              <div class="rounded-xl bg-[#3B3A47] border border-[#4A4858] px-4 py-3">
                <div class="flex items-start gap-3">
                  <!-- 仿真按钮 -->
                  <div class="shrink-0 pt-0.5">
                    <div class="h-8 w-8 rounded-xl bg-[#252430] border border-[#4A4858] flex items-center justify-center">
                      <Copy :size="15" color="#9B96AD" />
                    </div>
                  </div>
                  <!-- 说明文字 -->
                  <div>
                    <div class="text-xs font-medium text-[#EDE9F7] mb-1">{{ t('onboarding.copyTitle') }}</div>
                    <p class="text-[11px] text-[#9B96AD] leading-relaxed">{{ t('onboarding.copyDesc') }}</p>
                  </div>
                </div>
              </div>

            </template>
          </div>

          <!-- 底部导航 -->
          <div class="px-5 py-4 border-t border-[#38364A] flex items-center justify-between">

            <!-- 左箭头 -->
            <button
              v-if="page > 0"
              type="button"
              class="h-8 w-8 rounded-full flex items-center justify-center text-[#9B96AD] hover:text-[#EDE9F7] hover:bg-[#38364A] transition-colors"
              @click="page--"
            >
              <ChevronLeft :size="16" />
            </button>
            <span v-else class="h-8 w-8" />

            <!-- 关闭按钮（圆形 X） -->
            <button
              type="button"
              class="h-9 w-9 rounded-full border border-[#4A4858] flex items-center justify-center text-[#9B96AD] hover:text-[#EDE9F7] hover:border-[#9B96AD] transition-colors"
              :title="t('onboarding.reopen')"
              @click="close()"
            >
              <X :size="16" />
            </button>

            <!-- 右箭头 -->
            <button
              v-if="page < 1"
              type="button"
              class="h-8 w-8 rounded-full flex items-center justify-center text-[#9B96AD] hover:text-[#EDE9F7] hover:bg-[#38364A] transition-colors"
              @click="page++"
            >
              <ChevronRight :size="16" />
            </button>
            <span v-else class="h-8 w-8" />
          </div>

        </div>
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

// 每次打开时重置到第一页
watch(isOpen, (val) => {
  if (val) page.value = 0;
});
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active .relative,
.modal-leave-active .relative {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .relative {
  transform: scale(0.95);
  opacity: 0;
}
.modal-leave-to .relative {
  transform: scale(0.95);
  opacity: 0;
}
</style>
