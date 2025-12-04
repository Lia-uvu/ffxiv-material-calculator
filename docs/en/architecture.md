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
