# 静态数据与部署（v1.0）
本文档记录魔石精计算器所使用的静态数据结构、CI更新方式及部署相关信息。

架构见：[`01-architecture-dataflow.md`](03-architecture-dataflow.md)  
通信规则见：[`02-contracts.md`](02-contracts.md)

## 数据来源
### 中文物品名&配方信息
仓库地址
https://github.com/thewakingsands/ffxiv-datamining-cn

使用方法：仓库里拿csv文件，用script里`ffxiv-datamining-cn/`里的python脚本清洗成符合现行约定的格式

### 国际服英日物品名：XIVAPI V2
基础域名是：
https://v2.xivapi.com
常用的 V2 数据接口前缀一般是：
https://v2.xivapi.com/api/…
比如（V2 文档里的示例）查 Item 表某个 row：
https://v2.xivapi.com/api/sheet/Item/37362?fields=Name,Description
使用方法：调api用脚本请求data/里从国服仓库扒的needed_item_ids.json需求列表对应的多语言名字


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

## 数据更新CI自动化
部署Github Actions
 


## Version文件留档
CI的log和快照格式写在这里

## 部署
CloudFlare全家桶，绑到GitHub main上了
