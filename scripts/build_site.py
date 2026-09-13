#!/usr/bin/env python3
"""Genere site/index.html (autonome) a partir de cartes-500/.

Donnees inline (pas de fetch), images referencees dans ../images/cartes-500/.
"""

import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "cartes-500")
DEST = os.path.join(ROOT, "site", "index.html")
ID_RE = re.compile(r"^(\d+-\d+-\d+)_")

THEMES = [
    ("drapeaux", "Drapeaux"),
    ("capitales-chefs-lieux", "Capitales & chefs-lieux"),
    ("montagnes", "Montagnes"),
    ("lacs-mers-oceans-rivieres", "Lacs, mers, océans & rivières"),
    ("monuments", "Monuments"),
    ("merveilles-et-espace", "Merveilles & espace"),
    ("animaux", "Animaux"),
]
SUBS = {
    "suisse": "Suisse", "europe": "Europe", "monde": "Monde",
    "lacs": "Lacs", "mers-et-oceans": "Mers & océans",
    "fleuves-et-rivieres": "Fleuves & rivières", "espace": "Espace",
}


def section(lines, header):
    try:
        i = lines.index(header)
    except ValueError:
        return ""
    out = []
    for ln in lines[i + 1:]:
        if ln.startswith("# "):
            break
        if ln:
            out.append(ln)
    return " ".join(out)


def parse_card(path):
    lines = [ln.strip() for ln in open(path, encoding="utf-8")]
    return section(lines, "# Titre"), section(lines, "# Description")


def collect():
    cards, theme_meta = [], []
    for tkey, tlabel in THEMES:
        tdir = os.path.join(SRC, tkey)
        subs = []
        for skey in sorted(os.listdir(tdir)):
            sdir = os.path.join(tdir, skey)
            if not os.path.isdir(sdir):
                continue
            subs.append({"key": skey, "label": SUBS.get(skey, skey)})
            for name in sorted(os.listdir(sdir)):
                m = ID_RE.match(name)
                if not m or not name.endswith(".md"):
                    continue
                title, desc = parse_card(os.path.join(sdir, name))
                cards.append({"id": m.group(1), "t": tkey, "s": skey,
                              "title": title, "desc": desc})
        theme_meta.append({"key": tkey, "label": tlabel, "subs": subs})
    return cards, theme_meta


