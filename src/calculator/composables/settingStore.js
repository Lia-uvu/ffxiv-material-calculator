// 存储状态（单向数据流根文件）
import { reactive, readonly } from "vue";

// 模块级单例：全 app 共用一份
const state = reactive({
  settings: {
    searchQuery: "",
  },
  targets: [], // number[]
});

function setSearchQuery(next) {
  // 先不做清洗优化，你要先跑起来：保证是字符串就行
  state.settings.searchQuery = String(next ?? "");
}

function addTarget(itemId) {
  const id = Number(itemId);
  if (!Number.isFinite(id)) return;

  // 防重复
  if (!state.targets.includes(id)) state.targets.push(id);
}

function removeTarget(itemId) {
  const id = Number(itemId);
  const idx = state.targets.indexOf(id);
  if (idx !== -1) state.targets.splice(idx, 1);
}

export function useCalculatorSettings() {
  return {
    settings: readonly(state.settings),
    targets: readonly(state.targets),

    setSearchQuery,
    addTarget,
    removeTarget,
  };
}

