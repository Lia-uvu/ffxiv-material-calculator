# Architecture & Data Model (v0.1)

## Data Split

Internal data is split into two entity types:

- `Item`: stores information about the item itself  
- `Recipe`: stores information about a single crafting action (a recipe)

### `Item` structure (current test version)

```jsonc
{
  "id": 4421,               // Item ID
  "name": "Beastbone Ring", // Item name (Chinese for now)
  "isCrystal": false,       // Whether this item is a crystal
  "obtainMethods": ["CRAFT", "MARKET"]  // How this item can be obtained
}
```

### Recipe structure (current test version)

```json
{
  "id": 2000,             // Recipe ID
  "resultItemId": 4421,   // ID of the resulting item
  "resultAmount": 1,      // Number of items produced per craft
  "job": "GOLDSMITH",     // Crafting job for this recipe
  "itemLevel": 9,         // Item level of the result
  "patch": "1.23",        // Game patch in which this recipe was introduced
  "materials": [          // List of required materials
    { "itemId": 1370, "amount": 1 },
    { "itemId": 2210, "amount": 1 },
    { "itemId": 1000, "amount": 1 },
    { "itemId": 1001, "amount": 1 }
  ]
}
```

## Data flow

There is only **one** source of truth for dynamic state: `settingsStore`.

- Reads always flow **top-down** (store → page → children).
- Writes always go **bottom-up via events** (children → page → store).

---

### View direction (downstream)

- `useCalculatorSettings()` exposes `settings`.
- `CalculatorPage.vue` calls it to get `settings`.
- `CalculatorPage.vue` passes selected fields from `settings` down to child components as `props`  
  (search bar / toggle controls / material tree, etc.).

This line is:

> Settings Store → Page → child components (via `props`)

---

### Event direction (upstream)

- Inside child components, when the user clicks a button / types in an input,  
  they emit events, e.g. `emit('update:xxx', value)` or custom events.
- `CalculatorPage.vue` listens to these events.
- In `CalculatorPage.vue`, we call the functions provided by `useCalculatorSettings()`  
  (or in some cases directly update `settings.xxx`, depending on the design).
- Once `settings` changes, all computed values / components that depend on it update automatically.

This line is:

> Child components (emit) → Page → Settings Store

