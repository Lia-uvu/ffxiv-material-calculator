
**`docs/decisions.md`（记录我们今天的规范）：**

```md
# 设计决策记录（Decision Log）

## 2025-12-02: 统一使用 number 类型 ID

**决策：**

- `Item.id` / `Recipe.id` / `resultItemId` / `materials[].itemId` 全部使用 `number` 类型。

**原因：**

- 上游数据源通常以数字 ID 表示物品和配方，映射成本更低。
- 方便在代码中使用 `Map<number, ...>` 等结构，避免 string/number 混用。
- 现在处于项目早期，在此时确定规范，可以避免后续大规模迁移。

---

## 2025-12-02: 拆分 Item / Recipe 两类数据实体

**决策：**

- 将游戏数据拆分为 `Item` 与 `Recipe`。
- 物品自身属性（获取方式、是否为水晶、未来采集点信息等）存放在 `Item` 中。
- `Recipe` 仅描述「用哪些材料 → 产出哪个成品」，不存储物品属性。

**原因：**

- 让 `Recipe` 结构保持瘦且稳定，方便将来扩展 `Item` 信息而不影响配方逻辑。
- 配方树计算只依赖 `itemId` 关系，降低耦合度。
