#!/usr/bin/env python3
"""Trouve, pour chaque carte problematique, un titre Wikipedia FR avec image.

Tente plusieurs candidats par carte et sauvegarde le premier qui a une image.
Sortie: images/_override_targets.json (reprise possible).
"""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "images", "_override_targets.json")
API = "https://fr.wikipedia.org/w/api.php"
UA = "kids-culture-g/0.1 (image override lookup)"

CANDS = {
    "7-2-009": ["Morse (animal)", "Morse"],
    "7-3-059": ["Hippocampe (poisson)", "Hippocampe (genre)"],
    "2-2-004": ["Vienne (Autriche)"],
    "2-1-004": ["Sion (Valais)"],
    "2-1-005": ["Fribourg (ville suisse)"],
    "2-1-013": ["Altdorf (Uri)"],
    "4-3-005": ["Amazone (fleuve)"],
    "4-3-006": ["Mississippi (fleuve)"],
    "4-3-033": ["Congo (fleuve)"],
    "4-2-009": ["Arctique", "Océan Arctique", "Océan glacial arctique"],
    "6-3-004": ["Mercure (planète)"],
    "6-3-005": ["Vénus (planète)"],
    "6-3-006": ["Mars (planète)"],
    "6-3-007": ["Jupiter (planète)"],
    "6-3-008": ["Saturne (planète)"],
    "6-3-009": ["Uranus (planète)"],
    "6-3-010": ["Neptune (planète)"],
    "6-3-011": ["Pluton (planète naine)"],
    "6-3-013": ["Titan (lune)"],
    "6-3-015": ["Io (lune)"],
    "6-3-022": ["Galaxie d'Andromède"],
    "6-3-033": ["Orion (constellation)"],
    "6-3-038": ["Big Bang", "Univers", "Cosmologie"],
    "6-3-044": ["Télescope spatial James-Webb", "James-Webb (télescope spatial)"],
    "6-3-056": ["Télescope spatial Hubble", "Hubble (télescope spatial)"],
    "3-1-012": ["Pilatus (montagne)", "Mont Pilatus", "Pilatus (sommet)"],
    "3-1-038": ["Diablerets (massif)", "Les Diablerets (montagne)", "Diablerets (montagne)"],
    "5-2-013": ["Cathédrale Notre-Dame de Paris", "Notre-Dame de Paris"],
    "5-2-016": ["Alhambra", "Alhambra (Grenade)", "Alhambra (Espagne)"],
    "5-3-009": ["Cathédrale Saint-Basile-le-Bienheureux", "Cathédrale Saint-Basile"],
    "5-3-020": ["Christ Rédempteur (Rio de Janeiro)", "Christ Rédempteur"],
    "6-1-003": ["Vallée de Lauterbrunnen", "Lauterbrunnen (vallée)", "Lauterbrunnen"],
    "6-1-011": ["Sarine", "Chutes de la Sarine"],
    "6-1-012": ["Saut du Doubs", "Chutes du Doubs", "Doubs (rivière)"],
    "6-1-025": ["Val Bavona", "Bavona", "Bavona (rivière)"],
    "6-1-028": ["Creux de l'Envers", "Vallorbe", "Vallée de Joux"],
    "5-2-017": ["Monastère de l'Escurial", "Monastère de San Lorenzo de El Escorial"],
    "5-1-005": ["Pont de la Chapelle", "Kapellbrücke"],
    "5-3-005": ["Moai", "Île de Pâques"],
}

_last = [0.0]
DELAY = 1.5


def api_get(params):
    url = API + "?" + urllib.parse.urlencode(dict(params, format="json", formatversion="2"))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(8):
        delta = time.monotonic() - _last[0]
        if delta < DELAY:
            time.sleep(DELAY - delta)
        _last[0] = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 7:
                raise
            wait = 8 * (attempt + 1)
            print(f"   429 -> {wait}s", flush=True)
            time.sleep(wait)


def has_image(cand):
    data = api_get({
        "action": "query", "redirects": 1,
        "prop": "pageimages|pageprops", "piprop": "thumbnail|name",
        "pithumbsize": 1024, "ppprop": "wikibase_item", "titles": cand,
    })
    q = data.get("query", {})
    norm = {}
    for x in q.get("normalized", []):
        norm[x["from"]] = x["to"]
    for x in q.get("redirects", []):
        norm[x["from"]] = x["to"]
    final = norm.get(norm.get(cand, cand), norm.get(cand, cand))
    page = next((p for p in q.get("pages", []) if p.get("title") == final and "missing" not in p), None)
    if page and page.get("thumbnail"):
        return page["title"], page["thumbnail"]["source"], page.get("pageprops", {}).get("wikibase_item")
    return None


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    data = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    for cid, cands in CANDS.items():
        if data.get(cid):
            continue
        found = None
        for cand in cands:
            try:
                got = has_image(cand)
            except Exception as exc:  # noqa: BLE001
                print(f"!! {cid} {cand}: {exc}", flush=True)
                got = None
            if got:
                found = {"titre": got[0], "image": got[1], "qid": got[2]}
                break
        data[cid] = found
        json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{'OK  ' if found else 'FAIL'} {cid} -> " + (found["titre"] if found else "aucun candidat"), flush=True)

    ok = sum(1 for v in data.values() if v)
    print(f"\n{ok}/{len(CANDS)} resolus")
    for cid, v in data.items():
        if not v:
            print(f"  a revoir: {cid}")


if __name__ == "__main__":
    main()
