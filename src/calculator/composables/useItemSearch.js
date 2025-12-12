import { computed, unref } from "vue";

export function useItemSearch(itemsRef, queryRef, limit = 20) {
  const results = computed(() => {
    const items = unref(itemsRef) ?? [];
    const q = String(unref(queryRef) ?? "").trim().toLowerCase();

    if (!q) return [];

    const matched = items.filter((it) =>
      String(it.name ?? "").toLowerCase().includes(q)
    );

    return matched.slice(0, limit);
  });

  return { results };
}
