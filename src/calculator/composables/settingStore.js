// 存储状态（单向数据流根文件）
import { reactive, readonly } from "vue";

// 模块级单例：全 app 共用一份
const state = reactive({
  settings: {
    searchQuery: "",
  },
  // targets: Array<{ id: number; amount: number }>
  targets: [], // [{ id, amount }]
});


function setSearchQuery(next) {
  // 先不做清洗优化，你要先跑起来：保证是字符串就行
  state.settings.searchQuery = String(next ?? "");
}

function clampAmount(n) {
  const x = Number(n);
  if (!Number.isFinite(x)) return 1;
  return Math.max(1, Math.floor(x));
}

function addTarget(itemId, amount = 1) {
  const id = Number(itemId);
  if (!Number.isFinite(id)) return;

  const amt = clampAmount(amount);

  const hit = state.targets.find((t) => t.id === id);
  if (hit) {
    // 已存在：默认策略 = 数量累加
    hit.amount += amt;
    return;
  }

  // 新增：默认数量 1
  state.targets.push({ id, amount: amt });
}

function removeTarget(itemId) {
  const id = Number(itemId);
  if (!Number.isFinite(id)) return;

  const idx = state.targets.findIndex((t) => t.id === id);
  if (idx !== -1) state.targets.splice(idx, 1);
}

// 给 TargetPanel 用的更新数量接口
function updateTargetAmount({ id, amount }) {
  const n = Number(id);
  if (!Number.isFinite(n)) return;

  const t = state.targets.find(x => x.id === n);
  if (!t) return;

  t.amount = clampAmount(amount);
}



export function useSettingStore() {
  return {
    settings: readonly(state.settings),
    targets: readonly(state.targets),

    setSearchQuery,
    addTarget,
    removeTarget,
    updateTargetAmount
  };
}

