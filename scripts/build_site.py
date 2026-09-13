#!/usr/bin/env python3
"""Genere site/index.html (autonome) a partir de cartes-500/.

Donnees inline (pas de fetch), images referencees dans ../images/cartes-500/.
"""

import argparse
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "cartes-500")
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
dialog#lb{border:0;padding:0;background:transparent;width:min(1100px,92vw);max-width:100vw;max-height:100vh}
dialog#lb::backdrop{background:rgba(0,0,0,.62);backdrop-filter:blur(4px)}
dialog#lb[open]{animation:lbpop .18s ease}
@keyframes lbpop{from{opacity:0;transform:scale(.96)}}
.lbBox{position:relative;width:100%;display:flex;flex-direction:column;color:var(--fg);background:var(--card);
border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:0 12px 40px rgba(0,0,0,.45);max-height:94vh}
.lbImgWrap{position:relative;background:var(--frame);display:flex;align-items:center;justify-content:center;padding:14px;min-height:0}
.lbId{position:absolute;right:14px;bottom:14px;max-width:80%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
font-size:11px;color:#fff;background:rgba(0,0,0,.5);border-radius:999px;padding:3px 9px}
.lbImgWrap img{max-width:100%;max-height:70vh;width:auto;height:auto;object-fit:contain;display:block;border-radius:8px}
.lbCap{padding:12px 16px 16px}
.lbCap h3{margin:0 0 4px;font-size:17px}
.lbCap p{margin:0;color:var(--muted);font-size:14px}
.lbCount{position:absolute;top:11px;left:14px;z-index:2;font-size:12px;color:#fff;background:rgba(0,0,0,.5);border-radius:999px;padding:3px 9px}
.lbClose{position:absolute;top:9px;right:10px;z-index:2;border:0;cursor:pointer;background:rgba(0,0,0,.5);color:#fff;
width:32px;height:32px;border-radius:999px;font-size:20px;line-height:1}
.lbNav{position:absolute;top:50%;transform:translateY(-50%);z-index:2;border:0;cursor:pointer;background:rgba(0,0,0,.45);
color:#fff;width:42px;height:42px;border-radius:999px;font-size:24px;line-height:1}
.lbPrev{left:8px}.lbNext{right:8px}
.lbClose:hover,.lbNav:hover{background:rgba(0,0,0,.72)}
html.lb-on{overflow:hidden}
@media (prefers-reduced-motion:reduce){dialog#lb[open]{animation:none}}
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
<dialog id="lb" aria-label="Carte agrandie">
  <div class="lbBox">
    <span class="lbCount" id="lbCount"></span>
    <button class="lbClose" id="lbClose" aria-label="Fermer">&times;</button>
    <button class="lbNav lbPrev" id="lbPrev" aria-label="Carte precedente">&#8249;</button>
    <button class="lbNav lbNext" id="lbNext" aria-label="Carte suivante">&#8250;</button>
    <div class="lbImgWrap"><img id="lbImg" alt=""><span class="lbId" id="lbId"></span></div>
    <div class="lbCap"><h3 id="lbTitle"></h3><p id="lbDesc"></p></div>
  </div>
</dialog>
<script>
const DATA = /*__DATA__*/;
const THEMES = /*__THEMES__*/;
const IMG = /*__IMG__*/;
const ALL = {key:"all",label:"Tout"};
const TLABEL = {}, SLABEL = {};
THEMES.forEach(t => { TLABEL[t.key] = t.label; t.subs.forEach(s => SLABEL[t.key+"|"+s.key] = s.label); });

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
let visible = [], idx = 0;
function render(){
  const nq = norm(q);
  const list = DATA.filter(c =>
    (theme==="all" || c.t===theme) &&
    (theme==="all" || sub==="all" || c.s===sub) &&
    (!nq || norm(c.title).includes(nq)));
  visible = list;
  if(lb.open) lb.close();
  $("count").textContent = list.length + (list.length>1?" cartes":" carte");
  $("grid").innerHTML = list.map((c,i) => {
    const t = c.title.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
    const d = c.desc.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
    return `<article class="card" data-i="${i}"><div class="frame"><img loading="lazy" decoding="async" `
      + `src="${IMG}${c.id}.webp" alt="${t}"></div><h3>${t}</h3><p>${d}</p></article>`;
  }).join("");
  $("empty").hidden = list.length>0;
}

const lb=$("lb"), lbImg=$("lbImg"), lbTitle=$("lbTitle"), lbDesc=$("lbDesc"), lbCount=$("lbCount"), lbId=$("lbId");
function preload(){
  [1,-1].forEach(d => { const c = visible[(idx+d+visible.length)%visible.length];
    if(c) new Image().src = IMG+c.id+".webp"; });
}
function openLb(i){
  if(!visible.length) return;
  idx = (i + visible.length) % visible.length;
  const c = visible[idx];
  lbImg.src = IMG+c.id+".webp"; lbImg.alt = c.title;
  lbTitle.textContent = c.title; lbDesc.textContent = c.desc;
  lbCount.textContent = (idx+1)+" / "+visible.length;
  lbId.textContent = TLABEL[c.t] + " \\u00b7 " + (SLABEL[c.t+"|"+c.s]||c.s) + " \\u00b7 " + c.id;
  if(!lb.open) lb.showModal();
  document.documentElement.classList.add("lb-on");
  preload();
}
$("grid").addEventListener("click", e => {
  const card = e.target.closest(".card"); if(!card) return;
  openLb(+card.dataset.i);
});
lb.addEventListener("click", e => { if(e.target===lb) lb.close(); });
lb.addEventListener("close", () => document.documentElement.classList.remove("lb-on"));
lb.addEventListener("keydown", e => {
  if(e.key==="ArrowLeft"){ e.preventDefault(); openLb(idx-1); }
  else if(e.key==="ArrowRight"){ e.preventDefault(); openLb(idx+1); }
});
$("lbPrev").onclick = () => openLb(idx-1);
$("lbNext").onclick = () => openLb(idx+1);
$("lbClose").onclick = () => lb.close();
let sx=null;
lb.addEventListener("pointerdown", e => { sx=e.clientX; });
lb.addEventListener("pointerup", e => {
  if(sx==null) return; const dx=e.clientX-sx; sx=null;
  if(Math.abs(dx)>40) openLb(idx + (dx<0?1:-1));
});
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
    parser = argparse.ArgumentParser(description="Genere le site a partir de cartes-500/.")
    parser.add_argument("--out", default="site/index.html",
                        help="fichier HTML de sortie (relatif a la racine)")
    parser.add_argument("--img", default="../images/cartes-500/",
                        help="base du chemin des images vue depuis le HTML")
    args = parser.parse_args()

    cards, themes = collect()
    dest = os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    out = (TEMPLATE
           .replace("/*__DATA__*/", json.dumps(cards, ensure_ascii=False, separators=(",", ":")))
           .replace("/*__THEMES__*/", json.dumps(themes, ensure_ascii=False, separators=(",", ":")))
           .replace("/*__IMG__*/", json.dumps(args.img)))
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"{len(cards)} cartes -> {os.path.relpath(dest, ROOT)} ({len(out)//1024} Ko)")


if __name__ == "__main__":
    main()
