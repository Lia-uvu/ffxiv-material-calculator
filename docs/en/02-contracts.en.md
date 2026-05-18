# Module Contracts (v1.0)
This document records the interfaces and field contracts between modules in data-flow order.

> Scope: only covers contracts between pages, components, composables, and core under calculator/.
> Architecture overview: [`01-architecture-dataflow.en.md`](01-architecture-dataflow.en.md).
> Static data structures: [`03-deployment-data.en.md`](03-deployment-data.en.md).

## 1. Page ↔ UI Components

### 1.1 SearchPanel
**Purpose**: Search-area entry component. It composes `ItemSearchBar` / `ItemSearchResults` and owns outside-click close behavior plus Ctrl and pin-based multi-select lock hints.

**Props**
- `query: string` - Current search keyword.
- `results: Array<{ id: number, name: string, ... }>` - Results from `useItemSearch`.
- `targetAmounts: Map<number, number>` - Badge counts for already-added targets.

**Emits**
- `update:query(value: string)` - Emits the latest keyword on input or when an outside click clears it.
- `select(payload: { id: number, keepOpen: boolean })` - Emits the selected item id together with whether the search box should stay open.

**Source**
- Page passes in `settings.searchQuery`, `results`, and `targetAmountsMap`.
- Page receives `update:query` and calls `setSearchQuery`.
- Page receives `select`, calls `targetsCtrl.add`, and decides whether to clear the query based on `keepOpen`.

---

### 1.2 TargetItemPanel
**Purpose**: Shows target items, outfit bundle targets, edits amount, and clears all.

**Props**
- `targets: Array<{ id: number, name: string, amount: number }>` - Page maps store targets for display.
- `outfitBundles: Array<{ uid: number, setLabel: string, ilvl: number, jobLabel: string, amount: number, itemCount: number, expanded: boolean, items: Array<{ id: number, name: string, isWeapon: boolean }> }>` - Page maps outfit targets for display; `amount` is the target-list count for the whole bundle, `itemCount` is the number of gear pieces in expanded details, and weapon inclusion remains in Page/store rather than being toggled inside the component.

**Emits**
- `remove(id: number)` - Removes a target.
- `update-amount(payload: { id: number, amount: number })` - Updates amount (input + blur).
- `clear()` - Clears all targets.
- `remove-bundle(uid: number)` - Removes one outfit bundle target.
- `update-bundle-amount(payload: { uid: number, amount: number })` - Updates an outfit bundle target amount; the unit is one whole set, and materials are multiplied by that set count.
- `toggle-bundle-expand(uid: number)` - Expands/collapses an outfit bundle's item details.

**Source**
- Page receives events and calls `targetsCtrl.remove / updateAmount / clear` and `outfitTargetsCtrl.remove / updateAmount / toggleExpanded`.

---

### 1.3 MaterialsPanel
**Purpose**: Top-level materials container. It composes `MaterialsToolbar` / `CanCraftSection` / `NotCraftSection` / `CrystalsSection` and owns copy/reset confirmation UI behavior.

**Props**
- `ui: { craftable: Entry[], nonCraftable: Entry[] }`
- `checkedIds: Set<number>` - Checked items.
- `expandOrder: Map<number, number>` - Expansion order (earlier expanded comes first).
- `exportText: string` - Materials export text from `useMaterialsExport`.

**Emits**
- `toggle-expand(id: number)` - Expand/collapse a craftable item.
- `collapse-all()` - Collapse to top level (lock all).
- `expand-all()` - Expand all (controlled by Page).
- `toggle-check(id: number)` - Check/uncheck a material.
- `reset-materials()` - Reset materials progress (expand + checked).

**Source**
- Page passes in `ui` from `useMaterialsList`, `checkedIds/expandOrder` from `materialsCtrl`, and `exportText` from `useMaterialsExport`.
- Page receives events and calls the matching `materialsCtrl` methods; copy success feedback stays inside `MaterialsPanel`.

---

### 1.4 TopNav
**Purpose**: App-shell top bar for title, locale switching, and opening help.

**Props**
- None.

**Emits**
- `open-help()` - Opens the onboarding/help modal.

**Source**
- `App.vue` receives the event and calls `useOnboarding().open()`.

---

### 1.5 OnboardingModal
**Purpose**: App-shell onboarding/help modal.

**Props**
- `isOpen: boolean` - Whether the modal is visible.

**Emits**
- `close()` - Closes the modal.

**Source**
- `App.vue` passes in `useOnboarding().isOpen`.
- `App.vue` receives `close` and calls `useOnboarding().close()`.

---

### 1.6 CanCraftSection
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
  job: string | null
  source: string | null
  displayAmount: number
  displaySuffix: string
}
```

---

### 1.7 NotCraftSection
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

**Notes**
- `overrides` is reserved for selecting a recipe; currently not passed from Page.

---

### 2.4 useMaterialsExport
**Purpose**: Generates export text from the `ui` model returned by `useMaterialsList`.

**Input**
```ts
useMaterialsExport(uiRef)
```

**Output**
- `exportText: ComputedRef<string>` (materials export text)

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
`name` is resolved from the localized `name` map in `items.json`, falling back to `"Unknown"` if missing.

### 4.2 Materials UI entries
`useMaterialsList` converts results to `Entry`, then the UI shows:
- `displayAmount`: if `isCraftable && isExpanded`, show `craftTimes`, otherwise `needAmount`.
- `displaySuffix`: shows `"times"` when expanded, otherwise empty.
- `job`: from `recipe.job` (UI may replace with icons).
- `source`: mapped from `items.obtainMethods` into readable text (localized later).
- `useMaterialsExport().exportText`: output format:
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
