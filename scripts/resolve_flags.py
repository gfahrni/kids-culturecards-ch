#!/usr/bin/env python3
"""Resout les 121 drapeaux via Wikidata P41 (image de drapeau).

Sortie: images/_flags.json (id -> qid, file, thumb, licence, auteur).
Reprise possible: les cartes deja resolues sont sautees.
"""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "cartes-500", "drapeaux")
OUT = os.path.join(ROOT, "images", "_flags.json")
UA = "kids-culture-g/0.1 (educational flashcards; contact: guillaume@example.org)"
ID_RE = re.compile(r"^(\d+-\d+-\d+)_")
DELAY = 1.2
_last = [0.0]


def api(base, params):
    url = base + "?" + urllib.parse.urlencode(dict(params, format="json", formatversion="2"))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(6):
        delta = time.monotonic() - _last[0]
        if delta < DELAY:
            time.sleep(DELAY - delta)
        _last[0] = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 5:
                raise
            wait = 10 * (attempt + 1)
            print(f"   429 -> {wait}s", flush=True)
            time.sleep(wait)


def card_title(path):
    lines = [ln.strip() for ln in open(path, encoding="utf-8")]
    for i, ln in enumerate(lines):
        if ln == "# Titre":
            return next(x for x in lines[i + 1:] if x)
    return ""


def candidates(title, sub):
    t = title.strip()
    if sub == "suisse" and t.lower() != "suisse":
        return [f"canton de {t}", f"canton du {t}", f"canton d'{t}", t]
    return [t]


def find_p41(title, sub):
    for cand in candidates(title, sub):
        data = api("https://www.wikidata.org/w/api.php", {
            "action": "wbsearchentities", "search": cand,
            "language": "fr", "uselang": "fr", "limit": 5,
        })
        ids = [h["id"] for h in data.get("search", [])]
        if not ids:
            continue
        ents = api("https://www.wikidata.org/w/api.php", {
            "action": "wbgetentities", "ids": "|".join(ids),
            "props": "claims|labels|descriptions", "languages": "fr|en",
        })
        for qid in ids:
            ent = ents.get("entities", {}).get(qid, {})
            p41 = ent.get("claims", {}).get("P41")
            if p41:
                fname = p41[0]["mainsnak"].get("datavalue", {}).get("value")
                if fname:
                    return qid, fname
    return None, None


def flag_cards():
    out = []
    for sub in sorted(os.listdir(DEST)):
        sdir = os.path.join(DEST, sub)
        if not os.path.isdir(sdir):
            continue
        for name in sorted(os.listdir(sdir)):
            m = ID_RE.match(name)
            if m and name.endswith(".md"):
                out.append({"id": m.group(1), "sub": sub,
                            "titre": card_title(os.path.join(sdir, name))})
    return out


def main():
    data = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    cards = flag_cards()
    for c in cards:
        if data.get(c["id"]):
            continue
        qid, fname = find_p41(c["titre"], c["sub"])
        data[c["id"]] = {"titre": c["titre"], "qid": qid, "file": fname}
        json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{'OK  ' if fname else 'FAIL'} {c['id']} {c['titre']:34s} -> {fname}", flush=True)

    ok = [c for c in cards if data.get(c["id"], {}).get("file")]
    print(f"\n{len(ok)}/{len(cards)} drapeaux resolus")
    for c in cards:
        if not data.get(c["id"], {}).get("file"):
            print(f"  a revoir: {c['id']} {c['titre']}")


if __name__ == "__main__":
    main()
