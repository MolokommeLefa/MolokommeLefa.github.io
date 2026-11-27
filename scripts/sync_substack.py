import json, re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.request import Request, urlopen

FEED_URL = "https://lefa1creative.substack.com/feed"
request = Request(FEED_URL, headers={"User-Agent": "LefaPortfolioRSS/1.0"})
with urlopen(request, timeout=30) as response:
    root = ET.fromstring(response.read())

def clean(value):
    value = re.sub(r"<(script|style)[^>]*>[\\s\\S]*?</\\1>", " ", value or "", flags=re.I)
    return re.sub(r"\\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()

posts = []
for item in root.findall("./channel/item")[:6]:
    title, link = clean(item.findtext("title")), (item.findtext("link") or "").strip()
    if not title or not link:
        continue
    raw_date = item.findtext("pubDate") or ""
    try:
        date = parsedate_to_datetime(raw_date).strftime("%d %b %Y")
    except Exception:
        date = raw_date
    posts.append({"title": title, "link": link, "date": date, "description": clean(item.findtext("description"))[:240]})

with open("substack-posts.json", "w", encoding="utf-8") as output:
    json.dump({"updated": datetime.now(timezone.utc).strftime("%d %b %Y"), "posts": posts}, output, ensure_ascii=False, indent=2)
print(f"Synced {len(posts)} Substack posts")
