# 架构与数据模型（v0.1）

## 数据拆分

内部数据拆分为两类实体：

- `Item`：物品本身的信息
- `Recipe`：一次制作行为（配方）

### Item 结构（当前测试版）

```jsonc
{
  "id": 4421,
  "name": "兽骨戒指",
  "isCrystal": false,
  "obtainMethods": ["CRAFT", "MARKET"]
}

### Recipe 结构（当前测试版）
{
  "id": 2000,
  "resultItemId": 4421,
  "resultAmount": 1,
  "job": "GOLDSMITH",
  "itemLevel": 9,
  "patch": "1.23",
  "materials": [
    { "itemId": 1370, "amount": 1 },
    { "itemId": 2210, "amount": 1 },
    { "itemId": 1000, "amount": 1 },
    { "itemId": 1001, "amount": 1 }
  ]
}
