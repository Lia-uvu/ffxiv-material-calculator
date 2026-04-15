// 获取途径优先级（从高到低）
// 用于：多来源物品的归类 + 采集清单各组的显示顺序
export const OBTAIN_PRIORITY_ORDER = [
  "EXCHANGE_TOME",
  "EXCHANGE_GEMSTONE",
  "SHOP_NPC",
  "EXCHANGE_SCRIP_CRAFTER",
  "EXCHANGE_SCRIP_GATHERER",
  "EXCHANGE_GC_SEALS",
  "GATHER_MINER",
  "GATHER_BOTANIST",
  "GATHER_FISHER",
  "SHOP_MARKET",
];

/**
 * 从物品的多个获取途径中，选出优先级最高的一个。
 * @param {string[]} obtainMethods
 * @returns {string|null}
 */
export function getPrimaryMethod(obtainMethods) {
  if (!obtainMethods?.length) return null;
  let best = null;
  let bestRank = Infinity;
  for (const m of obtainMethods) {
    const rank = OBTAIN_PRIORITY_ORDER.indexOf(m);
    const effectiveRank = rank === -1 ? Infinity : rank;
    if (effectiveRank < bestRank) {
      bestRank = effectiveRank;
      best = m;
    }
  }
  return best ?? obtainMethods[0];
}
