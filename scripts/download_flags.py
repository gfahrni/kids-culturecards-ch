#!/usr/bin/env python3
"""Telecharge les drapeaux resolus (images/_flags.json) en WebP.

Sortie: images/cartes-500/<id>.webp (meme dossier que les autres cartes).
"""

import io
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "images", "cartes-500")
FLAGS = os.path.join(ROOT, "images", "_flags.json")
COMMONS = "https://commons.wikimedia.org/w/api.php"
UA = "kids-culture-g/0.1 (educational flashcards; contact: guillaume@example.org)"
WIDTH, QUALITY = 1024, 82


def api(params):
    url = COMMONS + "?" + urllib.parse.urlencode(dict(params, format="json", formatversion="2"))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 5:
                raise
            wait = 8 * (attempt + 1)
            print(f"   429 -> {wait}s", flush=True)
            time.sleep(wait)
    return {}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 3:
                raise
            time.sleep(10 * (attempt + 1))


def to_webp(raw, dst):
    img = Image.open(io.BytesIO(raw))
    img.load()
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    if img.width > WIDTH:
        img = img.resize((WIDTH, round(img.height * WIDTH / img.width)), Image.LANCZOS)
    img.save(dst, "WEBP", quality=QUALITY, method=4)


def main():
    flags = json.load(open(FLAGS, encoding="utf-8"))
    items = [(cid, v) for cid, v in flags.items() if v.get("file")]

    info = {}
    for i in range(0, len(items), 50):
        chunk = items[i:i + 50]
        titles = "|".join("File:" + v["file"] for _, v in chunk)
        data = api({"action": "query", "prop": "imageinfo",
                    "iiprop": "url|extmetadata", "iiurlwidth": WIDTH, "titles": titles})
        for page in data.get("query", {}).get("pages", []):
            ii = page.get("imageinfo", [{}])[0]
            em = ii.get("extmetadata", {})
            info[page["title"]] = {
                "thumb": ii.get("thumburl") or ii.get("url"),
                "licence": em.get("LicenseShortName", {}).get("value", ""),
                "auteur": em.get("Artist", {}).get("value", ""),
            }
        print(f"   imageinfo {min(i + 50, len(items))}/{len(items)}", flush=True)
        time.sleep(1)

    done = 0
    for cid, v in items:
        title = "File:" + v["file"]
        meta = info.get(title, {})
        url = meta.get("thumb")
        dst = os.path.join(OUT_DIR, f"{cid}.webp")
        if not url:
            print(f"MANQUE {cid} {v['file']}", flush=True)
            continue
        try:
            if not os.path.exists(dst):
                to_webp(fetch(url), dst)
            flags[cid].update({"thumb": url, "licence": meta.get("licence", ""),
                               "auteur": meta.get("auteur", "")})
            done += 1
            print(f"OK {cid}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"ERREUR {cid}: {exc}", flush=True)
        time.sleep(0.4)

    json.dump(flags, open(FLAGS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n{done}/{len(items)} drapeaux telecharges")


if __name__ == "__main__":
    main()
