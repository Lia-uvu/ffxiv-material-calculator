# 模块通信（v1.0）

本文档按数据流向顺序记录模块之间的通信接口与字段。覆盖 calculator/ 下页面、组件、composables、core 之间的接口约定。

> 架构概览见：[`01-architecture-dataflow.md`](01-architecture-dataflow.md)。
> 静态数据结构见：[`03-deployment-data.md`](03-deployment-data.md)。

## 1. 页面（Page）与 UI 组件通信

### 1.1 SearchPanel
**用途**：搜索区块入口组件，组合 `ItemSearchBar` / `ItemSearchResults`，并内聚点击外部关闭与 Ctrl 多选提示。

**Props**
- `query: string` - 当前搜索关键词。
- `results: Array<{ id: number, name: string, ... }>` - 搜索结果数组（来自 `useItemSearch`）。
- `targetAmounts: Map<number, number>` - 已添加目标的数量角标。

**Emits**
- `update:query(value: string)` - 输入变化或点击外部清空时回传最新关键词。
- `select(payload: { id: number, ctrlKey: boolean })` - 点击条目时上报选中的 item id 与 Ctrl 状态。

**来源**
- Page 传入 `settings.searchQuery`、`results`、`targetAmountsMap`。
- Page 收到 `update:query` 后调用 `setSearchQuery`。
- Page 收到 `select` 后调用 `targetsCtrl.add`，并按 `ctrlKey` 决定是否清空搜索框。

---

### 1.2 TargetItemPanel
**用途**：展示目标成品列表、数量调整、清空。

**Props**
- `targets: Array<{ id: number, name: string, amount: number }>` - Page 将 store 中 targets 映射为可展示结构。

**Emits**
- `remove(id: number)` - 删除单个目标。
- `update-amount(payload: { id: number, amount: number })` - 修改数量（输入/失焦都会触发）。
- `clear()` - 清空所有目标。

**来源**
- Page 接收到事件后分别调用 `targetsCtrl.remove / updateAmount / clear`。

---

### 1.3 MaterialsPanel
**用途**：材料区总容器，组合 `MaterialsToolbar` / `CanCraftSection` / `NotCraftSection` / `CrystalsSection`，并内聚复制与重置确认。

**Props**
- `ui: { craftable: Entry[], nonCraftable: Entry[] }`
- `checkedIds: Set<number>` - 已完成勾选。
- `expandOrder: Map<number, number>` - 展开顺序（先拆的排序更靠前）。
- `exportText: string` - 由 `useMaterialsExport` 生成的材料清单文本。

**Emits**
- `toggle-expand(id: number)` - 展开/收起某个可制作材料。
- `collapse-all()` - 折叠到顶层（全部锁回）。
- `expand-all()` - “拆到底”（实际由 Page 控制可拆集合）。
- `toggle-check(id: number)` - 勾选/取消勾选材料。
- `reset-materials()` - 重置材料进度（展开状态 + 勾选）。

**来源**
- Page 传入 `useMaterialsList` 的 `ui`、`materialsCtrl.checkedIds / expandOrder`，以及 `useMaterialsExport` 的 `exportText`。
- Page 接收到事件后调用 `materialsCtrl` 对应接口；复制与成功反馈由 `MaterialsPanel` 自己处理。

---

### 1.4 TopNav
**用途**：应用壳层顶栏，负责标题、语言切换、打开说明入口。

**Props**
- 无。

**Emits**
- `open-help()` - 打开说明弹层。

**来源**
- `App.vue` 接收到事件后调用 `useOnboarding().open()`。

---

### 1.5 OnboardingModal
**用途**：应用壳层说明弹层。

**Props**
- `isOpen: boolean` - 当前是否显示弹层。

**Emits**
- `close()` - 关闭说明弹层。

**来源**
- `App.vue` 传入 `useOnboarding().isOpen`。
- `App.vue` 接收到 `close` 后调用 `useOnboarding().close()`。

---

### 1.6 CanCraftSection
**用途**：渲染“可制作材料”区块。

**Props**
- `craftable: Entry[]`
- `checkedIds: Set<number>`
- `expandOrder: Map<number, number>`

**Emits**
- `toggle-check(id: number)` - 勾选材料。
- `toggle-expand(id: number)` - 展开/收起材料。

**Entry 结构（由 useMaterialsList 生成）**
```ts
type Entry = {
  id: number
  name: string
  isCrystal: boolean
  isCraftable: boolean
  isExpanded: boolean
  needAmount: number
  craftTimes: number
  recipeId: number | null
  job: string | null
  source: string | null
  displayAmount: number
  displaySuffix: string
}
```

---

### 1.7 NotCraftSection
**用途**：渲染“不可制作材料”区块。

**Props**
- `nonCraftable: Entry[]`
- `checkedIds: Set<number>`

**Emits**
- `toggle-check(id: number)` - 勾选材料。

---

## 2. 页面（Page）与 composables 通信

### 2.1 useSettingStore
**用途**：单例 store（targets / 展开状态 / 勾选状态 / 输入框等）。

