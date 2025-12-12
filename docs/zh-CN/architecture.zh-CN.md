# 架构与数据模型（v0.1）

## 文件结构

```txt
src/
  calculator/
    pages/
      CalculatorPage.vue

    components/                 // ui组件
      ItemSearchBar.vue         // 搜索框
      TargetItemPanel.vue       // 成品选择栏
      CraftOptionsControls.vue  // 界面小组件
      MaterialList.vue          // 材料列表

    composables/
      settingStore.js           // 存储设置
      useItemSearch.js          // 组件逻辑-搜索框
      useMaterialTree.js        // 组件逻辑-材料树

    core/
      calcMaterial.js           // 底层计算逻辑

  data/                         // 静态数据来源
    items.json
    recipes.json
```

```vue
<template>
  <!-- 1. 结构 -->
</template>

<script setup>
// 2.1 import
// 2.2 defineProps / defineEmits / defineExpose
// 2.3 const refs / reactive / computed
// 2.4 functions
// 2.5 lifecycle hooks
</script>

<style scoped>
/* 3. 样式 */
</style>
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

## 数据流向

数据源头只有一个：settingsStore；

读总是从上往下（store → page → 子）；

写总是通过事件从下往上（子 → page → store）。

### 视图方向（下行）

useCalculatorSettings() 暴露出 settings；

CalculatorPage.vue 调用它，拿到 settings；

CalculatorPage.vue 把 settings 的某些字段作为 props 传给子组件（搜索栏 / 开关控件 / 材料树之类）。

这条线是：Settings Store → Page → 子组件（props）

### 事件方向（上行）

子组件里，用户点按钮 / 输入文字 → 用 emit('update:xxx', value) 或者自定义事件；

CalculatorPage.vue 接到这个事件；

在 CalculatorPage.vue 里调用 useCalculatorSettings 提供的 方法（或者直接改 settings.xxx）；

settings 改了，所有依赖它的 computed / 组件自动更新。

这条线是：子组件（emit） → Page → Settings Store

