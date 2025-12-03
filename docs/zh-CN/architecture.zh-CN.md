# 架构与数据模型（v0.1）

## 数据拆分

内部数据拆分为两类实体：

- `Item`：记录物品本身的信息
- `Recipe`：记录一次制作行为（配方）的信息

### Item 结构（当前测试版）

```jsonc
{
  "id": 4421,             // 物品id
  "name": "兽骨戒指",      // 物品中文名
  "isCrystal": false,     // 是否为水晶
  "obtainMethods": ["CRAFT", "MARKET"]  //该物品获取方式
}
```

### Recipe 结构（当前测试版）

```jsonc
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
```