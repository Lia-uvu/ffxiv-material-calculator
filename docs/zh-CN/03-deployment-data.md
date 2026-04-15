# 静态数据与部署（v2.0）
本文档记录魔石精计算器当前使用的本地 CSV 数据流水线、运行时数据目录和自动发布流程。

架构见：[`01-architecture-dataflow.md`](01-architecture-dataflow.md)  
通信规则见：[`02-contracts.md`](02-contracts.md)

## 数据来源
### CN 配方与物品基础信息
- 上游仓库：在 GitHub Actions 仓库变量中配置
- 读取文件：`Recipe.csv`、`RecipeLevelTable.csv`、`Item.csv` 以及获取途径相关 CSV
- 用途：
  - `Recipe.csv` 生成完整 `recipes`
  - `Item.csv` 与获取来源 CSV 生成 CN base `items`
- 当前接入约定：
  - `FFXIV_DATAMINING_CN_REPO=thewakingsands/ffxiv-datamining-cn`

### EN / JA 物品名称
- 上游仓库：在 GitHub Actions 仓库变量中配置
- 读取文件：各自仓库的 `Item.csv`
- 用途：仅按同一份 `needed_item_ids` 抽取物品名称
- 当前接入约定：
  - `FFXIV_DATAMINING_EN_REPO=InfSein/ffxiv-datamining-mixed`，读取子目录 `en/Item.csv`
  - `FFXIV_DATAMINING_JA_REPO=a1hena/ffxiv-datamining-jp`，读取子目录 `csv/Item.csv`

### 历史遗留工具
- `scripts/xivapi/` 仍保留，但不再进入主流程，也不被 CI 调用。
- 这些脚本现在要求显式传入 `--ids` / `--items`，默认不再读写 `src/data/`。

## Pipeline 步骤
唯一主入口：`scripts/pipeline/run_pipeline.py`

分步脚本：
1. `01_build_recipes.py`：读取 CN CSV，生成 `01_recipes.full.json`
2. `02_extract_needed_item_ids.py`：从 recipes 提取并排序 `needed_item_ids`
3. `03_build_items_cn.py`：按 `needed_item_ids` 过滤 CN `Item.csv` 与获取来源 CSV，生成 `03_items.base.cn.json`
4. `04_build_items_i18n_name.py`：从 EN / JA `Item.csv` 抽取名称，生成 `04_items.i18n_name.json`
5. `05_merge_items.py`：合并 CN base items 与 i18n 名称，缺失时回退 `zh-CN`
6. `06_validate_publish.py`：校验 recipes / items 交叉完整性，并统计缺失翻译
7. `07_publish.py`：在校验通过时发布到 `src/data/`

## 中间产物契约
Pipeline 工作目录默认是 `tmp/pipeline/`，中间产物不进入 Git，仅作为 CI artifact 留档：

- `00_manifest.json`
- `01_recipes.full.json`
- `02_needed_item_ids.json`
- `03_items.base.cn.json`
- `04_items.i18n_name.json`
- `05_items.merged.json`
- `06_validation_report.json`
- `07_publish_diff.json`

另有一个轻量状态文件会提交回仓库：
- `scripts/pipeline/state/last_successful_manifest.json`
- 用途：记录最近一次成功发布时对应的上游 SHA 和当前仓库 SHA，供 CI 判断是否需要重跑

## 运行时数据目录
前端运行时目录 `src/data/` 当前包含：

- `items.json`
- `recipes.json`
- `outfitSetMeta.json`
- `outfitSets.json`
- `index.js`

另有生成的多语言套装名文件：

- `src/i18n/generated/outfitSetNames.json`

最小测试样例已迁出到 `tests/fixtures/pipeline/`，不再放在运行时目录下。

