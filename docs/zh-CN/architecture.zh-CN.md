# 架构与数据模型（v0.1）

## 文件结构

```txt
src/
  calculator/
    pages/
      CalculatorPage.vue

    components/                 // ui组件
      ItemSearchBar.vue         // 搜索框
      ItemSearchResults.vue     // 下拉搜索结果
      TargetItemPanel.vue       // 成品选择栏
      CraftOptionsControls.vue  // 界面设置小组件
      MaterialList.vue          // 计算出的材料列表

    composables/
      settingStore.js           // 存储设置
      useItemSearch.js          // 搜索逻辑
      useMaterialTree.js        // 材料列表逻辑，带计算入口

    core/
      calcMaterial.js           // 底层计算逻辑

  data/                         // 静态数据来源
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


# 页面数据流与架构复盘（Vue + Store + Composables + Core）

这套页面遵循一个稳定的单向数据流：**状态自上而下、事件自下而上**。  
核心是把规则分成两类：**正确性级**（影响结果可信度）与 **体验级**（只影响显示/交互）。

---

## 规则分层

### 正确性级规则（必须在 Store/Core）
会影响“结果是否可信/计算是否正确”的规则必须集中在 **Store/Core**，不能只靠 UI：
- `targets` 的数量合法性（默认值、最小值、非数字处理等）
- 计算逻辑（配方选择、循环检测、产出量校验等）
- 配方覆盖 `overrides` 的解释与回退规则

### 体验级规则（可在 Page/Composable/Component）
只影响“怎么展示/好不好用”，不改变真实结果：
- 是否显示水晶（隐藏/展示）
- 排序方式、折叠展开、筛选搜索、分页
- 展示用 `name`、`Unknown` 文案

---

## 角色分工（谁该做什么）

### 1) Store：全局真实状态 + 写入接口（actions）
Store 持有页面的“真状态”，对外只开放：
- **readonly state**（外部可读不可直接改）
- **actions**（唯一写入入口）

典型内容：
- `settings.searchQuery`：当前搜索输入
- `targets: Array<{ id, amount }>`：目标列表（业务输入）
- `recipeOverrides`：配方覆盖（业务输入）
- actions：`setSearchQuery / addTarget / removeTarget / updateTargetAmount ...`

**为什么要 actions？**  
因为正确性兜底（例如 amount 最小为 1、默认 1）应该集中在 store，避免 UI 被绕过。

---

### 2) Core：纯计算（输入 → 输出）
Core 是纯函数层，不依赖 Vue，不读写 store，只负责：
- 接收业务输入
- 输出计算结果

例如：
- `calcMaterials({ targets, recipes, overrides }) -> { materials, crafts, picks, warnings }`

Core 的接口应稳定、可测试，并且 `targets` 的结构要与 store 一致（本项目收口为 `{ id, amount }`）。

---

### 3) Composable：派生/胶水（return computed，不改全局真状态）
Composable 的定位是“派生器 / selector / view-model”，常见职责：
- 支持 `ref/computed/普通值` 输入（用 `unref`）
- 把 core 输出映射成 UI 需要的结构（Map → Array、补 name、排序）
- 做轻量体验级清洗/匹配（trim/lowercase/filter）

关键点：Composable **return computed/ref**，而不是 emit/callback 把数据“推回” page。  
`computed` 是声明式派生（公式），不会引入回路；`emit` 是事件推送，适合报告用户意图。

---

### 4) Page：容器/协调者（接线与分发）
Page 负责“接线”：
- 从 store 读取 readonly state（props 来源）
- 调用 composables 生成派生数据（computed）
- 把派生数据传给展示组件渲染
- 接收组件 emit 的用户意图，然后调用 store actions 更新真状态

Page 可以选择把体验级规则放在这里（比如“方案1：page 过滤后再传给组件”）：
- `filteredMaterialEntries = showCrystals ? materialEntries : materialEntries.filter(!isCrystal)`

后期 page 变大时，这些 computed 可以“整块搬走”到 view-model composable 或 container 组件，迁移成本很低。

---

### 5) Components：展示层（props in, emit out）
展示组件不碰 store、不算业务结果，只做：
- 渲染 props
- emit 用户意图（例如 `update:query`, `select`, `remove`, `update-amount`）

例子：
- SearchBar 只 emit 字符串
- Results 只 emit 被点中的 id
- “已选列表”的累积永远在 store 的 `targets` 中完成

---

## 两条典型链路（按数据流向复刻就能拼回去）

### A) 搜索链路
1. 用户输入 → SearchBar `emit("update:query", value)`
2. Page 接收事件 → 调 store action：`setSearchQuery(value)`（更新真状态）
3. `useItemSearch(items, queryRef)` 内部 computed 自动做：清洗（trim/lowercase）+ 匹配 → 得到 `results`
4. Page 将 `results` 传给 Results 组件渲染
5. 用户点击某项 → Results `emit("select", id)`
6. Page 调 store action：`addTarget(id)`（targets 更新，后续计算自动联动）

要点：**搜索 composable 只负责派生结果，不负责写入 targets。写入 targets 是 store 的职责。**

---

### B) 材料计算链路
1. `targets/overrides` 属于 store 真状态
2. Page 调 `useMaterialsList({ targets, recipes, overrides, items })`
3. composable 内部 computed 调用 core：`calcMaterials(...)` 得到 `calcResult`
4. composable 再把 `calcResult.materials(Map)` 映射成 `materialEntries(Array)`（补 name、排序）
5. Page 可选进一步做体验级过滤（如隐藏水晶），然后把最终 entries 传给 `MaterialsList` 渲染

要点：**core 负责正确性计算；composable/page 负责把结果变成 UI 能用的“展示形”。**

---

## computed vs emit：为什么看似相同却会影响“是否单向”

- `computed`：声明式派生（像公式），依赖变了自动更新；适合“结果/列表/派生数据”
- `emit`：事件通知（用户做了什么）；适合“用户意图”上报给上层去改 state

因此，“page 调 composable 返回 computed 再传给组件”不是双向回路，它只是把 `computed(() => ...)` 搬到了模块里；真正容易绕的是让 composable “emit/推回” page。

---

## 一句话复盘（忘了就看这句）
**Store 管真状态 + actions，Core 管纯计算，Composable 管派生（return computed），Page 管接线分发，Component 管渲染和 emit 用户意图。**
