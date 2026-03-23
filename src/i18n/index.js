import { createI18n } from "vue-i18n";
import en from "./messages/en";
import ja from "./messages/ja";
import zhCN from "./messages/zh-CN";
import outfitSetNames from "./generated/outfitSetNames.json";

// Merge generated outfit set names into each locale's outfitSets namespace
function mergeOutfitSetNames(locale, messages) {
  const setEntries = {};
  for (const [key, names] of Object.entries(outfitSetNames)) {
    setEntries[key] = names[locale] || names["zh-CN"];
  }
  return {
    ...messages,
    outfitSets: {
      ...messages.outfitSets,
      set: setEntries,
    },
  };
}

function detectLocale() {
  const langs = [navigator.language, ...(navigator.languages ?? [])];
  for (const l of langs) {
    if (!l) continue;
    if (l.startsWith("zh")) return "zh-CN";
    if (l.startsWith("ja")) return "ja";
    if (l.startsWith("en")) return "en";
  }
  return "en";
}

const i18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: "zh-CN",
  messages: {
    en: mergeOutfitSetNames("en", en),
    ja: mergeOutfitSetNames("ja", ja),
    "zh-CN": mergeOutfitSetNames("zh-CN", zhCN),
  },
});

export default i18n;
