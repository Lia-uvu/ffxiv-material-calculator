// 做了输入清洗和匹配
import Fuse from "fuse.js";
import { computed, unref } from "vue";
import { useI18n } from "vue-i18n";
import { resolveItemName } from "../../data";

export function useItemSearch(itemsRef, queryRef, limit = 20) {
  const { locale, t } = useI18n();

  const indexedItems = computed(() => {
    const items = unref(itemsRef) ?? [];
    const currentLocale = locale.value;
    const fallbackName = t("common.unknown");
    return items.map((item) => ({
      ...item,
      searchName: resolveItemName(item, currentLocale) ?? fallbackName,
    }));
  });

  const fuse = computed(() => {
    return new Fuse(indexedItems.value, {
      keys: ["searchName"],
      threshold: 0.3,
      ignoreLocation: true,
    });
  });

  const results = computed(() => {
    const q = String(unref(queryRef) ?? "").trim();
    // trim()负责清洗前后空格
    if (!q) return [];

    const matched = fuse.value.search(q).map((result) => result.item);

    return matched.slice(0, limit).map((item) => ({
      ...item,
      name: item.searchName,
    }));
  });

  return { results };
}
