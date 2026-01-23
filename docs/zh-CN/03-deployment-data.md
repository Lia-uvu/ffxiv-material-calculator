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

使用方法：调 API 用脚本请求 `src/data/needed_item_ids.json` 需求列表对应的多语言名字。

#### XIVAPI 拉取流程（脚本化）
脚本路径：`scripts/xivapi/`

1. **抓取 raw 数据**：
   ```bash
   node scripts/xivapi/fetchNames.js
   ```
   - 默认读取 `src/data/needed_item_ids.json`。
   - 结果写到 `scripts/xivapi/data/xivapi-names-raw.json`。
   - 请求日志写到 `scripts/logs/`。

2. **清洗为 `{id,en,ja}`**：
   ```bash
   node scripts/xivapi/normalizeXivapiResponse.js
   ```
   - 输出 `scripts/xivapi/data/xivapi-names-normalized.json`。

3. **合并进本地 items.json**：
   ```bash
   node scripts/xivapi/mergeIntoLocalJson.js
   ```
   - 默认更新 `src/data/items.json`。
   - 写入日志到 `scripts/logs/`，包含新增/缺失统计。

#### 服务器友好策略
XIVAPI 是公共服务，尽量减少压力：
- **请求节流**：默认并发 3、每次请求间隔 250ms（可用参数调整）。
- **字段最小化**：只请求 `Name` 字段，避免多余数据。
- **失败重试**：脚本会记录失败、缺失列表，方便后续补抓。
- **分阶段处理**：先抓 raw，再清洗、合并，避免重复请求。

可选参数示例：
```bash
node scripts/xivapi/fetchNames.js \
  --ids src/data/needed_item_ids.json \
  --concurrency 2 \
  --delay-ms 400
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
目前数据更新以手动为主，脚本化流程主要是：
1. 从 `ffxiv-datamining-cn` 更新中文 CSV。
2. 用 `scripts/ffxiv-datamining-cn/` 清洗出符合本项目结构的 JSON。
3. 如需补全英/日名称，执行 `scripts/xivapi/` 的抓取-清洗-合并流程。
4. 更新 `src/data/version.json`（标记数据源与更新时间）。

## Version 文件留档
`src/data/version.json` 用于记录当前数据来源、版本与时间戳。任何数据更新都应同步更新该文件，方便回溯。建议字段包括：
- `data_version`：数据版本号（手动递增）
- `updated_at`：更新日期
- `i18n_source`：国际化名称来源

## 部署
目前使用 Cloudflare Pages 部署：
1. `main` 分支有更新时自动触发构建。
2. 构建产物来自 `vite build`。
3. 生产站点：`https://msjcalc.pages.dev`
