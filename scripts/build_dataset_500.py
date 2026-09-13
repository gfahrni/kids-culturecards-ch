#!/usr/bin/env python3
"""Copie une selection de 500 cartes dans cartes-500/ (rien n'est supprime).

Drapeaux: conserves integralement (121).
Autres themes: on garde les references les plus connues pour un public suisse.
"""

import csv
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "cartes-500")
CACHE = os.path.join(ROOT, "images", "_resolution.json")
SKIP_DIRS = {".git", "scripts", "images", "cartes-500"}
ID_RE = re.compile(r"^(\d+-\d+-\d+)_")

KEEP = {
    "animaux": {
        "suisse": "001 002 003 004 005 006 007 010 011 012 013 014 015 016 017 018 019 020 021 024 032 035 039 042 046 052 053 056 059 060 064 065 071 072 075",
        "europe": "001 002 003 004 005 009 012 013 014 023 025 027 028 035 037 038 039 042 047 057 058 060 061 062 066 067 069 071 072 073 074 075 076",
        "monde": "001 002 003 004 005 006 007 008 009 010 011 012 013 014 015 016 017 021 022 024 026 031 040 042 045 048 049 050 052 056 059 060 070 072 074 075 076",
    },
    "capitales-chefs-lieux": {
        "suisse": "001 002 003 004 005 006 007 008 009 010 011 012 013 014 015 016 017 018 019 020 021 022 023 024 025 026 027",
        "europe": "001 002 003 004 005 006 007 008 009 010 011 012 013 014 015",
        "monde": "001 002 003 004 005 007 008 009 024 027 028 029 031",
    },
    "montagnes": {
        "suisse": "001 002 003 004 005 006 007 008 009 010 011 012 013 014 033 034 038 039",
        "europe": "001 002 003 004 005 007 016",
        "monde": "001 002 003 004 005 006 007 008 009 010",
    },
    "lacs-mers-oceans-rivieres": {
        "lacs": "001 002 003 004 005 006 007 008 009 010 011 012 039 040 041 044 045 047 048 049 050 054",
        "mers-et-oceans": "001 002 003 004 005 006 007 008 009 010 014 018 023 025 034 035 036 037",
        "fleuves-et-rivieres": "001 002 003 004 005 006 007 008 009 013 020 021 026 033 034",
    },
    "merveilles-et-espace": {
        "suisse": "001 002 003 004 005 006 008 009 010 011 012 013 016 017 018 021 022 023",
        "monde": "001 002 003 004 005 007 010 011 012 015 016 019 020 024 025 026 027 029 031 032 033 039 041 054 059",
        "espace": "001 002 003 004 005 006 007 008 009 010 011 012 013 014 015 019 021 022 026 028 032 033 038 041 042 044 046 048 050 052 056 058",
    },
    "monuments": {
        "suisse": "001 002 003 004 005 006 007 009 010 012 013 015 016 018 021 023 024 025 028 029",
        "europe": "001 002 003 004 005 006 007 008 009 010 011 012 013 016 022 028 029 030 031 032",
        "monde": "001 002 003 004 005 006 007 008 009 010 011 013 020 035",
    },
}


def keep_ids():
    ids = set()
    for theme, subs in KEEP.items():
        for sub, nums in subs.items():
            for n in nums.split():
                ids.add(f"{theme}|{sub}|{n}")
    return ids


def main():
    keep = keep_ids()
    copied = 0
    for theme in sorted(os.listdir(ROOT)):
        tdir = os.path.join(ROOT, theme)
        if not os.path.isdir(tdir) or theme in SKIP_DIRS or theme == "drapeaux":
            continue
        for sub in sorted(os.listdir(tdir)):
            sdir = os.path.join(tdir, sub)
            if not os.path.isdir(sdir):
                continue
            for name in sorted(os.listdir(sdir)):
                m = ID_RE.match(name)
                if not m or not name.endswith(".md"):
                    continue
                num = m.group(1).split("-")[-1]
                if f"{theme}|{sub}|{num}" not in keep:
                    continue
                dst_dir = os.path.join(DEST, theme, sub)
                os.makedirs(dst_dir, exist_ok=True)
                shutil.copy2(os.path.join(sdir, name), os.path.join(dst_dir, name))
                copied += 1

    # drapeaux: tout conserver
    for sub in sorted(os.listdir(os.path.join(ROOT, "drapeaux"))):
        sdir = os.path.join(ROOT, "drapeaux", sub)
        if not os.path.isdir(sdir):
            continue
        for name in sorted(os.listdir(sdir)):
            if not name.endswith(".md") or not ID_RE.match(name):
                continue
            dst_dir = os.path.join(DEST, "drapeaux", sub)
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy2(os.path.join(sdir, name), os.path.join(dst_dir, name))
            copied += 1

    print(f"{copied} cartes copiees dans {os.path.relpath(DEST, ROOT)}")


if __name__ == "__main__":
    main()
