import json
import os
import time
import urllib.parse
import urllib.request

BASE_URL = os.environ.get("XIVAPI_BASE_URL", "https://v2.xivapi.com/api/sheet")
CN_BASE_URL = os.environ.get(
    "XIVAPI_CN_BASE_URL", "https://cafemaker.wakingsands.com/api/sheet"
)
SHEET = os.environ.get("XIVAPI_SHEET", "Item")
LOCALES = [
    locale.strip()
    for locale in os.environ.get("XIVAPI_LOCALES", "ja,zh-CN").split(",")
    if locale.strip()
]
VERSION = os.environ.get("XIVAPI_VERSION", "7.0")
ROWS_PARAM = os.environ.get("ROWS_PARAM", "rows")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "100"))
MIN_DELAY_MS = int(os.environ.get("MIN_DELAY_MS", "200"))
ITEMS_PATH = os.environ.get("ITEMS_PATH", os.path.join("src", "data", "items.json"))
USER_AGENT = os.environ.get(
    "USER_AGENT",
    "ffxiv-material-calculator/1.0 (+https://github.com/unknown/ffxiv-material-calculator)",
)

if BATCH_SIZE <= 0:
    raise ValueError(f"Invalid BATCH_SIZE: {BATCH_SIZE}")

if MIN_DELAY_MS < 0:
    raise ValueError(f"Invalid MIN_DELAY_MS: {MIN_DELAY_MS}")


def resolve_base_url(locale: str) -> str:
    return CN_BASE_URL if locale == "zh-CN" else BASE_URL


def resolve_language(locale: str) -> str:
    return "zh" if locale == "zh-CN" else locale


def to_item_rows(payload: dict) -> list:
    return payload.get("rows") or payload.get("results") or payload.get("data") or []


def fetch_names(batch: list[int], locale: str) -> list[dict]:
    base_url = resolve_base_url(locale)
    query = {
        ROWS_PARAM: ",".join(str(item_id) for item_id in batch),
        "fields": "Name",
        "language": resolve_language(locale),
    }
    if VERSION:
        query["version"] = VERSION
    url = f"{base_url}/{SHEET}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return to_item_rows(payload)


with open(ITEMS_PATH, "r", encoding="utf-8") as handle:
    items = json.load(handle)

items_by_id = {item["id"]: item for item in items}
item_ids = [item["id"] for item in items if item.get("id") is not None]

batches = [
    item_ids[index : index + BATCH_SIZE]
    for index in range(0, len(item_ids), BATCH_SIZE)
]

for batch_index, batch in enumerate(batches, start=1):
    for locale in LOCALES:
        rows = fetch_names(batch, locale)
        for row in rows:
            fields = row.get("fields") or row.get("Fields") or row
            item_id = row.get("row_id") or row.get("ID") or row.get("id")
            name = fields.get("Name") if isinstance(fields, dict) else None
            if not item_id or not name:
                continue
            item = items_by_id.get(int(item_id))
            if not item:
                continue
            if "name" not in item:
                item["name"] = {}
            item["name"][locale] = name
        print(
            f"[names] batch={batch_index}/{len(batches)} locale={locale} ids={len(batch)}"
        )
        if MIN_DELAY_MS > 0:
            time.sleep(MIN_DELAY_MS / 1000)

with open(ITEMS_PATH, "w", encoding="utf-8") as handle:
    json.dump(items, handle, ensure_ascii=False, indent=2)
    handle.write("\n")

print(f"[names] done. updated={len(items)} file={ITEMS_PATH}")
