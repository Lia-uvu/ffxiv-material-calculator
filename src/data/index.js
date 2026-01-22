import items from "./items.json";
import recipes from "./recipes.json";
import version from "./version.json";

const itemsById = new Map(items.map((item) => [item.id, item]));
const recipesById = new Map(recipes.map((recipe) => [recipe.id, recipe]));

export function getItemById(id) {
  return itemsById.get(id);
}

export function getRecipeById(id) {
  return recipesById.get(id);
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

export { items, recipes, version };
