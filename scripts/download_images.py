#!/usr/bin/env python3
"""Telecharge et normalise en WebP les images du dataset cartes-500.

Sources: images/_resolution.json + images/_override_targets.json
+ images/_override_commons.json. Les drapeaux sont ignores (traitement a part).
Sortie: images/cartes-500/<id>.webp + images/cartes-500/_manifest.csv
"""

import csv
import io
import json
import os
import re
import time
import urllib.error
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "cartes-500")
OUT_DIR = os.path.join(ROOT, "images", "cartes-500")
MANIFEST = os.path.join(OUT_DIR, "_manifest.csv")
ID_RE = re.compile(r"^(\d+-\d+-\d+)_")
SKIP_DIRS = {".git", "scripts", "images", "cartes-500"}
UA = "kids-culture-g/0.1 (image download)"
WIDTH = 1024
QUALITY = 82


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return json.load(fh)


def card_list():
    out = []
    for theme in sorted(os.listdir(DEST)):
        tdir = os.path.join(DEST, theme)
        if not os.path.isdir(tdir):
            continue
        for sub in sorted(os.listdir(tdir)):
            sdir = os.path.join(tdir, sub)
            if not os.path.isdir(sdir):
                continue
            for name in sorted(os.listdir(sdir)):
                m = ID_RE.match(name)
                if m and name.endswith(".md"):
                    out.append({"id": m.group(1), "theme": theme, "sub": sub, "file": name})
    return out


def source_for(cid, cache, targets, commons):
    if cid in commons:
        c = commons[cid]
        return c["image"], c["titre"], "commons", c.get("licence", ""), c.get("auteur", "")
    if cid in targets and targets[cid]:
        t = targets[cid]
        return t["image"], t["titre"], "wikipedia", "", ""
    c = cache.get(cid)
    if c and c.get("status") == "ok":
        return c["image"], c.get("page"), "wikipedia", "", ""
    return None, None, None, "", ""


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 5:
                raise
            wait = 5 * (attempt + 1)
            print(f"      429 -> {wait}s", flush=True)
            time.sleep(wait)
        except Exception:
            if attempt == 5:
                raise
            time.sleep(2 ** attempt)


def to_webp(raw, dst):
    img = Image.open(io.BytesIO(raw))
    img.load()
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    if img.width > WIDTH:
        ratio = WIDTH / img.width
        img = img.resize((WIDTH, round(img.height * ratio)), Image.LANCZOS)
    img.save(dst, "WEBP", quality=QUALITY, method=4)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cache = load("images/_resolution.json")
    targets = load("images/_override_targets.json")
    commons = load("images/_override_commons.json")

    rows, ok, fail, skip = [], 0, 0, 0
    for card in card_list():
        if card["theme"] == "drapeaux":
            skip += 1
            continue
        url, page, src, licence, author = source_for(card["id"], cache, targets, commons)
        dst = os.path.join(OUT_DIR, f"{card['id']}.webp")
        if not url:
            rows.append({**card, "source_url": "", "source_page": page or "", "licence": "",
                         "fichier": "", "statut": "MANQUANTE"})
            print(f"MANQUE {card['id']}", flush=True)
            continue
        if os.path.exists(dst):
            rows.append({**card, "source_url": url, "source_page": page or "", "licence": licence,
                         "fichier": os.path.relpath(dst, ROOT), "statut": "ok"})
            ok += 1
            continue
        try:
            raw = fetch(url)
            to_webp(raw, dst)
            rows.append({**card, "source_url": url, "source_page": page or "", "licence": licence,
                         "fichier": os.path.relpath(dst, ROOT), "statut": "ok"})
            ok += 1
            print(f"OK     {card['id']}", flush=True)
        except Exception as exc:  # noqa: BLE001
            rows.append({**card, "source_url": url, "source_page": page or "", "licence": licence,
                         "fichier": "", "statut": f"ERREUR: {exc}"})
            fail += 1
            print(f"ERREUR {card['id']}: {exc}", flush=True)
        time.sleep(0.3)

    with open(MANIFEST, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "theme", "sub", "file", "source_url",
                                                "source_page", "licence", "fichier", "statut"])
        writer.writeheader()
        writer.writerows(rows)

    total = ok + fail + sum(1 for r in rows if r["statut"] == "MANQUANTE")
    print(f"\nTelechargees: {ok}  Erreurs: {fail}  Manquantes: {total - ok - fail}")
    print(f"Manifeste: {os.path.relpath(MANIFEST, ROOT)}")


if __name__ == "__main__":
    main()
