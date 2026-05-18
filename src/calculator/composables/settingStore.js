// settingStore.js 存储动态数据（单向数据流根文件）
import { reactive, readonly } from "vue";
import { clampPositiveInteger } from "../utils/amountUtils";

// ---- persistence (localStorage) ----
// 只存"用户交互产生的状态"：targets / 展开锁链 / 勾选 / 输入框内容等
const STORAGE_KEY = "msjcalc.settingStore.v1";

function safeParse(raw) {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function toFiniteNumber(n) {
  const x = Number(n);
  return Number.isFinite(x) ? x : null;
}

function loadFromStorage(state) {
  if (typeof window === "undefined") return;
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return;

  const data = safeParse(raw);
  if (!data || typeof data !== "object") return;

  // settings
  if (data.settings && typeof data.settings === "object") {
    if (typeof data.settings.searchQuery === "string") {
      state.settings.searchQuery = data.settings.searchQuery;
    }
  }

  // targets
  state.targets.splice(0, state.targets.length);
  for (const t of data.targets || []) {
    const id = toFiniteNumber(t?.id);
    const amount = toFiniteNumber(t?.amount);
    if (id == null || amount == null) continue;
    state.targets.push({ id, amount: Math.max(1, Math.floor(amount)) });
  }

  // outfit bundle targets
  state.outfitTargets.splice(0, state.outfitTargets.length);
  for (const b of data.outfitTargets || []) {
    if (!b?.setKey || !b?.jobKey) continue;
    const uid = toFiniteNumber(b.uid) ?? 0;
    const itemIds = (b.itemIds || []).map(Number).filter(Number.isFinite);
    const weaponIds = (b.weaponIds || []).map(Number).filter(Number.isFinite);
    state.outfitTargets.push({
      uid,
      setKey: String(b.setKey),
      tierLevel: toFiniteNumber(b.tierLevel) ?? 0,
      roleKey: b.roleKey ? String(b.roleKey) : null,
      jobKey: String(b.jobKey),
      amount: Math.max(1, Math.floor(toFiniteNumber(b.amount) ?? 1)),
      itemIds,
      weaponIds,
      includeWeapon: Boolean(b.includeWeapon),
      expanded: Boolean(b.expanded),
    });
  }
  const seq = toFiniteNumber(data.outfitTargetSeq);
  state.outfitTargetSeq =
    seq != null
      ? seq
      : state.outfitTargets.reduce((max, t) => Math.max(max, t.uid), 0) + 1;

  // expanded ids
  state.expandedResultItemIds.clear();
  for (const rawId of data.expandedIds || []) {
    const id = toFiniteNumber(rawId);
    if (id == null) continue;
    state.expandedResultItemIds.add(id);
  }

  // expand order
  state.expandedOrderById.clear();
  for (const pair of data.expandOrder || []) {
    const id = toFiniteNumber(pair?.[0]);
    const order = toFiniteNumber(pair?.[1]);
    if (id == null || order == null) continue;
    state.expandedOrderById.set(id, order);
  }
  const seq2 = toFiniteNumber(data.expandSeq);
  state.expandSeq = seq2 != null ? seq2 : state.expandedOrderById.size;

  // checked ids
  state.checkedItemIds.clear();
  for (const rawId of data.checkedIds || []) {
    const id = toFiniteNumber(rawId);
    if (id == null) continue;
    state.checkedItemIds.add(id);
  }

  // keybinds（预留：未来做快捷键设置时直接复用；现在不影响功能）
  if (data.keybinds && typeof data.keybinds === "object") {
    state.keybinds = {
      ...state.keybinds,
      ...data.keybinds,
    };
  }
}

function saveToStorage(state) {
  if (typeof window === "undefined") return;
  try {
    const payload = {
      settings: {
        searchQuery: state.settings.searchQuery,
      },
      targets: state.targets.map((t) => ({ id: t.id, amount: t.amount })),
      outfitTargets: state.outfitTargets.map((b) => ({
        uid: b.uid,
        setKey: b.setKey,
        tierLevel: b.tierLevel,
        roleKey: b.roleKey,
        jobKey: b.jobKey,
        amount: b.amount,
        itemIds: b.itemIds,
        weaponIds: b.weaponIds,
        includeWeapon: b.includeWeapon,
        expanded: b.expanded,
      })),
      outfitTargetSeq: state.outfitTargetSeq,
      expandedIds: [...state.expandedResultItemIds],
      expandOrder: [...state.expandedOrderById.entries()],
      expandSeq: state.expandSeq,
      checkedIds: [...state.checkedItemIds],
      keybinds: state.keybinds,
    };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  } catch {
    // localStorage 可能满/被禁用：忽略即可
  }
}

// 模块级单例：全 app 共用一份
const state = reactive({
  settings: {
    searchQuery: "",
  },
  // targets: Array<{ id: number; amount: number }>
  targets: [],
  // outfitTargets: Array<{ uid, setKey, tierLevel, roleKey, jobKey, itemIds, weaponIds, includeWeapon, expanded }>
  outfitTargets: [],
  outfitTargetSeq: 0,
  // 用 Set：只记录"已拆开"的 resultItemId
  expandedResultItemIds: new Set(),

  // ✅ 新增：展开顺序（先拆的序号更小）
  expandedOrderById: new Map(),
  expandSeq: 0,

  // ✅ 新增：材料勾选（可制作/不可制作共用）
  checkedItemIds: new Set(),

  // ✅ 预留：快捷键配置（未来做 UI 时会用到）
  keybinds: {
    // e.g. collapseAll: "Escape", expandAll: "Shift+E"
  },
});

// 初始化：从 localStorage 恢复
loadFromStorage(state);

// -------- 锁链状态：读写接口（都写到 state 上） --------
function toId(n) {
  const x = Number(n);
  return Number.isFinite(x) ? x : null;
}

// 查询：某个物品是否处于"已拆开"
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

  if (!state.expandedOrderById.has(id)) {
    state.expandedOrderById.set(id, state.expandSeq++);
  }

  saveToStorage(state);
}

