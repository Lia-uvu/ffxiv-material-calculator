// settingStore.js 存储动态数据（单向数据流根文件）
import { reactive, readonly } from "vue";

// 模块级单例：全 app 共用一份
const state = reactive({
  settings: {
    searchQuery: "",
  },
  // targets: Array<{ id: number; amount: number }>
  targets: [],
  // 用 Set：只记录“已拆开”的 resultItemId
  expandedResultItemIds: new Set(),
});

// -------- 锁链状态：读写接口（都写到 state 上） --------
function toId(n) {
  const x = Number(n);
  return Number.isFinite(x) ? x : null;
}

// 查询：某个物品是否处于“已拆开”
function isExpanded(resultItemId) {
  const id = toId(resultItemId);
  if (id == null) return false;
  return state.expandedResultItemIds.has(id);
}

// 操作：拆开
function expand(resultItemId) {
  const id = toId(resultItemId);
  if (id == null) return;
  state.expandedResultItemIds.add(id);
}

// 操作：收起（锁回去）
function collapse(resultItemId) {
  const id = toId(resultItemId);
  if (id == null) return;
  state.expandedResultItemIds.delete(id);
}

// 操作：切换锁链
function toggleExpand(resultItemId) {
  const id = toId(resultItemId);
  if (id == null) return;

  if (state.expandedResultItemIds.has(id)) state.expandedResultItemIds.delete(id);
  else state.expandedResultItemIds.add(id);
}

// 快捷键：全部锁回去（折叠到“全不拆”）
function collapseAll() {
  state.expandedResultItemIds.clear();
}

// 快捷键：批量拆开（以后“拆到底”会用到）
function expandMany(ids) {
  for (const raw of ids || []) {
    const id = toId(raw);
    if (id != null) state.expandedResultItemIds.add(id);
  }
}

// -------- 你已有的 targets / search 逻辑（原样保留） --------
function setSearchQuery(next) {
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
    hit.amount += amt;
    return;
  }

  state.targets.push({ id, amount: amt });
}

function removeTarget(itemId) {
  const id = Number(itemId);
  if (!Number.isFinite(id)) return;

  const idx = state.targets.findIndex((t) => t.id === id);
  if (idx !== -1) state.targets.splice(idx, 1);
}

function updateTargetAmount({ id, amount }) {
  const n = Number(id);
  if (!Number.isFinite(n)) return;

  const t = state.targets.find((x) => x.id === n);
  if (!t) return;

  t.amount = clampAmount(amount);
}

function clearTargets() {
  state.targets.splice(0, state.targets.length);
}

export function useSettingStore() {
  const targetsCtrl = {
    targets: readonly(state.targets),

    add: addTarget,
    remove: removeTarget,
    updateAmount: updateTargetAmount,
    clear: clearTargets
  };

  const materialsCtrl = {
    // （可选）给 composable 用
    expandedIds: readonly(state.expandedResultItemIds),

    isExpanded,
    expand,
    collapse,
    toggle: toggleExpand,
    collapseAll,
    expandMany,
  };

  return {
    settings: readonly(state.settings),
    setSearchQuery,

    targetsCtrl,
    materialsCtrl,
  };
}

