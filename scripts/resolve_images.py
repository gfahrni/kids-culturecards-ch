#!/usr/bin/env python3
"""Extrait les cartes et resout une image de tete via fr.wikipedia.

Sortie: images/_resolution.csv et images/_resolution.json (cache).
Aucun telechargement d'image: uniquement les URLs et la couverture.
"""

import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "images")
CACHE = os.path.join(OUT_DIR, "_resolution.json")
CSV_PATH = os.path.join(OUT_DIR, "_resolution.csv")

API = "https://fr.wikipedia.org/w/api.php"
UA = "kids-culture-g/0.1 (coverage report)"
BATCH = 50
ID_RE = re.compile(r"^(\d+-\d+-\d+)_")
FLAG_THEME = "drapeaux"
SKIP_DIRS = {".git", "scripts", "images"}


def card_files():
    for theme in sorted(os.listdir(ROOT)):
        tdir = os.path.join(ROOT, theme)
        if not os.path.isdir(tdir) or theme in SKIP_DIRS:
            continue
        for sub in sorted(os.listdir(tdir)):
            sdir = os.path.join(tdir, sub)
            if not os.path.isdir(sdir):
                continue
            for name in sorted(os.listdir(sdir)):
                if not name.endswith(".md"):
                    continue
                m = ID_RE.match(name)
                if not m:
                    continue
                yield {
                    "id": m.group(1),
                    "theme": theme,
                    "subtheme": sub,
                    "file": os.path.relpath(os.path.join(sdir, name), ROOT),
                }


def card_title(path):
    """Le format est `# Titre` puis la valeur sur la ligne suivante."""
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh]
    for i, line in enumerate(lines):
        if line == "# Titre":
            for nxt in lines[i + 1:]:
                if nxt:
                    return nxt
    for line in lines:
        if line.startswith("# ") and line != "# Titre":
            return line[2:].strip()
    return ""


MIN_INTERVAL = 0.6
_last_call = [0.0]


def api_get(params):
    params = dict(params, format="json", formatversion="2")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(7):
        delta = time.monotonic() - _last_call[0]
        if delta < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - delta)
        _last_call[0] = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:  # noqa: PERF203
            if exc.code != 429 or attempt == 6:
                raise
            wait = 5 * (2 ** attempt)
            print(f"  429 -> pause {wait}s", file=sys.stderr)
            time.sleep(wait)
        except Exception as exc:  # noqa: BLE001
            if attempt == 6:
                raise
            wait = 2 ** attempt
            print(f"  retry {attempt + 1} ({exc}) dans {wait}s", file=sys.stderr)
            time.sleep(wait)


def resolve(titles):
    """titre demande -> {status, page, qid, image} via un lot d'appels API."""
    result = {t: {"status": "missing", "page": None, "qid": None, "image": None} for t in titles}

    normalized, redirects = {}, {}
    pages = {}
    for i in range(0, len(titles), BATCH):
        chunk = titles[i:i + BATCH]
        data = api_get({
            "action": "query",
            "prop": "pageimages|pageprops",
            "piprop": "thumbnail|name",
            "pithumbsize": 1024,
            "ppprop": "wikibase_item",
            "redirects": 1,
            "titles": "|".join(chunk),
        })
        q = data.get("query", {})
        for item in q.get("normalized", []):
            normalized[item["from"]] = item["to"]
        for item in q.get("redirects", []):
            normalized[item["from"]] = item["to"]
        for page in q.get("pages", []):
            if "missing" in page:
                continue
            pages[page["title"]] = page
        time.sleep(0.1)

    def final_title(t):
        return normalized.get(normalized.get(t, t), normalized.get(t, t))

    for t in titles:
        page = pages.get(final_title(t))
        if not page:
            hits = api_get({"action": "query", "list": "search", "srsearch": t, "srlimit": 1})
            found = hits.get("query", {}).get("search", [])
            if not found:
                continue
            data = api_get({
                "action": "query",
                "prop": "pageimages|pageprops",
                "piprop": "thumbnail|name",
                "pithumbsize": 1024,
                "ppprop": "wikibase_item",
                "titles": found[0]["title"],
            })
            got = data.get("query", {}).get("pages", [])
            if not got or "missing" in got[0]:
                continue
            page = got[0]
        thumb = page.get("thumbnail", {}).get("source")
        result[t] = {
            "status": "ok" if thumb else "no-image",
            "page": page.get("title"),
            "qid": page.get("pageprops", {}).get("wikibase_item"),
            "image": thumb,
        }
    return result


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cache = {}
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as fh:
            cache = json.load(fh)

    cards = list(card_files())
    print(f"{len(cards)} cartes trouvees")

    todo = {}
    for c in cards:
        if c["theme"] == FLAG_THEME:
            continue
        if cache.get(c["id"], {}).get("status") == "ok":
            continue
        c["title"] = card_title(c["file"])
        todo.setdefault(c["theme"], []).append(c)

    def save_cache():
        with open(CACHE, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, ensure_ascii=False, indent=1)

    for theme, items in todo.items():
        print(f"-> {theme}: {len(items)} a resoudre")
        for i in range(0, len(items), BATCH):
            chunk_cards = items[i:i + BATCH]
            res = resolve([c["title"] for c in chunk_cards])
            for c in chunk_cards:
                cache[c["id"]] = res.get(
                    c["title"], {"status": "missing", "page": None, "qid": None, "image": None}
                )
            save_cache()
            print(f"   {min(i + BATCH, len(items))}/{len(items)}")

    save_cache()

    rows, stats = [], {}
    for c in cards:
        title = card_title(c["file"])
        if c["theme"] == FLAG_THEME:
            status, page, qid, image = "flag-special", None, None, None
        else:
            r = cache.get(c["id"], {"status": "missing"})
            status, page, qid, image = r.get("status"), r.get("page"), r.get("qid"), r.get("image")
        rows.append({
            "id": c["id"], "theme": c["theme"], "subtheme": c["subtheme"],
            "titre": title, "page_wikipedia": page, "qid": qid,
            "image_url": image, "statut": status, "fichier": c["file"],
        })
        stats.setdefault(c["theme"], Counter())[status] += 1

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("\nCouverture par theme:")
    grand = Counter()
    for theme in sorted(stats):
        s = stats[theme]
        grand.update(s)
        print(f"  {theme:32s} " + "  ".join(f"{k}={v}" for k, v in sorted(s.items())))
    print("\nTotal: " + "  ".join(f"{k}={v}" for k, v in sorted(grand.items())))
    print(f"\nCSV: {os.path.relpath(CSV_PATH, ROOT)}")


if __name__ == "__main__":
    main()
