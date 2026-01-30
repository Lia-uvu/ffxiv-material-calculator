# 静态数据与部署（v1.0）
本文档记录魔石精计算器所使用的静态数据结构、CI更新方式及部署相关信息。

架构见：[`01-architecture-dataflow.md`](01-architecture-dataflow.md)  
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

使用方法：调 API 用脚本请求 `src/data/needed_item_ids.json` 需求列表对应的多语言名字。

#### XIVAPI 拉取流程（脚本化）
脚本路径：`scripts/xivapi/`

1. **抓取增量 NDJSON（支持断点续跑）**：
   ```bash
   node scripts/xivapi/fetchNames.js
   ```
   - 默认读取 `src/data/needed_item_ids.json`。
   - 成功结果按行追加到 `src/data/nameMap.incremental.ndjson`（中间态）。
   - 每条成功记录会写入 `scripts/xivapi/cache/nameFetch.checkpoint.ndjson` 用于断点续跑。
   - 失败记录输出到 `scripts/xivapi/cache/failed-ids.ndjson`，支持后续重跑。
   - 日志统一写到 `scripts/logs/YYYY-MM-DD.log`。

2. **合并进本地 items.json**：
   ```bash
   node scripts/xivapi/mergeIntoLocalJson.js
   ```
   - 读取 `src/data/nameMap.incremental.ndjson`，合并到 `src/data/items.json`。
   - 只在 `item.name.en/ja` 为空或等于中文占位时写入，避免覆盖已有数据。
   - 合并统计写入 `scripts/logs/YYYY-MM-DD.log`。

#### 服务器友好策略
XIVAPI 是公共服务，尽量减少压力：
- **请求节流**：默认 rps=3、并发=6，保证整体 QPS 温和（可用参数调整）。
- **字段最小化**：只请求 `Name` 字段，避免多余数据。
- **失败重试**：429 指数退避 + jitter，失败会落盘到 failed-ids 方便重跑。
- **分阶段处理**：先拉取 NDJSON，再合并入 items.json，避免重复请求。

可选参数示例：
```bash
node scripts/xivapi/fetchNames.js \
  --ids src/data/needed_item_ids.json \
  --rps 2 \
  --concurrency 4
```

重跑失败列表：
```bash
node scripts/xivapi/fetchNames.js \
  --retry-failed scripts/xivapi/cache/failed-ids.ndjson
```

合并后清空增量文件（可选）：
```bash
node scripts/xivapi/mergeIntoLocalJson.js --clear-incremental
```

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
    "制作",               // 玩家制作
    "市场购买",           // 市场交易
    "采矿工",             // 采矿工采集
    "园艺工",             // 园艺工采集
    "捕鱼人",             // 捕鱼人采集
    "NPC 购买",           // 金币商店（GilShop）
    "军票兑换",           // 军票商店（GCScripShop）
    "工匠票据兑换",       // 工匠票据兑换
    "采集票据兑换",       // 采集票据兑换
    "双色宝石兑换",       // 双色宝石兑换
    "神典石兑换"          // 神典石兑换
    ],
  "obtainMethodDetails": { // 可选：获取途径补充信息
    "NPC 购买": {          // 金币商店的价格信息（如果可用）
      "priceLow": 9        // 来自 Item.csv 的 Price{Low}
    }
  }
}
```

#### `items.obtainMethods` 字段说明
`obtainMethods` 仍然是**字符串数组**，仅在现有结构上做扩展。每个值均可被独立组合，便于后续 UI 标注/筛选。

| 值 | 含义 | CSV 来源与字段 |
| --- | --- | --- |
| `制作` | 玩家制作 | `Recipe.csv`：`Item{Result}` |
| `采矿工` | 采矿工采集 | `GatheringType.csv` + `GatheringItem.csv` + `GatheringPointBase.csv`：`GatheringType`、`Item[0..7]` |
| `园艺工` | 园艺工采集 | 同上（采集类型名为“采伐/割草”） |
| `捕鱼人` | 捕鱼人采集 | `FishingSpot.csv`：`Item[0..9]` |
| `NPC 购买` | 金币商店 | `GilShopItem.csv`：`Item` |
| `军票兑换` | 军票商店 | `GCScripShopItem.csv`：`Item` |
| `工匠票据兑换` | 工匠票据兑换 | `SpecialShop.csv`：`Item{Receive}[i][j]` + `Item{Cost}[i][j]`，**以成本物品（票据货币）的名称**包含“巧手”与“票”为准 |
| `采集票据兑换` | 采集票据兑换 | `SpecialShop.csv`：`Item{Receive}[i][j]` + `Item{Cost}[i][j]`，**以成本物品（票据货币）的名称**包含“大地”与“票”为准 |
| `双色宝石兑换` | 双色宝石兑换 | `SpecialShop.csv`：`Item{Receive}[i][j]` + `Item{Cost}[i][j]`，成本物品为“双色宝石” |
| `神典石兑换` | 神典石兑换 | `SpecialShop.csv` + `TomestonesItem.csv`：成本物品在 `TomestonesItem.csv` 的 `Item` 列 |
| `市场购买` | 市场交易 | `Item.csv`：`IsUntradable`（可交易即加入） |

#### `items.obtainMethodDetails` 字段说明
当某些获取方式存在额外数据时，用该对象补充说明。当前仅定义金币商店价格：
- `NPC 购买.priceLow`：来自 `Item.csv` 的 `Price{Low}`，仅当该物品出现在 `GilShopItem.csv` 且价格>0 时写入。

**明确忽略项（不进入结构与清洗输出）**：
`DisposalShopItem.csv`，以及任务/令行/成就/周常奖励类：`QuestClassJobReward.csv`、`LeveRewardItemGroup.csv`、`Achievement.csv`、`WeeklyBingoRewardData.csv`。

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
目前数据更新以手动为主，脚本化流程主要是：
1. 从 `ffxiv-datamining-cn` 更新中文 CSV。
2. 用 `scripts/ffxiv-datamining-cn/` 清洗出符合本项目结构的 JSON。
3. 如需补全英/日名称，执行 `scripts/xivapi/` 的抓取（增量 NDJSON）→ 合并流程。
4. 运行日志统一写入 `scripts/logs/YYYY-MM-DD.log`。

## 部署
目前使用 Cloudflare Pages 部署：
1. `main` 分支有更新时自动触发构建。
2. 构建产物来自 `vite build`。
3. 生产站点：`https://msjcalc.pages.dev`