// 操作：收起（锁回去）
function collapse(resultItemId) {
  const id = toId(resultItemId);
  if (id == null) return;
  state.expandedResultItemIds.delete(id);
  saveToStorage(state);
}

// 操作：切换锁链
function toggleExpand(resultItemId) {
  const id = toId(resultItemId);
  if (id == null) return;

  if (state.expandedResultItemIds.has(id)) {
    state.expandedResultItemIds.delete(id);
  } else {
    state.expandedResultItemIds.add(id);
    if (!state.expandedOrderById.has(id)) {
      state.expandedOrderById.set(id, state.expandSeq++);
    }
  }

  saveToStorage(state);
}

// 快捷键：全部锁回去（折叠到"全不拆"）
function collapseAll() {
  state.expandedResultItemIds.clear();
  saveToStorage(state);
}

// 快捷键：批量拆开（以后"拆到底"会用到）
function expandMany(ids) {
  for (const raw of ids || []) {
    const id = toId(raw);
    if (id == null) continue;
    state.expandedResultItemIds.add(id);
    if (!state.expandedOrderById.has(id)) {
      state.expandedOrderById.set(id, state.expandSeq++);
    }
  }
  saveToStorage(state);
}

// -------- 你已有的 targets / search 逻辑（原样保留） --------
function setSearchQuery(next) {
  state.settings.searchQuery = String(next ?? "");
  saveToStorage(state);
}

function addTarget(itemId, amount = 1) {
  const id = Number(itemId);
  if (!Number.isFinite(id)) return;

  const amt = clampPositiveInteger(amount);

  const hit = state.targets.find((t) => t.id === id);
  if (hit) {
    hit.amount += amt;
    saveToStorage(state);
    return;
  }

  state.targets.push({ id, amount: amt });
  saveToStorage(state);
}

function removeTarget(itemId) {
  const id = Number(itemId);
  if (!Number.isFinite(id)) return;

  const idx = state.targets.findIndex((t) => t.id === id);
  if (idx !== -1) state.targets.splice(idx, 1);
  saveToStorage(state);
}

function updateTargetAmount({ id, amount }) {
  const n = Number(id);
  if (!Number.isFinite(n)) return;

  const t = state.targets.find((x) => x.id === n);
  if (!t) return;

  t.amount = clampPositiveInteger(amount);
  saveToStorage(state);
}

function clearTargets() {
  state.targets.splice(0, state.targets.length);
  saveToStorage(state);
}

// -------- outfit bundle targets --------
function sameNumberList(a, b) {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i += 1) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}

