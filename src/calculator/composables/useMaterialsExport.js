import { computed, unref } from "vue";
import { useI18n } from "vue-i18n";

export function useMaterialsExport(uiRef) {
  const { t, te } = useI18n();

  const exportText = computed(() => {
    const ui = unref(uiRef) ?? {};
    const craftable = (ui.craftable ?? []).filter((e) => !e?.isCrystal);
    const nonCraftable = (ui.nonCraftable ?? []).filter((e) => !e?.isCrystal);
    const crystals = [...(ui.craftable ?? []), ...(ui.nonCraftable ?? [])].filter(
      (e) => e?.isCrystal
    );

    const lines = [];

    lines.push(t("materials.export.craftableTitle"));
    for (const e of craftable) {
      const jobKey = e.job ? `jobs.${e.job}` : null;
      const job = jobKey && te(jobKey) ? t(jobKey) : (e.job ?? t("common.placeholder"));
      const suffix = e.displaySuffix ?? "";
      lines.push(
        t("materials.export.craftableLine", {
          name: e.name,
          amount: e.displayAmount,
          suffix,
          job,
        })
      );
    }

    lines.push("", t("materials.export.nonCraftableTitle"));
    for (const e of nonCraftable) {
      const source = e.source ?? t("common.placeholder");
      const suffix = e.displaySuffix ?? "";
      lines.push(
        t("materials.export.nonCraftableLine", {
          name: e.name,
          amount: e.displayAmount,
          suffix,
          source,
        })
      );
    }

    lines.push("", t("materials.export.crystalsTitle"));
    for (const e of crystals) {
      const suffix = e.displaySuffix ?? "";
      lines.push(
        t("materials.export.crystalLine", {
          name: e.name,
          amount: e.displayAmount,
          suffix,
        })
      );
    }

    return lines.join("\n");
  });

  return { exportText };
}
