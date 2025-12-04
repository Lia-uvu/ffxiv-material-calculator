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
