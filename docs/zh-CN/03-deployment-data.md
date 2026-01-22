# 静态数据与部署（v1.0）
本文档记录魔石精计算器所使用的静态数据结构、更新方式及部署相关信息。

架构见：[`01-architecture-dataflow.md`](03-architecture-dataflow.md)  
通信规则见：[`02-contracts.md`](02-contracts.md)
## 静态数据结构

内部数据拆分为两类实体：

- `Item`：记录物品本身的信息
- `Recipe`：记录一次制作行为（配方）的信息

### Item 结构示例
```jsonc
{
  "id": 4421,
  "name": "兽骨戒指",      // 多语言物品名（未来会写成map）
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

### Recipe 结构示例
```jsonc
{
  "id": 2000,             // 配方id
  "resultItemId": 4421,   // 产物的物品id
  "resultAmount": 1,      // 制作一次配方生成几个成品
  "job": "GOLDSMITH",     // 该配方对应的职业（可选）
  "itemLevel": 9,         // 成品品级（可选）
  "patch": "1.23",        // 配方实装版本
  "materials": [          // 材料清单
    { "itemId": 1370, "amount": 1 },
    { "itemId": 2210, "amount": 1 },
    { "itemId": 1000, "amount": 1 },
    { "itemId": 1001, "amount": 1 }
  ]
}
```

## XIVAPI v2 数据更新脚本（Patch ≤ 7.0）

项目提供了脚本来拉取 XIVAPI v2 的配方与道具数据，并按当前静态数据格式输出：  

- 配方：`scripts/xivapi/fetch-recipes.mjs` 以 JSONL 形式流式写入（`recipes_7.0.jsonl`）。  
- 道具：`scripts/xivapi/fetch-items.mjs` 根据配方统计涉及的物品 ID，再批量查询并写入 JSONL（`items_7.0.jsonl`）。  
- 转换：`scripts/xivapi/jsonl-to-array.mjs` 将 JSONL 转成 JSON 数组，覆盖 `src/data/*.json`。  

脚本默认使用 `fields` 参数拉取最小字段（对关联字段使用 `@as(raw)` 仅取 ID），并包含断点续跑、限速、指数退避等礼貌访问策略。  
具体用法见 `scripts/xivapi/README.md`。  


## `data/`内容
包含测试数据，正式数据和版本信息
写一下版本信息文件的格式