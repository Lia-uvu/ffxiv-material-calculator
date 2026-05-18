import { computed, shallowRef } from "vue";

export const items = shallowRef([]);
export const recipes = shallowRef([]);
export const outfitSets = shallowRef([]);
export const catalogReady = shallowRef(false);
export const recipesReady = shallowRef(false);
export const dataReady = computed(() => catalogReady.value && recipesReady.value);

let catalogPromise = null;
let recipesPromise = null;

export async function loadCatalogData() {
  if (catalogReady.value) return;
  if (catalogPromise) return catalogPromise;

  catalogPromise = Promise.all([
    import("./items.json"),
    import("./outfitSets.json"),
  ]).then(([itemsMod, outfitSetsMod]) => {
    items.value = itemsMod.default;
    outfitSets.value = outfitSetsMod.default;
    catalogReady.value = true;
  }).finally(() => {
    catalogPromise = null;
  });

  return catalogPromise;
}

export async function loadRecipeData() {
  if (recipesReady.value) return;
  if (recipesPromise) return recipesPromise;

  recipesPromise = import("./recipes.json").then((recipesMod) => {
    recipes.value = recipesMod.default;
    recipesReady.value = true;
  }).finally(() => {
    recipesPromise = null;
  });

  return recipesPromise;
}

export async function loadData() {
  await Promise.all([loadCatalogData(), loadRecipeData()]);
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
