# 静态数据与部署（v1.0）
本文档记录魔石精计算器所使用的静态数据结构、CI更新方式及部署相关信息。

架构见：[`01-architecture-dataflow.md`](03-architecture-dataflow.md)  
通信规则见：[`02-contracts.md`](02-contracts.md)

## 数据来源
### 中文物品名&配方信息
https://github.com/thewakingsands/ffxiv-datamining-cn
仓库里拿csv文件，用script里`ffxiv-datamining-cn/`里的python脚本清洗成符合现行约定的格式

### 国际服英日物品名：XIVAPI
Base URL (v1 风格常用)：https://xivapi.com
Docs（v1/v2 总入口）：https://xivapi.com/
v1 文档（老版 /Item 这种路由）：https://xivapi.com/docs
v2 文档（/api/sheet/... 这种路由）：https://xivapi.com/docs/v2
Patch list（XIVAPI 自带的 patchlist）：http://cafemaker.wakingsands.com/patchlist   # 文档里给的这个地址


## 静态数据结构

内部数据拆分为两类实体：

- `Item`：记录物品本身的信息
- `Recipe`：记录一次制作行为（配方）的信息

### Item 结构示例
```jsonc
{
  "id": 4421,
  "name": {              // 多语言物品名
    "zh-CN": "兽骨戒指",
    "ja": "ボーンリング",
    "en": "Bone Ring"
  },
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

 


## `data/`内容格式
包含测试数据，正式数据和版本信息
**codex你看到这个帮我写一下版本信息version文件的格式规范**
