# Module Contracts (v1.0)
This document records the interfaces and field contracts between modules in data-flow order.

> Scope: only covers contracts between pages, components, composables, and core under calculator/.
> Architecture overview: [`01-architecture-dataflow.en.md`](01-architecture-dataflow.en.md).
> Static data structures: [`03-deployment-data.en.md`](03-deployment-data.en.md).

## 1. Page ↔ UI Components

### 1.1 ItemSearchBar
**Purpose**: Search input only; emits input events.

**Props**
- `query: string` - Current search keyword.

**Emits**
- `update:query(value: string)` - Emits the latest keyword on input.

**Source**
- Page passes in `settings.searchQuery`.
- Page receives `update:query` and calls `setSearchQuery`.

---

### 1.2 ItemSearchResults
**Purpose**: Shows the search results list.

**Props**
- `results: Array<{ id: number, name: string, ... }>` - Results from `useItemSearch`.

**Emits**
- `select(id: number)` - Emits the selected item id on click.

**Source**
- Page reads `results` from `useItemSearch`.
- Page receives `select`, calls `targetsCtrl.add`, and clears the search query.

---

### 1.3 TargetItemPanel
**Purpose**: Shows target items, edits amount, and clears all.

**Props**
- `targets: Array<{ id: number, name: string, amount: number }>` - Page maps store targets for display.

**Emits**
- `remove(id: number)` - Removes a target.
- `update-amount(payload: { id: number, amount: number })` - Updates amount (input + blur).
- `clear()` - Clears all targets.

**Source**
- Page receives events and calls `targetsCtrl.remove / updateAmount / clear`.

---

### 1.4 MaterialsList
**Purpose**: Materials list container, including craftable/non-craftable sections and actions.

**Props**
- `ui: { craftable: Entry[], nonCraftable: Entry[] }`
- `checkedIds: Set<number>` - Checked items.
- `expandOrder: Map<number, number>` - Expansion order (earlier expanded comes first).

**Emits**
- `toggle-expand(id: number)` - Expand/collapse a craftable item.
- `collapse-all()` - Collapse to top level (lock all).
- `expand-all()` - Expand all (controlled by Page).
- `toggle-check(id: number)` - Check/uncheck a material.
- `clear-checked()` - Clear checked state.
- `reset-materials()` - Reset materials progress (expand + checked).
- `copy-materials()` - Copy the materials list text.

**Source**
- Page passes in `ui` from `useMaterialsList` and `checkedIds/expandOrder` from `materialsCtrl`.
- Page receives events and calls the matching `materialsCtrl` methods.

---

### 1.5 CanCraftSection
**Purpose**: Renders the craftable materials section.

**Props**
- `craftable: Entry[]`
- `checkedIds: Set<number>`
- `expandOrder: Map<number, number>`

**Emits**
- `toggle-check(id: number)` - Check a material.
- `toggle-expand(id: number)` - Expand/collapse a material.

**Entry shape (from useMaterialsList)**
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
  job: string | null // From the recipe (may map to job icons later)
  source: string | null // Derived from obtainMethods (localized later)
  displayAmount: number // Displayed amount (craft times when expanded)
  displaySuffix: string // "times" when expanded, otherwise empty
}
```

---

### 1.6 NotCraftSection
**Purpose**: Renders the non-craftable materials section.

**Props**
- `nonCraftable: Entry[]`
- `checkedIds: Set<number>`

**Emits**
- `toggle-check(id: number)` - Check a material.

---

## 2. Page ↔ composables

### 2.1 useSettingStore
**Purpose**: Singleton store (targets / expanded state / checked state / input).

**Return**
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

**Notes (reserved but not exposed)**
- `keybinds`: Reserved for future shortcut settings (not used yet).

---

### 2.2 useItemSearch
**Purpose**: Search results (input cleanup + substring match).

**Signature**
```ts
useItemSearch(itemsRef, queryRef, limit = 20)
```
- `itemsRef`: Array<Item>
- `queryRef`: string
- `limit`: number

**Output**
- `results: ComputedRef<Array<Item>>` (empty input returns an empty list)

---

### 2.3 useMaterialsList
**Purpose**: Materials list derivation (core calculation + UI shaping).

**Input**
```ts
useMaterialsList({
  targets: Array<{ id: number, amount: number }>,
  items: Array<Item>,
  recipes: Array<Recipe>,
  expandedIds: Set<number>,
  overrides?: Map<number, number>,
})
```

**Output**
- `itemById: ComputedRef<Map<number, Item>>`
- `ui: ComputedRef<{ craftable: Entry[], nonCraftable: Entry[] }>`
- `reachableCraftableIds: ComputedRef<Set<number>>` (reachable craftable ids for "expand all")
- `exportText: ComputedRef<string>` (materials export text)

**Notes**
- `overrides` is reserved for selecting a recipe; currently not passed from Page.

---

## 3. composables ↔ core

### 3.1 calcMaterials
**Purpose**: Core material calculation.

**Input**
```ts
calcMaterials({
  targets: Array<{ id: number, amount: number }>,
  recipes: Array<Recipe>,
  overrides?: Map<number, number>,
  expandedIds?: Set<number>,
})
```

**Output**
```ts
{
  materials: Map<itemId, amount> // Boundary materials (non-craftable + craftable that stay unexpanded)
  crafts: Map<resultItemId, { recipeId: number, times: number }>
  needs: Map<itemId, amount>     // Total needs (targets + intermediate needs)
  rootNeeds: Map<itemId, amount> // Needs coming from targets only
  picks: Map<resultItemId, recipeId>
  warnings: Array<
    | { kind: 'cycle', path: number[] }
    | { kind: 'invalid-yield', recipeId: number, resultItemId: number, resultAmount: number }
    | { kind: 'override-miss', resultItemId: number, recipeId: number }
  >
}
```

**Key contracts**
- `expandedIds` decides whether a craftable item is expanded further; if not expanded, it is treated as a boundary material.
- Top-level targets are force-expanded one level by default.

---

### 3.2 recipeUtils
**buildRecipesByResultId(recipes)**
- Input `recipes` array, output `Map<resultItemId, Recipe[]>`.

**pickRecipe(resultItemId, candidates, overrides?, warnings?)**
- If `overrides` specifies a recipeId and it exists, use it.
- Otherwise choose `candidates[0]`.
- If override misses, optionally push a warning.

---

## 4. Page mappings (for UI display)

### 4.1 Target entries
Page maps store `targets` to display objects:
```ts
{ id: number, amount: number, name: string }
```
`name` is resolved from `items.json`; falls back to `"Unknown"` if missing.

### 4.2 Materials UI entries
`useMaterialsList` converts results to `Entry`, then the UI shows:
- `displayAmount`: if `isCraftable && isExpanded`, show `craftTimes`, otherwise `needAmount`.
- `displaySuffix`: shows `"times"` when expanded, otherwise empty.
- `job`: from `recipe.job` (UI may replace with icons).
- `source`: mapped from `items.obtainMethods` into readable text (localized later).
- `exportText`: output format:
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
