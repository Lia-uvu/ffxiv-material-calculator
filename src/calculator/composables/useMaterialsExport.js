import { computed, unref } from "vue";
import { useI18n } from "vue-i18n";
import { OBTAIN_PRIORITY_ORDER, getPrimaryMethod } from "../core/obtainMethodUtils";

function getTier(id) {
  if (id <= 7) return "shard";
  if (id <= 13) return "crystal";
  return "cluster";
}

function getElementName(name, locale) {
  if (locale === "zh-CN") return name.split("之")[0];
  if (locale === "ja") return name.replace(/シャード|クリスタル|クラスター$/, "");
  return name.split(" ")[0];
}

export function useMaterialsExport(uiRef) {
  const { t, te, locale } = useI18n();

  const exportText = computed(() => {
    const ui = unref(uiRef) ?? {};
    const craftable = (ui.craftable ?? []).filter((e) => !e?.isCrystal);
    const nonCraftable = (ui.nonCraftable ?? []).filter((e) => !e?.isCrystal);
    const crystals = [...(ui.craftable ?? []), ...(ui.nonCraftable ?? [])].filter(
      (e) => e?.isCrystal
    );

    const lines = [];

    // === 制作清单 ===
    lines.push("=== 制作清单 ===");
    lines.push("");

    // 按职业分组
    const craftByJob = new Map();
    for (const e of craftable) {
      const jobKey = e.job ? `jobs.${e.job}` : null;
      const jobLabel = jobKey && te(jobKey) ? t(jobKey) : (e.job ?? t("common.placeholder"));
      if (!craftByJob.has(jobLabel)) craftByJob.set(jobLabel, []);
      craftByJob.get(jobLabel).push(e);
    }

    for (const [jobLabel, items] of craftByJob) {
      lines.push(`【${jobLabel}】`);
      lines.push("");
      for (const e of items) {
        lines.push(`${e.name} × ${e.craftTimes}次 → ${e.needAmount}个`);
        lines.push("");
      }
    }

    // === 采集清单 ===
    lines.push("=== 采集清单 ===");
    lines.push("");

    // 按最高优先级来源分组，并按优先级顺序排列各组
    const gatherByMethod = new Map();
    for (const e of nonCraftable) {
      const primary = getPrimaryMethod(e.obtainMethods);
      const methodKey = primary ? `obtainMethods.${primary}` : null;
      const methodLabel =
        methodKey && te(methodKey) ? t(methodKey) : (e.source ?? t("common.placeholder"));
      if (!gatherByMethod.has(primary ?? methodLabel)) {
        gatherByMethod.set(primary ?? methodLabel, { label: methodLabel, items: [] });
      }
      gatherByMethod.get(primary ?? methodLabel).items.push(e);
    }

    // 按 OBTAIN_PRIORITY_ORDER 排序组的顺序
    const sortedMethodKeys = [...gatherByMethod.keys()].sort((a, b) => {
      const ra = OBTAIN_PRIORITY_ORDER.indexOf(a);
      const rb = OBTAIN_PRIORITY_ORDER.indexOf(b);
      const ea = ra === -1 ? Infinity : ra;
      const eb = rb === -1 ? Infinity : rb;
      return ea - eb;
    });

    for (const key of sortedMethodKeys) {
      const { label, items } = gatherByMethod.get(key);
      lines.push(`【${label}】`);
      lines.push("");
      for (const e of items) {
        lines.push(`${e.name} × ${e.needAmount}`);
        lines.push("");
      }
    }

    // === 水晶消耗 ===
    lines.push("=== 水晶消耗 ===");
    lines.push("");

    const crystalByTier = { shard: [], crystal: [], cluster: [] };
    const TIER_ORDER = ["cluster", "crystal", "shard"];

    for (const c of crystals) {
      const tier = getTier(c.id);
      if (crystalByTier[tier]) {
        crystalByTier[tier].push(c);
      }
    }

    for (const tier of TIER_ORDER) {
      const items = crystalByTier[tier];
      if (!items.length) continue;
      const tierLabel = t(`materials.crystalTiers.${tier}`);
      lines.push(`【${tierLabel}】`);
      lines.push("");
      const sorted = items.slice().sort((a, b) => a.id - b.id);
      const parts = sorted.map((c) => {
        const elemName = getElementName(c.name, locale.value);
        return `${elemName} × ${c.needAmount}`;
      });
      lines.push(parts.join(" | "));
      lines.push("");
    }

    return lines.join("\n").trimEnd();
  });

  return { exportText };
}
