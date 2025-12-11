# 设计决策记录（Decision Log）

> 记录项目中比较重要的设计选择，以及当时的原因。  
> 小改小动（比如变量名微调）不在这里记。

---

## 2025-12-02：统一使用 number 类型 ID

**类型**：数据模型 / 约定  
**结论**：所有 ID（`Item.id` / `Recipe.id` / `resultItemId` / `materials[].itemId`）统一使用 `number` 类型，而不是字符串形式的数字。

**原因**：
- 上游数据源（FF14 API / Wiki 等）大多使用数字 ID，映射时不需要频繁做类型转换。
- 方便在代码中使用 `Map<number, Item>` 等结构，避免 string/number 混用导致的 bug。
- 当前项目仍处于早期阶段，在此时统一规范，可以避免后续进行成本较大的迁移。

**影响**：
- 清洗外部数据时，如果源数据为字符串 ID，需要在导入时显式转换为 number。
- 前端代码中禁止使用 `"4421"` 这类字符串 ID 作为内部约定。

**状态**：有效

---

## 2025-12-02：拆分 Item 与 Recipe 两类实体

**类型**：数据模型 
**结论**：将游戏数据拆分为两类实体：
- `Item`：只描述物品本身的信息（名称、是否为水晶、获取方式等）。
- `Recipe`：只描述一次制作行为（“用哪些材料 → 产出哪个成品”）。

**原因**：
- 让 `Recipe` 结构保持瘦且稳定，未来扩展 `Item` 信息时不需要修改所有配方。
- 配方树计算逻辑只依赖 ID 关系（`resultItemId` 和 `materials[].itemId`），降低耦合度。
- 便于在 `Item` 上逐步增加字段（采集点、NPC、分类等），而不让 `Recipe` 变得臃肿。

**影响**：
- 数据清洗脚本在导入时需要分别生成 `items.json` 与 `recipes.json`。
- 前端在展示配方时，需要通过 `itemId` 去 `Item` 表查物品信息，不再从 `Recipe` 中直接读取名称等属性。

**状态**：有效

---

## 2025-12-11：确认单向数据流设计
**类型**：架构  
**结论**：将游戏数据拆分为视图方向（下行）和事件方向（上行）：
- 视图方向（下行）：Settings Store → Page → 子组件（props）
- 事件方向（上行）：子组件（emit） → Page → Settings Store
data文件夹内只存静态数据，动态数据保存在settingStore.js里，放在负责组件逻辑(动态)的composables文件夹内

**原因**：
- 确保CalculatorPage.vue CalculatorPage 做的事情非常单纯：
  把 settings 拆成不同 props 给小组件；
  把小组件 emit 回来的事件转成对 settings 的修改。
  它自己不需要有额外的业务状态，只有 “引入哪个组件 & 怎么连线” 这种“页面配置”的职责
- 区分静态数据和动态数据

**影响**：
- props和emit等数据输入需要检查是否符合数据流顺序

**状态**：有效

---

## 2025-12-11：规范watch/props/emit使用位置
**类型**：代码规范
**结论**：ref / reactive 和 watch 应该“挨着逻辑放”

和“设置本身”相关的东西（默认值、当前值、持久化、重置）
👉 全都放在 useCalculatorSettings.js 里，那里就是这块逻辑的“老家”。

和“某个页面临时 UI 状态”相关的（比如某个弹窗是否打开，只对这个页面有意义）
👉 放在 CalculatorPage.vue 里，用自己的 ref 管就好。

watch 要放在哪？
👉 放在需要产生“副作用”的那个地方，比如：

设置变了要写 localStorage → 放在 useCalculatorSettings 里；

设置变了要触发某个页面特效 → 放在 CalculatorPage.vue 里。


谁关心这件事，谁就 import ref/watch，在自己那边贴着用。