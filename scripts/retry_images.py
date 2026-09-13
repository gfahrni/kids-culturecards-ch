#!/usr/bin/env python3
"""Reessaie les images du manifeste cartes-500 restees non telechargees."""

import csv
import io
import os
import sys
import time
import urllib.error
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "images", "cartes-500", "_manifest.csv")
OUT_DIR = os.path.join(ROOT, "images", "cartes-500")
UA = "kids-culture-g/0.1 (educational flashcards; contact: guillaume@example.org)"
WIDTH, QUALITY = 1024, 82


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 2:
                raise
            wait = 20 * (3 ** attempt)
            print(f"    429 -> pause {wait}s", flush=True)
            time.sleep(wait)


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
        img = img.resize((WIDTH, round(img.height * WIDTH / img.width)), Image.LANCZOS)
    img.save(dst, "WEBP", quality=QUALITY, method=4)


def main():
    with open(MANIFEST, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    todo = [r for r in rows if r["statut"] != "ok"]
    print(f"{len(todo)} images a reessayer", flush=True)

    fixed = 0
    for i, row in enumerate(todo, 1):
        url, cid = row["source_url"], row["id"]
        if not url:
            print(f"[{i}/{len(todo)}] {cid} sans URL, ignore", flush=True)
            continue
        dst = os.path.join(OUT_DIR, f"{cid}.webp")
        print(f"[{i}/{len(todo)}] {cid} ...", flush=True)
        try:
            to_webp(fetch(url), dst)
            row["statut"] = "ok"
            row["fichier"] = os.path.relpath(dst, ROOT)
            fixed += 1
            print("    OK", flush=True)
        except Exception as exc:  # noqa: BLE001
            row["statut"] = f"ERREUR: {exc}"
            print(f"    ECHEC: {exc}", flush=True)
        time.sleep(3)

    with open(MANIFEST, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n{fixed}/{len(todo)} recuperees", flush=True)


if __name__ == "__main__":
    main()