**返回值**
```ts
{
  settings: { searchQuery: string }
  setSearchQuery(next: string): void

  targetsCtrl: {
    targets: ReadonlyArray<{ id: number, amount: number }>
    add(id: number, amount?: number): void
    remove(id: number): void
    updateAmount(payload: { id: number, amount: number }): void
    clear(): void
  }

  materialsCtrl: {
    expandedIds: ReadonlySet<number>
    expandOrder: ReadonlyMap<number, number>

    isExpanded(id: number): boolean
    expand(id: number): void
    collapse(id: number): void
    toggle(id: number): void
    collapseAll(): void
    expandMany(ids: number[]): void

    checkedIds: ReadonlySet<number>
    isChecked(id: number): boolean
    toggleCheck(id: number): void
    clearChecked(): void

    resetMaterials(): void
  }
}
```

**额外说明（有但暂未对外暴露的字段）**
- `keybinds`：预留快捷键配置（当前未被任何组件使用）。

---

### 2.2 useItemSearch
**用途**：搜索结果计算（输入清洗 + substring 匹配）。

**入参**
```ts
useItemSearch(itemsRef, queryRef, limit = 20)
```
- `itemsRef`: Array<Item>
- `queryRef`: string
- `limit`: number

**输出**
- `results: ComputedRef<Array<Item>>`（空输入时返回空数组）

---

### 2.3 useMaterialsList
**用途**：材料列表派生（调用 core 计算 + 输出 UI 结构）。

**入参**
```ts
useMaterialsList({
  targets: Array<{ id: number, amount: number }>,
  items: Array<Item>,
  recipes: Array<Recipe>,
  expandedIds: Set<number>,
  overrides?: Map<number, number>,
})
```

**输出**
- `itemById: ComputedRef<Map<number, Item>>`
- `ui: ComputedRef<{ craftable: Entry[], nonCraftable: Entry[] }>`
- `reachableCraftableIds: ComputedRef<Set<number>>`（“拆到底”所需的可达可制作 item id）

**说明**
- `overrides` 预留接口，用于“指定配方”；目前 Page 未传。

---

### 2.4 useMaterialsExport
**用途**：根据 `useMaterialsList` 输出的 `ui` 生成材料清单导出文本。

**入参**
```ts
useMaterialsExport(uiRef)
```

**输出**
- `exportText: ComputedRef<string>`（材料清单导出文本）

---

## 3. composables 与 core 通信

### 3.1 calcMaterials
**用途**：核心材料计算。

**输入**
```ts
calcMaterials({
  targets: Array<{ id: number, amount: number }>,
  recipes: Array<Recipe>,
  overrides?: Map<number, number>,
  expandedIds?: Set<number>,
})
```

**输出**
```ts
{
  materials: Map<itemId, amount> // 边界材料（不可制作 + 仍处于“未展开”的可制作项）
  crafts: Map<resultItemId, { recipeId: number, times: number }>
  needs: Map<itemId, amount>     // 总需求（含 targets + 中间需求）
  rootNeeds: Map<itemId, amount> // 只来自 targets 的需求
  picks: Map<resultItemId, recipeId>
  warnings: Array<
    | { kind: 'cycle', path: number[] }
    | { kind: 'invalid-yield', recipeId: number, resultItemId: number, resultAmount: number }
    | { kind: 'override-miss', resultItemId: number, recipeId: number }
  >
}
```

**关键约定**
- `expandedIds` 决定“可制作材料是否继续展开”。未展开时会作为边界材料返回。
- 顶层 targets 默认“强制展开一层”。

---

### 3.2 recipeUtils
**buildRecipesByResultId(recipes)**
- 输入 `recipes` 数组，输出 `Map<resultItemId, Recipe[]>`。

**pickRecipe(resultItemId, candidates, overrides?, warnings?)**
- 若 `overrides` 有指定 recipeId 且命中，则优先选用。
- 否则默认选择 `candidates[0]`。
- override miss 时可将 warning 推入 `warnings`。

---

## 4. Page 内部映射（供组件展示）

### 4.1 Target entries
Page 将 store 中 `targets` 映射为展示结构：
```ts
{ id: number, amount: number, name: string }
```
`name` 从 `items.json` 的多语言 `name` map 中按当前语言解析，缺失时为 `"Unknown"`。

### 4.2 Materials UI entries
`useMaterialsList` 将计算结果转为 `Entry`，并在 UI 中进一步展示：
- `displayAmount`：若 `isCraftable && isExpanded` 则显示 `craftTimes`，否则显示 `needAmount`。
- `displaySuffix`：展开时显示 `"次"`，否则为空。
- `job`：来自配方 `recipe.job`（展示层可替换为图标）。
- `source`：由 `items.obtainMethods` 映射为可读文本（未来可替换为多语言映射）。
- `useMaterialsExport().exportText`：导出格式如下：
```
目标材料（可制作）
- XXX × 3次 （职业）
- YYY × 5次 （职业）

不可制作材料
- AAA × 12 （获取方式）
- BBB × 4 （获取方式）

水晶
- 风之水晶 × 20
```
