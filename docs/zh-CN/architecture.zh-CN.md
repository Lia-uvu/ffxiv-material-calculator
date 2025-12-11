# 架构与数据模型（v0.1）

## 文件结构

```txt
src/
  calculator/
    pages/                  // 页面（单个）
      CalculatorPage.vue

    components/             // ui组件
      ItemSearchBar.vue     // 搜索框
      TargetItemPanel.vue   // 成品选择栏
      CraftOptionsPanel.vue // 界面小组件
      MaterialTree.vue      // 材料树

    composables/
      useItemSearch.js      // 组件逻辑-搜索框
      useMaterialTree.js    // 组件逻辑-材料树

    core/
      calcMaterials.js      // 底层计算逻辑

  data/                     // 数据来源
    items.json
    recipes.json
```


## 数据拆分

内部数据拆分为两类实体：

- `Item`：记录物品本身的信息
- `Recipe`：记录一次制作行为（配方）的信息

### Item 结构（当前测试版）

```jsonc
{
  "id": 4421,
  "name": "兽骨戒指",      // 多语言物品名（未来会写成列表）
  "isCrystal": false,     // 是否为“水晶类素材”（碎晶/水晶/晶簇），用于在计算时决定要不要单独统计/排除
  "obtainMethods": [      // 该物品所有获取方式，用于标记
    "CRAFT",              // 玩家制作
    "MARKET",             // 市场交易
    "NPC",                // 商人NPC购买
    "GATHER_MINER",       // 矿工采集
    "GATHER_BOTANIST"     // 园艺工采集
    ]
}
```

### Recipe 结构（当前测试版）

```jsonc
{
  "id": 2000,             // 配方id
  "resultItemId": 4421,   // 产物的物品id
  "resultAmount": 1,      // 制作一次配方生成几个成品
  "job": "GOLDSMITH",     // 该配方对应的职业
  "itemLevel": 9,         // 成品品级
  "patch": "1.23",        // 配方实装版本
  "materials": [          // 材料清单
    { "itemId": 1370, "amount": 1 },
    { "itemId": 2210, "amount": 1 },
    { "itemId": 1000, "amount": 1 },
    { "itemId": 1001, "amount": 1 }
  ]
}
```