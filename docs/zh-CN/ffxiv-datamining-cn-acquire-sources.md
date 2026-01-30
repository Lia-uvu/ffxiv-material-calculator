# ffxiv-datamining-cn：与物品获取途径相关的 CSV

以下是从 `thewakingsands/ffxiv-datamining-cn` 数据集中**和物品获取途径相关**的常见 CSV 类型，便于后续补充 `items.obtainMethods`。

> 该清单来自对上游仓库根目录 CSV 文件名的核对（例如可用 `ls <repo> | rg -n "^(Item|Recipe|GatheringItem|GatheringPointBase|GatheringType|FishingSpot|GilShopItem|SpecialShop|TomestonesItem|GCScripShopItem|DisposalShopItem|QuestClassJobReward|LeveRewardItemGroup|Achievement|WeeklyBingoRewardData)\\.csv$"` 进行验证）。

## 1. 基础物品信息（可用于推断市场/NPC等）
- `Item.csv`：物品基础属性（如 `IsUntradable`、`Price{Low}`、`ItemUICategory`）。

## 2. 制作（Crafting）
- `Recipe.csv`：制作产物与材料（`Item{Result}`、`Item{Ingredient}[n]`）。

## 3. 采集 / 采矿 / 园艺（Gathering）
- `GatheringItem.csv`：采集物品到 `Item` 的映射。
- `GatheringPointBase.csv`：采集点上的物品槽位（`Item[0..7]`）。
- `GatheringType.csv`：采集类型名称（可区分采矿/园艺）。

## 4. 钓鱼（Fishing）
- `FishingSpot.csv`：钓场与可钓物品（`Item[0..9]`）。

## 5. 商店 / 兑换 / 点数
- `GilShopItem.csv`：金币商店物品。
- `SpecialShop.csv`：兑换商店（`Item{Receive}[i][j]`、`Item{Cost}[i][j]`），用于识别工匠票据/采集票据/双色宝石/神典石兑换。
- `TomestonesItem.csv`：神典石物品列表（`Item`）。
- `GCScripShopItem.csv`：军票/军票商店兑换（`Cost{GCSeals}` + `Item`）。
- `DisposalShopItem.csv`：物品回收/交换（`Item{Disposed}` / `Item{Received}`）。

## 6. 任务 / 令行 / 成就 / 周常奖励
- `QuestClassJobReward.csv`：任务奖励物品与数量（`Reward{Item}`、`Reward{Amount}`）。
- `LeveRewardItemGroup.csv`：理符奖励物品（`Item[n]`）。
- `Achievement.csv`：成就奖励物品（`Item`）。
- `WeeklyBingoRewardData.csv`：每周挑战日志奖励物品（`Reward{Item}`）。
