import { createI18n } from "vue-i18n";
import en from "./messages/en";
import ja from "./messages/ja";
import zhCN from "./messages/zh-CN";

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
  messages: { en, ja, "zh-CN": zhCN },
});

export default i18n;
