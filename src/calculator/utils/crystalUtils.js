export function getCrystalTier(id) {
  if (id <= 7) return "shard";
  if (id <= 13) return "crystal";
  return "cluster";
}

export function getCrystalElementName(name, locale) {
  if (locale === "zh-CN") return name.split("之")[0];
  if (locale === "ja") return name.replace(/シャード|クリスタル|クラスター$/, "");
  return name.split(" ")[0];
}
