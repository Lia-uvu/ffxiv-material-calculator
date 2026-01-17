# 模块通信（v1.0）
本文档按数据流向顺序记录模块之间的通信接口与字段。覆盖 calculator/ 下页面、组件、composables、core 之间的接口约定。

> 架构概览见：[`01-architecture-dataflow.md`](01-architecture-dataflow.md)。
> 静态数据结构见：[`03-deployment-data.md`](03-deployment-data.md)。

## 1. 页面（Page）与 UI 组件通信

### 1.1 ItemSearchBar
**用途**：搜索输入框，仅做输入/触发事件。

**Props**
- `query: string` - 当前搜索关键词。

**Emits**
- `update:query(value: string)` - 输入变化时回传最新关键词。

**来源**
- Page 传入 `settings.searchQuery`。
- Page 收到 `update:query` 后调用 `setSearchQuery`。

---

### 1.2 ItemSearchResults
**用途**：展示搜索结果列表。

**Props**
- `results: Array<{ id: number, name: string, ... }>` - 搜索结果数组（来自 `useItemSearch`）。

**Emits**
- `select(id: number)` - 点击条目时上报选中的 item id。

**来源**
- Page 从 `useItemSearch` 拿到 `results`。
- Page 收到 `select` 后调用 `targetsCtrl.add`，并清空搜索框。

---

### 1.3 TargetItemPanel
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

### 1.4 MaterialsList
**用途**：材料列表总容器，包含“可制作”和“不可制作”两块与操作按钮。

**Props**
- `ui: { craftable: Entry[], nonCraftable: Entry[] }`
- `checkedIds: Set<number>` - 已完成勾选。
- `expandOrder: Map<number, number>` - 展开顺序（先拆的排序更靠前）。

**Emits**
- `toggle-expand(id: number)` - 展开/收起某个可制作材料。
- `collapse-all()` - 折叠到顶层（全部锁回）。
- `expand-all()` - “拆到底”（实际由 Page 控制可拆集合）。
- `toggle-check(id: number)` - 勾选/取消勾选材料。
- `clear-checked()` - 清空勾选。
- `reset-materials()` - 重置材料进度（展开状态 + 勾选）。

**来源**
- Page 传入 `useMaterialsList` 的 `ui` 和 `materialsCtrl` 的 `checkedIds/expandOrder`。
- Page 接收到事件后调用 `materialsCtrl` 对应接口。

---

### 1.5 CanCraftSection
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
  displayAmount: number // 可展示数量（展开后为制作次数）
  displaySuffix: string // 展开时为 "次"，否则为空
}
```

---

### 1.6 NotCraftSection
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
`name` 从 `items.json` 中查得，缺失时为 `"Unknown"`。

### 4.2 Materials UI entries
`useMaterialsList` 将计算结果转为 `Entry`，并在 UI 中进一步展示：
- `displayAmount`：若 `isCraftable && isExpanded` 则显示 `craftTimes`，否则显示 `needAmount`。
- `displaySuffix`：展开时显示 `"次"`，否则为空。
