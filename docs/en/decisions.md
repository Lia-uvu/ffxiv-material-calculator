# Design Decision Log

> Records important design choices in this project and the reasoning behind them.  
> Small tweaks (e.g. minor variable renames) are not logged here.

---

## 2025-12-02: Use numeric IDs consistently

**Type**: Data model / convention  
**Decision**: All IDs (`Item.id` / `Recipe.id` / `resultItemId` / `materials[].itemId`) use the `number` type, instead of numeric strings.

**Rationale**:
- Upstream data sources (FF14 API / wiki, etc.) mostly use numeric IDs, so we don’t need frequent type conversions while mapping.
- Makes it easier to use structures like `Map<number, Item>` in code and avoids bugs caused by mixing strings and numbers.
- The project is still in an early stage; standardizing now avoids a costly migration later.

**Impact**:
- When cleaning external data, if the source uses string IDs, we must explicitly convert them to numbers during import.
- In frontend code, using string IDs such as `"4421"` for internal data is not allowed.

**Status**: Active

---

## 2025-12-02: Split `Item` and `Recipe` into two entities

**Type**: Data model / architecture  
**Decision**: Split game data into two entity types:
- `Item`: describes the item itself (name, whether it’s a crystal, obtain methods, etc.).
- `Recipe`: describes a single crafting action (“which materials → which resulting item”).

**Rationale**:
- Keeps the `Recipe` structure slim and stable, so extending `Item` in the future won’t require changes to all recipes.
- Crafting tree calculation logic only depends on ID relationships (`resultItemId` and `materials[].itemId`), which reduces coupling.
- Makes it easier to gradually add fields to `Item` (gathering nodes, NPCs, categories, etc.) without bloating `Recipe`.

**Impact**:
- Data cleaning scripts must generate `items.json` and `recipes.json` separately during import.
- When displaying recipes on the frontend, we need to look up item info in the `Item` table by `itemId` instead of reading names and other properties directly from `Recipe`.

**Status**: Active

---

## 2025-12-11: Confirm one-way data flow design

**Type**: Architecture  

**Decision**:  
Split data flow into a **view (downstream) direction** and an **event (upstream) direction**:

- View (downstream): Settings Store → Page → child components (via `props`)
- Events (upstream): child components (via `emit`) → Page → Settings Store  

The `data` folder only stores **static** data.  
**Dynamic** data is stored in `settingStore.js`, which lives in the `composables` folder together with other “component logic (dynamic)” code.

---

**Rationale**:  

- Ensure `CalculatorPage.vue` stays very simple:
  - It decomposes `settings` into different `props` and passes them to child components.
  - It converts child components’ emitted events into updates to `settings`.
  - It does *not* maintain extra business state of its own; its responsibility is just:
    - “Which components to import”
    - “How to wire them together”
    In other words: it is a **page configuration** layer, not a business logic layer.
- Clearly separate **static** data from **dynamic** state.

---

**Impact**:  

- `props` / `emit` usage and other data inputs need to respect the one-way data flow:
  - Downstream: read-only `props`
  - Upstream: events → page → store update functions

---

**Status**: Active

---

## 2025-12-12: Settings store API design

**Type**: Code conventions  

**Decision**:  
The `settings` object is **read-only** from the outside.  
Settings can only be modified through dedicated functions exposed by the settings store.

---

**Rationale**:  

- By only exposing:
  - `settings`
  - and a small set of “update functions”
  
  we force all **upstream** changes to go through functions / events.  
  This avoids accidentally mutating state in random places and keeps the data flow explicit.

---

**Impact**:  

- Components `emit` events → pages receive the events → pages call update functions exported from `settingStore` to actually change `settings`.

---

**Status**: Active

---

## 2025-12-14: Layered query sanitization (UI / Store / Core)

**Type**: Data flow / State management  

**Decision**:  
Split search query handling into three layers:

1. `SearchBar` (UI layer):  
   Only handles input-experience concerns (basic cleaning, debouncing, IME behavior, etc.).
2. Store’s `setSearchQuery()` (state layer):  
   Performs the **final unified sanitization** (length limit, `trim`, normalization, etc.).  
   All code paths that write the query must go through this function.
3. `calcMaterials()` and similar core functions (business layer):  
   Only interpret the query in a business sense and compute results.  
   They do **not** perform string-level cleaning.

---

**Rationale**:  

- In the future, the query may come from many sources:
  - Manual input in the search bar  
  - “Recent searches” button  
  - URL parameters (`?q=`)  
  - Keyboard shortcuts that pre-fill values  