function addOutfitTarget({ setKey, tierLevel, roleKey, jobKey, itemIds, weaponIds }) {
  const nextItemIds = [...itemIds];
  const nextWeaponIds = [...weaponIds];
  const includeWeapon = nextWeaponIds.length > 0;
  const hit = state.outfitTargets.find((t) =>
    t.setKey === setKey
    && t.tierLevel === tierLevel
    && (!t.roleKey || !roleKey || t.roleKey === roleKey)
    && t.jobKey === jobKey
    && t.includeWeapon === includeWeapon
    && sameNumberList(t.itemIds, nextItemIds)
    && sameNumberList(t.weaponIds, nextWeaponIds)
  );

  if (hit) {
    hit.amount += 1;
    saveToStorage(state);
    return;
  }

  const uid = ++state.outfitTargetSeq;
  state.outfitTargets.push({
    uid,
    setKey,
    tierLevel,
    roleKey: roleKey ?? null,
    jobKey,
    amount: 1,
    itemIds: nextItemIds,
    weaponIds: nextWeaponIds,
    includeWeapon,
    expanded: false,
  });
  saveToStorage(state);
}

function removeOutfitTarget(uid) {
  const idx = state.outfitTargets.findIndex((t) => t.uid === uid);
  if (idx !== -1) state.outfitTargets.splice(idx, 1);
  saveToStorage(state);
}

function updateOutfitTargetAmount({ uid, amount }) {
  const t = state.outfitTargets.find((t) => t.uid === uid);
  const next = Math.max(1, Math.floor(Number(amount) || 1));
  if (!t) return;
  t.amount = next;
  saveToStorage(state);
}

function toggleOutfitWeapon(uid) {
  const t = state.outfitTargets.find((t) => t.uid === uid);
  if (!t) return;
  t.includeWeapon = !t.includeWeapon;
  saveToStorage(state);
}

function toggleOutfitExpanded(uid) {
  const t = state.outfitTargets.find((t) => t.uid === uid);
  if (!t) return;
  t.expanded = !t.expanded;
  saveToStorage(state);
}

function clearOutfitTargets() {
  state.outfitTargets.splice(0, state.outfitTargets.length);
  saveToStorage(state);
}

// -------- 勾选：读写接口（用于 MaterialsList） --------
function isChecked(itemId) {
  const id = toId(itemId);
  if (id == null) return false;
  return state.checkedItemIds.has(id);
}

function toggleChecked(itemId) {
  const id = toId(itemId);
  if (id == null) return;
  if (state.checkedItemIds.has(id)) state.checkedItemIds.delete(id);
  else state.checkedItemIds.add(id);
  saveToStorage(state);
}

function clearChecked() {
  state.checkedItemIds.clear();
  saveToStorage(state);
}

// -------- 材料列表：一键重置（只清材料相关，不影响 targets / search） --------
function resetMaterials() {
  // 展开状态 + 展开顺序
  state.expandedResultItemIds.clear();
  state.expandedOrderById.clear();
  state.expandSeq = 0;

  // 勾选
  state.checkedItemIds.clear();

  saveToStorage(state);
}

export function useSettingStore() {
  const targetsCtrl = {
    targets: readonly(state.targets),

    add: addTarget,
    remove: removeTarget,
    updateAmount: updateTargetAmount,
    clear: clearTargets,
  };

  const outfitTargetsCtrl = {
    outfitTargets: readonly(state.outfitTargets),

    add: addOutfitTarget,
    remove: removeOutfitTarget,
    updateAmount: updateOutfitTargetAmount,
    toggleWeapon: toggleOutfitWeapon,
    toggleExpanded: toggleOutfitExpanded,
    clear: clearOutfitTargets,
  };

  const materialsCtrl = {
    // （可选）给 composable 用
    expandedIds: readonly(state.expandedResultItemIds),

    // ✅ 给 UI 排序用（已拆按先后）
    expandOrder: readonly(state.expandedOrderById),

    isExpanded,
    expand,
    collapse,
    toggle: toggleExpand,
    collapseAll,
    expandMany,

    // ✅ 勾选（持久化）
    checkedIds: readonly(state.checkedItemIds),
    isChecked,
    toggleCheck: toggleChecked,
    clearChecked,

    // ✅ 重置材料列表状态（不影响 targets/search）
    resetMaterials,
  };

  return {
    settings: readonly(state.settings),
    setSearchQuery,

    targetsCtrl,
    outfitTargetsCtrl,
    materialsCtrl,
  };
}