## 运行时数据结构
### Item 结构示例
```jsonc
{
  "id": 4421,
  "name": {
    "zh-CN": "兽骨戒指",
    "en": "Bone Ring",
    "ja": "ボーンリング"
  },
  "isCrystal": false,
  "obtainMethods": [
    "CRAFT",
    "SHOP_MARKET"
  ],
  "obtainMethodDetails": {
    "SHOP_NPC": {
      "priceLow": 9
    }
  }
}
```

### `items.obtainMethods` 枚举
| 值 | 含义 | 来源 |
| --- | --- | --- |
| `CRAFT` | 玩家制作 | `Recipe.csv` |
| `GATHER_MINER` | 采矿工采集 | `GatheringType.csv` + `GatheringItem.csv` + `GatheringPointBase.csv` |
| `GATHER_BOTANIST` | 园艺工采集 | 同上 |
| `GATHER_FISHER` | 捕鱼人采集 | `FishingSpot.csv` |
| `SHOP_NPC` | 金币商店 | `GilShopItem.csv` |
| `EXCHANGE_GC_SEALS` | 军票兑换 | `GCScripShopItem.csv` |
| `EXCHANGE_SCRIP_CRAFTER` | 工匠票据兑换 | `SpecialShop.csv` 店铺名识别 |
| `EXCHANGE_SCRIP_GATHERER` | 采集票据兑换 | `SpecialShop.csv` 店铺名识别 |
| `EXCHANGE_GEMSTONE` | 双色宝石兑换 | `SpecialShop.csv` + `Item.csv` 成本物品名识别 |
| `EXCHANGE_TOME` | 神典石兑换 | `SpecialShop.csv` 店铺名识别 |
| `SHOP_MARKET` | 市场交易 | `Item.csv:IsUntradable` |

### Recipe 结构示例
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
    { "itemId": 2210, "amount": 1 }
  ]
}
```

## CI / 发布
工作流：`.github/workflows/update-data-pipeline.yml`

触发方式：
- `schedule`：每天轮询一次
- `workflow_dispatch`：手动触发，可选 `force_run`
- “检测到 pipeline 输入变化”：在工作流内部比对上次成功发布记录的上游 SHA、仓库 SHA 与当前输入

执行流程：
1. checkout 当前仓库
2. 获取 CN / EN / JA 三个上游仓库当前 HEAD SHA
3. 若上游 SHA 未变化、当前仓库 SHA 与上次成功发布一致，且不是 `force_run`，提前成功退出
4. checkout 三个上游仓库到工作目录
5. 跑 Python pipeline 测试
6. 执行 `scripts/pipeline/run_pipeline.py`
7. 执行 `scripts/pipeline/build_outfit_sets.py`
8. 执行 `npm run build`
9. 上传 `tmp/pipeline/` 全部中间产物为 artifact
10. 若有 diff，则原子提交 `src/data/items.json`、`src/data/recipes.json`、`src/data/outfitSetMeta.json`、`src/data/outfitSets.json`、`src/i18n/generated/outfitSetNames.json` 和状态文件

失败阻断规则：
- recipes 生成失败：阻断
- `needed_item_ids` 为空：阻断
- CN items 生成失败：阻断
- EN / JA `Item.csv` 缺失或解析失败：阻断
- recipes 引用的 item 不存在于 merged items：阻断
- EN / JA 名称缺失：不阻断，仅写入 `06_validation_report.json`

## 当前验证策略
- `tests/test_pipeline.py` 使用 `tests/fixtures/pipeline/` 的本地 CSV fixture
- 覆盖：
  - `ItemSearchCategory == 0` 的 result item 被排除
  - `needed_item_ids` 同时包含产物与材料
  - 票据、双色宝石、神典石、军票、钓鱼等 `obtainMethods` 规则不回归
  - EN / JA 缺失名称时回退 `zh-CN`
  - validation 对缺失 item 引用阻断，对缺失翻译只告警
  - 全流程 smoke test 能从本地 CSV 全量重建最终 `items.json` / `recipes.json`