- If “final cleaning” only happens inside a single component, other entry points will bypass those rules and cause inconsistent state.
- Clear layering improves maintainability:
  - UI layer can iterate freely on the experience;
  - Store layer guarantees data validity;
  - Core layer focuses solely on “same query → same result.”

---

**Impact**:  

- We need to introduce or standardize a single entry function (e.g. `setSearchQuery(raw)`), and all places that write the query must use it.
- When debugging, we can distinguish:
  - UI experience issues,
  - state sanitization issues,
  - and core computation issues more easily.
- Core computation functions can assume the incoming query already satisfies basic format requirements, reducing duplicated defensive code.

---

**Status**: Active  

---

## 2025-12-14: Defensive design – rules must not rely on UI only

**Type**: Architectural principle / Convention  

**Decision**:  
All rules that affect **result correctness** (e.g. case sensitivity, tokenization/matching strategies, alias handling, multi-language matching, etc.) must be implemented and centralized in the Store / Core business layers, **not** enforced only by UI components.

---

**Rationale**:  

- The UI is just one of many entry points and cannot be the only “gatekeeper”.
- Users can trigger calculations via different channels (URL, shortcuts, future mobile UIs, etc.).  
  If some rules live only in one component, it is easy to bypass them unintentionally.
- Centralizing correctness-related rules in business layers simplifies:
  - global changes;
  - testing and validation;
  - avoiding “fixed it here, forgot it elsewhere” situations.

---

**Impact**:  

- When designing new features, we must clearly distinguish:
  - “Experience-level” rules (impact how nice it feels to use, but not correctness).
  - “Correctness-level” rules (impact whether the result is trustworthy).
- All correctness-level rules should be pushed down into Store / Core.  
  UI only complements them or provides extra hints, not the primary guarantee.
- Unit tests should mainly cover correctness-level rules in Store / Core, rather than depending on component behavior to indirectly validate them.

---

**Status**: Active  

---

## 2025-12-14: Core computation functions stay pure

**Type**: Architecture / Code organization  

**Decision**:  
Core computation logic such as `calcMaterials()` must remain **pure functions**:

- They receive all inputs through parameters (no direct access to Vue components or global store).
- They return results via return values, without mutating external state.

---

**Rationale**:  

- Easier unit testing: core logic can be tested without a Vue environment.
- Future reuse:
  - The same logic can run in a CLI, on the server, or in other front-ends.
  - It is not tied to the current UI stack.
- Lower coupling:  
  the presentation layer only “feeds input / consumes output / renders”,  
  while the business layer focuses solely on “given this input → compute that output”.

---

**Impact**:  

- We need well-defined input structures as function parameters, for example:
  - `targetItems` (target item list);
  - `items` and `recipes` data tables;
  - `options` (calculation options).
- Components that depend on computed results should:
  - call these pure functions,
  - handle state updates and error handling outside the functions.
- When the computation logic changes, we can adjust the pure functions without necessarily modifying components.

---

**Status**: Active  

---

## 2025-12-14: Target item list as the single calculation entry

**Type**: Data model / API design  

**Decision**:  
Core calculation functions only accept a unified **target item list** as the entry, for example:

```ts
type TargetItem = {
  itemId: number;
  quantity: number;
};

type TargetItemList = TargetItem[];
```

Regardless of how target items are chosen (search results, recent items, presets, etc.), as long as we can produce a `TargetItemList`, we can reuse the same material calculation logic.

---

**Rationale**:  

- Decouple “how to select target items” from “how to calculate materials”:
  - Selection can have many UI/interaction forms;
  - Calculation only cares about IDs and quantities.
- Make it easy to add new entry types:
  - e.g. “one-click select a gear set”, “load last record”, etc.  
  All these just need to output the same `TargetItemList` format.
- Stabilize the core API:
  - As requirements evolve, we mainly change UI and target-list generation,
  - while keeping the core calculation function signature relatively stable.

---

**Impact**:  

- The target item panel / list is responsible for turning user actions (selecting, changing quantities) into a `TargetItemList`.
- The calculation entry (e.g. `calcMaterials(targetItems, items, recipes, options)`) no longer accepts scattered parameters; it relies on this unified list.
- Tests can construct different `TargetItemList` samples to cover various scenarios:
  - single item,
  - multiple items,
  - large quantities,
  - mixed recipes, etc.

---

**Status**: Active  