TEMPLATE = """<!DOCTYPE html>
<html lang="fr" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cartes &mdash; culture generale</title>
<style>
:root{--bg:#f4f4f6;--fg:#1d1d1f;--muted:#6e6e73;--card:#fff;--line:#e4e4e7;
--accent:#0a84ff;--accent-fg:#fff;--shadow:0 1px 3px rgba(0,0,0,.08);--frame:#ececf0}
html[data-theme="dark"]{--bg:#111114;--fg:#f2f2f4;--muted:#98989f;--card:#1b1b1f;--line:#2b2b31;
--accent:#0a84ff;--accent-fg:#fff;--shadow:0 1px 3px rgba(0,0,0,.5);--frame:#242429}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--fg);
font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{position:sticky;top:0;z-index:20;background:var(--bg);border-bottom:1px solid var(--line);
padding:10px 14px 0;backdrop-filter:saturate(1.4) blur(8px)}
.top{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding-bottom:10px}
.brand{font-weight:700;font-size:16px;white-space:nowrap}
.count{color:var(--muted);font-size:13px;margin-left:auto}
input[type=search]{flex:1 1 220px;min-width:160px;max-width:420px;padding:8px 12px;border-radius:10px;
border:1px solid var(--line);background:var(--card);color:var(--fg);font-size:15px;outline:none}
input[type=search]:focus{border-color:var(--accent)}
button.theme{cursor:pointer;border:1px solid var(--line);background:var(--card);color:var(--fg);
border-radius:10px;padding:7px 11px;font-size:14px;line-height:1}
nav{display:flex;gap:6px;overflow-x:auto;padding-bottom:8px;scrollbar-width:none}
nav::-webkit-scrollbar{display:none}
.tab{cursor:pointer;white-space:nowrap;border:1px solid var(--line);background:var(--card);color:var(--fg);
border-radius:999px;padding:6px 13px;font-size:14px}
.tab.active{background:var(--accent);color:var(--accent-fg);border-color:var(--accent)}
.subtabs{display:flex;gap:6px;overflow-x:auto;padding:0 0 10px;scrollbar-width:none}
.subtabs::-webkit-scrollbar{display:none}
.sub{cursor:pointer;white-space:nowrap;border:none;background:transparent;color:var(--muted);
border-radius:8px;padding:4px 9px;font-size:13px}
.sub.active{background:var(--frame);color:var(--fg);font-weight:600}
main{padding:16px 14px 60px}
.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(210px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;
box-shadow:var(--shadow);display:flex;flex-direction:column;content-visibility:auto;
contain-intrinsic-size:280px}
.frame{aspect-ratio:4/3;background:var(--frame);overflow:hidden;padding:8px}
.frame img{width:100%;height:100%;object-fit:contain;display:block;border-radius:6px}
.card h3{margin:11px 13px 4px;font-size:15px;line-height:1.3}
.card p{margin:0 13px 13px;color:var(--muted);font-size:13px}
.empty{color:var(--muted);text-align:center;padding:60px 0}
</style>
</head>
<body>
<header>
  <div class="top">
    <span class="brand">Cartes de culture generale</span>
    <input type="search" id="q" placeholder="Rechercher un titre..." autocomplete="off">
    <button class="theme" id="toggle" aria-label="Changer de theme">Sombre</button>
    <span class="count" id="count"></span>
  </div>
  <nav id="tabs"></nav>
  <div class="subtabs" id="subtabs"></div>
</header>
<main><div class="grid" id="grid"></div><div class="empty" id="empty" hidden>Aucun resultat.</div></main>
<script>
const DATA = /*__DATA__*/;
const THEMES = /*__THEMES__*/;
const IMG = "../images/cartes-500/";
const ALL = {key:"all",label:"Tout"};

const norm = s => (s||"").normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").toLowerCase();
let theme = "all", sub = "all", q = "";

const $ = id => document.getElementById(id);

function themeTabs(){
  const items = [ALL].concat(THEMES);
  $("tabs").innerHTML = items.map(t =>
    `<button class="tab${t.key===theme?" active":""}" data-t="${t.key}">${t.label}</button>`).join("");
}
function subTabs(){
  const el = $("subtabs");
  if(theme==="all"){ el.hidden = true; el.innerHTML=""; return; }
  el.hidden = false;
  const subs = (THEMES.find(t=>t.key===theme)||{subs:[]}).subs;
  const items = [ALL].concat(subs);
  el.innerHTML = items.map(s =>
    `<button class="sub${s.key===sub?" active":""}" data-s="${s.key}">${s.label}</button>`).join("");
}
function render(){
  const nq = norm(q);
  const list = DATA.filter(c =>
    (theme==="all" || c.t===theme) &&
    (theme==="all" || sub==="all" || c.s===sub) &&
    (!nq || norm(c.title).includes(nq)));
  $("count").textContent = list.length + (list.length>1?" cartes":" carte");
  $("grid").innerHTML = list.map(c => {
    const t = c.title.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
    const d = c.desc.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
    return `<article class="card"><div class="frame"><img loading="lazy" decoding="async" `
      + `src="${IMG}${c.id}.webp" alt="${t}"></div><h3>${t}</h3><p>${d}</p></article>`;
  }).join("");
  $("empty").hidden = list.length>0;
}
function setTheme(next){
  document.documentElement.dataset.theme = next;
  $("toggle").textContent = next==="dark" ? "Clair" : "Sombre";
  try{ localStorage.setItem("theme", next); }catch(e){}
}
$("tabs").addEventListener("click", e => {
  const b = e.target.closest("[data-t]"); if(!b) return;
  theme = b.dataset.t; sub = "all"; themeTabs(); subTabs(); render();
});
$("subtabs").addEventListener("click", e => {
  const b = e.target.closest("[data-s]"); if(!b) return;
  sub = b.dataset.s; subTabs(); render();
});
let timer;
$("q").addEventListener("input", e => {
  clearTimeout(timer);
  timer = setTimeout(() => { q = e.target.value.trim(); render(); }, 60);
});
$("toggle").addEventListener("click", () =>
  setTheme(document.documentElement.dataset.theme==="dark" ? "light" : "dark"));
let saved = null;
try{ saved = localStorage.getItem("theme"); }catch(e){}
setTheme(saved || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
themeTabs(); subTabs(); render();
</script>
</body>
</html>
"""


def main():
    cards, themes = collect()
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    out = (TEMPLATE
           .replace("/*__DATA__*/", json.dumps(cards, ensure_ascii=False, separators=(",", ":")))
           .replace("/*__THEMES__*/", json.dumps(themes, ensure_ascii=False, separators=(",", ":"))))
    with open(DEST, "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"{len(cards)} cartes -> {os.path.relpath(DEST, ROOT)} ({len(out)//1024} Ko)")


if __name__ == "__main__":
    main()
