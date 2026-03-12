import { createI18n } from "vue-i18n";
import messages from "./messages";

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
  messages,
});

export default i18n;
