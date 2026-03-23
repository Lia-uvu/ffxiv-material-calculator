import { shallowRef } from "vue";

export const items = shallowRef([]);
export const recipes = shallowRef([]);
export const outfitSets = shallowRef([]);
export const dataReady = shallowRef(false);

export async function loadData() {
  if (dataReady.value) return;
  const [itemsMod, recipesMod, outfitSetsMod] = await Promise.all([
    import("./items.json"),
    import("./recipes.json"),
    import("./outfitSets.json"),
  ]);
  items.value = itemsMod.default;
  recipes.value = recipesMod.default;
  outfitSets.value = outfitSetsMod.default;
  dataReady.value = true;
}

export function resolveItemName(item, locale = "zh-CN") {
  if (!item) return null;
  const raw = item?.name;
  if (typeof raw === "string") return raw;
  if (raw && typeof raw === "object") {
    return raw[locale] ?? raw["zh-CN"] ?? raw.en ?? Object.values(raw)[0];
  }
  return null;
}
