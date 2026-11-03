# Builds the tree-by-tree series: HTML cards for every post, plus posts.json with the caption,
# alt text, sources, and notes that go into each post's "Post wording" document.
# Usage: python3 build_trees.py <out_dir>        (photos from series/img, or $SERIES_IMG)
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from source import FIELD_GUIDE, COMMITMENTS, timeline
from trees import TREES, INTRO, CLOSING, ERA_ASK, FRESH

for _t in TREES.values():  # connected trees read in time order on the card and in the caption
    _t["links"] = sorted(_t["links"])

OUT = os.path.abspath(sys.argv[1])
HTML_DIR = os.path.join(OUT, "html")
os.makedirs(HTML_DIR, exist_ok=True)
IMG = os.environ.get("SERIES_IMG", os.path.abspath(os.path.join(HERE, "..", "img")))
FONTS = os.path.join(HERE, "fonts")

TL = timeline()
E = TL["E"]
ERAS = TL["ERAS"]
LANES = TL["LANES"]
N = len(E)
ERA_N = {e["id"]: i + 1 for i, e in enumerate(ERAS)}
ERA = {e["id"]: e for e in ERAS}
TIMELINE_URL = "https://claude.ai/artifact/U8XhxLs1m2Xs8o4ydrXA8k"

# Content notes for entries that need one (every cutting, killing, and dark entry gets one).
CN = {
    11: "forced sterilization", 19: "forced sterilization", 22: "forced sterilization",
    23: "forced sterilization and rape", 26: "forced sterilization", 28: "forced sterilization in Nazi Germany",
    29: "Nazi Germany and the killing of disabled children", 30: "the killing of disabled children",
    31: "the killing of disabled people", 32: "the killing of disabled people", 33: "the killing of disabled children",
    34: "the killing of disabled people", 36: "Nazi Germany and the killing of disabled children",
    37: "electroshock used on children", 39: "drug experiments on children", 44: "electric shock used on a child",
    46: "drug experiments on young children", 49: "rape and forced sterilization", 52: "forced sterilization",
    54: "forced sterilization", 65: "restraint and electric shock", 70: "forced sterilization",
    76: "forced sterilization", 83: "electric shock devices",
}


def esc(s):
    return html.escape(s, quote=False)


def smart(s):
    """Curly quotes and apostrophes for display."""
    s = re.sub(r'(^|[\s(\[—–-])"', r"\1“", s)
    s = s.replace('"', "”")
    s = re.sub(r"(^|[\s(\[—–-])'", r"\1‘", s)
    return s.replace("'", "’")


def quote_display(q):
    """Wrap a report quote for display: inner quotes become single quotes, fragments get ellipses."""
    s = q.strip()
    s = re.sub(r'"([^"]*)"', r"‘\1’", s)
    s = smart(s)
    if s[0].islower():
        s = "…" + s
    if not re.search(r"[.!?’”]$", s):
        s = s + "…"
    return "“" + s + "”"


def plain_title(t):
    return re.sub(r"[“”\"]", "", t)


def folder_safe(s):
    s = plain_title(s).replace("’", "'")
    s = re.sub(r'[<>:"/\\|?*]', "", s)
    return re.sub(r"\s+", " ", s).strip().rstrip(".")


MONTHS = dict(Jan="January", Feb="February", Mar="March", Apr="April", May="May", Jun="June", Jul="July",
              Aug="August", Sep="September", Oct="October", Nov="November", Dec="December")


def date_label(e):
    """Dates the way a caption reads them: "April 17, 1857", "October 1938", "By 1944"."""
    sub = e.get("sub", "")
    if sub == "by":
        return "By " + e["y"]
    if not sub:
        return e["y"]
    mon, _, day = sub.partition(" ")
    mon = MONTHS.get(mon[:3], mon)
    return f"{mon} {day}, {e['y']}" if day else f"{mon} {e['y']}"


def sentences(s):
    return re.split(r"(?<=[.!?])\s+(?=[A-Z“\"])", s)


def is_dark(n):
    return bool(E[n - 1].get("dark"))


def work_on(n, t):
    e = E[n - 1]
    default = e["lane"] in ("measure", "remove", "speak", "frame") and not e.get("dark") and e["era"] != "killing"
    return bool(t.get("term")) and t.get("work", default) and default


def strip_refs(s):
    return re.sub(r"\s*\((?:[IVX]+(?:,\s*|\s+to\s+)?)+\)\s*$", "", s).strip()


def name_it(n, t):
    """The 'Name it' box: a field-guide term or a closing commitment, in the report's own words."""
    if t.get("term"):
        fg = FIELD_GUIDE[t["term"]]
        box = dict(kind="term", label="Name it", name=fg["term"], text=fg["short"] + ".", origin=fg["origin"])
        if work_on(n, t):
            box["work"] = fg["work"]
        if t.get("hist"):
            box["hist"] = strip_refs(fg["hist"])
        if t.get("turn"):
            box["turn"] = t["turn"]
        return box
    if t.get("commit"):
        c = COMMITMENTS[t["commit"]]
        ss = sentences(c["text"])
        pick = t.get("cs", [0, 1])
        return dict(kind="commit", label="What the history asks", name=c["name"],
                    text=" ".join(ss[i] for i in pick if i < len(ss)))
    return None


def tags(n):
    e = E[n - 1]
    t = TREES[n]
    txt = (e["t"] + " " + e["d"]).lower()
    out = ["#OnTheBusOrOffTheBus", "#DisabilityHistory"]
    if re.search(r"autis|asperger|kanner|sukhareva|neurodivers", txt):
        out.append("#Autism")
    if re.search(r"neurodivers|autistic people|autistic adults|autistic scholars|double empathy", txt):
        out.append("#Neurodiversity")
    if e["era"] == "killing":
        out.append("#HolocaustRemembrance")
    elif e["lane"] == "cut" or (e["era"] in ("ledger", "measure") and e["lane"] in ("measure", "remove") and int(e["y"][-4:]) >= 1883):
        out.append("#Eugenics")
    if e["lane"] == "speak" and e["era"] != "killing":
        out.append("#DisabilityRights")
    if work_on(n, t):
        out.append("#WorkplaceBullying")
    return out[:7]


def link_line(m):
    e = E[m - 1]
    return f"{e['y']}: {e['t']} (Tree {m})"


# ---------------------------------------------------------------- styles
FONT_CSS = open(os.path.join(FONTS, "fonts.css")).read().replace("url(t", f"url(file://{FONTS}/t")
CSS = FONT_CSS + """
:root{--paper:#e8eee6;--paper2:#dfe7dc;--ink:#1c2824;--soft:#4a5a54;--acc:#b23a35;--line:#b9c9d6;--gold:#9a7424;--card:#f4f7f1;
--measure:#2f5f8a;--remove:#7a5a1c;--cut:#a33a2c;--kill:#3b3b3b;--speak:#2f7a55;--frame:#7a3f8a}
.dk{--paper:#141617;--paper2:#1b1e1f;--ink:#e6e1d4;--soft:#a39d8f;--acc:#c9a54a;--line:#2c3233;--gold:#d9b65c;--card:#1d2122;
--measure:#7fb0dc;--remove:#d6ac5e;--cut:#e3826f;--kill:#b8b8b8;--speak:#79c99c;--frame:#c99ad8}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#888}
@page{size:1080px 1350px;margin:0}
.slide{--s:1;width:1080px;height:1350px;position:relative;overflow:hidden;background:var(--paper);color:var(--ink);
  font-family:Literata,serif;page-break-after:always;break-after:page}
.ledger{background:repeating-linear-gradient(180deg,transparent 0 53px,rgba(150,172,190,.32) 53px 55px),var(--paper)}
.ledger:before{content:"";position:absolute;top:0;bottom:0;left:118px;width:2px;background:var(--acc);opacity:.45}
.dk.ledger{background:var(--paper)}
.dk.ledger:before{opacity:.35}
.under{background:var(--paper2)}
.top{position:absolute;top:58px;left:84px;right:84px;display:flex;justify-content:space-between;align-items:center;gap:28px;white-space:nowrap;
  font:700 calc(var(--s)*0px + 21px)/1 'Courier Prime',monospace;letter-spacing:.16em;text-transform:uppercase;color:var(--soft);z-index:3}
.ledger .top,.ledger .foot,.ledger .pad{left:150px}
.top .acc{color:var(--acc)}
.top span:last-child{overflow:hidden;text-overflow:ellipsis}
.foot{position:absolute;bottom:52px;left:84px;right:84px;display:flex;justify-content:space-between;align-items:center;white-space:nowrap;gap:24px;
  font:700 20px/1 'Courier Prime',monospace;letter-spacing:.16em;text-transform:uppercase;color:var(--soft);z-index:3}
.foot .go{color:var(--acc)}
.pad{position:absolute;top:128px;bottom:120px;left:84px;right:84px;display:flex;flex-direction:column;justify-content:center}
.tag{align-self:flex-start;display:inline-flex;align-items:center;gap:12px;border:2px solid var(--lane);color:var(--lane);border-radius:40px;
  padding:9px 20px 8px;font:700 calc(var(--s)*22px)/1 'Courier Prime',monospace;letter-spacing:.12em;text-transform:uppercase;margin-bottom:calc(var(--s)*26px)}
.tag:before{content:"";width:14px;height:14px;border-radius:50%;background:var(--lane)}
.cn{align-self:stretch;border:2px solid var(--acc);color:var(--acc);border-radius:10px;padding:16px 22px;margin-bottom:calc(var(--s)*34px);
  font:700 calc(var(--s)*22px)/1.35 'Courier Prime',monospace;letter-spacing:.06em}
.yr{font:400 calc(var(--s)*168px)/.92 'IM Fell English',serif;color:var(--ink);display:flex;align-items:baseline;gap:22px}
.yr .sub{font:700 calc(var(--s)*34px)/1 'Courier Prime',monospace;color:var(--acc);letter-spacing:.06em}
h2.t{font:400 calc(var(--s)*68px)/1.06 'IM Fell English',serif;margin:calc(var(--s)*20px) 0 calc(var(--s)*24px)}
.streak{width:130px;height:6px;background:var(--acc);border-radius:3px;margin-bottom:calc(var(--s)*30px);flex:none}
p.d{font-size:calc(var(--s)*35px);line-height:1.5;color:var(--ink)}
p.scene{font:italic 400 calc(var(--s)*25px)/1.4 Literata,serif;color:var(--soft);margin-top:calc(var(--s)*26px);padding-top:calc(var(--s)*18px);border-top:2px solid rgba(74,90,84,.25)}
p.scene b{font:700 calc(var(--s)*19px)/1 'Courier Prime',monospace;letter-spacing:.12em;text-transform:uppercase;font-style:normal;color:var(--acc);display:block;margin-bottom:8px}
/* photo cards */
.ph{position:absolute;top:0;left:0;right:0;height:560px;overflow:hidden;border-bottom:6px solid var(--acc)}
.ph img{width:100%;height:100%;object-fit:cover;object-position:center 10%;display:block}
.ph:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,16,14,.72) 0,rgba(10,16,14,.35) 9%,rgba(10,16,14,0) 20%)}
.photo .yr{font-size:calc(var(--s)*112px);margin-bottom:calc(var(--s)*2px)}
.photo .tagrow{display:flex;align-items:center;justify-content:space-between;margin-bottom:calc(var(--s)*14px)}
.photo .tagrow .tag{margin-bottom:0}
.foot .acc{color:var(--acc)}
.photo .pad{top:596px;justify-content:flex-start}
.photo .tag{margin-bottom:calc(var(--s)*12px)}
.photo h2.t{margin-top:calc(var(--s)*6px)}
/* under the surface */
.q{border-left:8px solid var(--acc);padding:4px 0 4px 34px;margin-bottom:calc(var(--s)*36px)}
.q p{font:italic 400 calc(var(--s)*38px)/1.42 Literata,serif}
.q .who{font:700 calc(var(--s)*20px)/1.3 'Courier Prime',monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--soft);margin-top:calc(var(--s)*16px)}
.box{background:var(--card);border:2px solid rgba(28,40,36,.12);border-radius:20px;padding:calc(var(--s)*36px) calc(var(--s)*42px);position:relative}
.dk .box{border-color:rgba(230,225,212,.14)}
.box .lab,.roots .lab{font:700 calc(var(--s)*21px)/1 'Courier Prime',monospace;letter-spacing:.16em;text-transform:uppercase;color:var(--acc);margin-bottom:calc(var(--s)*14px)}
.box h3{font:400 calc(var(--s)*56px)/1.05 'IM Fell English',serif;margin-bottom:calc(var(--s)*12px)}
.box p.def{font-size:calc(var(--s)*31px);line-height:1.42}
.box p.work{font:400 calc(var(--s)*27px)/1.45 'Courier Prime',monospace;margin-top:calc(var(--s)*18px);padding-top:calc(var(--s)*16px);border-top:2px dashed rgba(74,90,84,.3)}
.box p.work b{color:var(--acc)}
.box p.turn{font:italic 400 calc(var(--s)*28px)/1.4 Literata,serif;color:var(--speak);margin-top:calc(var(--s)*14px)}
.roots{margin-top:calc(var(--s)*40px);position:relative;padding-left:34px}
.roots:before{content:"";position:absolute;left:8px;top:calc(var(--s)*-40px);bottom:24px;width:3px;background:var(--soft);opacity:.35;border-radius:2px}
.roots ul{list-style:none}
.roots li{position:relative;font-size:calc(var(--s)*28px);line-height:1.3;margin-top:calc(var(--s)*16px)}
.roots li:before{content:"";position:absolute;left:-26px;top:.62em;width:20px;height:3px;background:var(--soft);opacity:.35}
.roots li i{font-style:normal;display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--c);margin-right:12px;vertical-align:.08em}
.roots li b{font:700 calc(var(--s)*26px)/1 'Courier Prime',monospace;margin-right:12px}
.roots li span{font:700 calc(var(--s)*19px)/1 'Courier Prime',monospace;color:var(--soft);letter-spacing:.1em;margin-left:10px;white-space:nowrap}
/* era maps */
.era h2{font:400 calc(var(--s)*86px)/1.02 'IM Fell English',serif;margin:calc(var(--s)*10px) 0 calc(var(--s)*22px)}
.era.cover h2{font-size:calc(var(--s)*104px)}
.era p.count{font:700 calc(var(--s)*24px)/1 'Courier Prime',monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--acc)}
.era h3.lt{font:400 calc(var(--s)*52px)/1.05 'IM Fell English',serif;margin-bottom:calc(var(--s)*22px)}
.era.list li{font-size:calc(var(--s)*30px)}
.era .span{font:700 calc(var(--s)*30px)/1 'Courier Prime',monospace;color:var(--acc);letter-spacing:.1em}
.era p.lede{font-size:calc(var(--s)*31px);line-height:1.45;margin-bottom:calc(var(--s)*30px)}
.era ol{list-style:none;border-top:2px solid rgba(74,90,84,.3)}
.era li{display:flex;align-items:baseline;gap:16px;padding:calc(var(--s)*10px) 0;border-bottom:1px solid rgba(74,90,84,.2);font-size:calc(var(--s)*27px);line-height:1.25}
.era li i{flex:none;width:13px;height:13px;border-radius:50%;background:var(--c);align-self:center}
.era li b{flex:none;width:calc(var(--s)*128px);font:700 calc(var(--s)*25px)/1 'Courier Prime',monospace}
.era li span{flex:1}
.era li small{flex:none;font:700 calc(var(--s)*18px)/1 'Courier Prime',monospace;color:var(--soft);letter-spacing:.1em}
.legend{display:flex;flex-wrap:wrap;gap:10px 26px;margin-top:calc(var(--s)*24px);font:700 calc(var(--s)*19px)/1 'Courier Prime',monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--soft)}
.legend i{display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--c);margin-right:8px}
/* intro and closing */
h1.big{font:400 calc(var(--s)*104px)/.98 'IM Fell English',serif;margin:calc(var(--s)*4px) 0 calc(var(--s)*18px)}
h1.big em,h2.t em{color:var(--acc)}
.kick{font:700 calc(var(--s)*24px)/1 'Courier Prime',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--acc)}
p.body{font-size:calc(var(--s)*32px);line-height:1.5;margin-top:calc(var(--s)*18px)}
p.note{font:400 calc(var(--s)*24px)/1.45 'Courier Prime',monospace;color:var(--soft);margin-top:calc(var(--s)*26px);border-top:2px solid rgba(74,90,84,.25);padding-top:calc(var(--s)*18px)}
.lanes{display:grid;grid-template-columns:1fr 1fr;gap:calc(var(--s)*16px) 30px;margin:calc(var(--s)*26px) 0}
.lanes div{font:400 calc(var(--s)*30px)/1.2 Literata,serif;display:flex;align-items:center;gap:14px}
.lanes i{width:20px;height:20px;border-radius:50%;background:var(--c);flex:none}
.steps p{font-size:calc(var(--s)*31px);line-height:1.45;margin-top:calc(var(--s)*18px)}
.steps p b{font:700 calc(var(--s)*24px)/1 'Courier Prime',monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--acc);margin-right:10px}
.commits li{list-style:none;margin-top:calc(var(--s)*20px)}
.commits h3{font:400 calc(var(--s)*54px)/1.1 'IM Fell English',serif}
.commits p{font-size:calc(var(--s)*29px);line-height:1.42;color:var(--soft)}
.commits li{margin-top:calc(var(--s)*26px)}
"""

FIT_JS = """
<script>
document.fonts.ready.then(()=>{
  document.querySelectorAll('.slide').forEach(sl=>{
    const pad=sl.querySelector('.pad'); if(!pad) return;
    let s=+(sl.dataset.max||1);
    sl.style.setProperty('--s',s.toFixed(2));
    const over=()=>pad.scrollHeight>pad.clientHeight+1;
    while(over() && s>0.66){ s-=0.02; sl.style.setProperty('--s',s.toFixed(2)); }
    sl.dataset.scale=s.toFixed(2);
  });
  document.body.dataset.ready='1';
});
</script>"""


def page(slides, title):
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)}</title>"
            f"<style>{CSS}</style></head><body>{''.join(slides)}{FIT_JS}</body></html>")


def lane_var(lane):
    return f"--lane:var(--{lane})"


def img_src(name):
    return f"file://{IMG}/{name}.jpg"


# ---------------------------------------------------------------- slides
def tree_slide1(n):
    e, t = E[n - 1], TREES[n]
    era = ERA[e["era"]]
    dark = is_dark(n)
    sc = e.get("scene")
    cls = "slide " + ("photo" if sc else "ledger") + (" dk" if dark else "") + f"' data-max='{1.1 if sc else 1.3}"
    top = (f"<div class='top'><span class='acc'>Tree {n} of {N}</span>"
           f"<span>{esc(era['span'])} · {esc(era['t'])}</span></div>")
    if e.get("sub") == "by":
        yr = f"<div class='yr'><span class='sub'>By</span>{esc(e['y'])}</div>"
    else:
        yr = f"<div class='yr'>{esc(e['y'])}" + (f"<span class='sub'>{esc(e['sub'])}</span>" if e.get("sub") else "") + "</div>"
    tag = f"<div class='tag' style='{lane_var(e['lane'])}'>{esc(LANES[e['lane']]['name'])}</div>"
    cn = f"<div class='cn'>Content note: {esc(CN[n])}.</div>" if n in CN else ""
    title = f"<h2 class='t'>{esc(e['t'])}</h2>"
    d = f"<p class='d'>{esc(e['d'])}</p>"
    foot = "<div class='foot'><span>On the Bus or Off the Bus</span><span class='go'>Swipe: under the surface →</span></div>"
    if sc:
        ph = f"<div class='ph'><img src='{img_src(sc['img'])}' alt=''></div>"
        lab = sc["lab"].replace("Scene · ", "")
        scene = f"<p class='scene'><b>Scene · {esc(lab)}</b>{esc(sc['cap'])}</p>"
        body = f"<div class='pad'>{cn}<div class='tagrow'>{yr}{tag}</div>{title}{d}{scene}</div>"
        foot = (f"<div class='foot'><span class='acc'>Tree {n} of {N}</span>"
                "<span class='go'>Swipe: under the surface →</span></div>")
        return f"<section class='{cls}'>{ph}{body}{foot}</section>"
    body = f"<div class='pad'>{cn}{tag}{yr}{title}<div class='streak'></div>{d}</div>"
    return f"<section class='{cls}'>{top}{body}{foot}</section>"


def box_html(box):
    if not box:
        return ""
    h = f"<div class='box'><div class='lab'>{esc(box['label'])}</div><h3>{esc(box['name'])}</h3><p class='def'>{esc(smart(box['text']))}</p>"
    if box.get("work"):
        h += f"<p class='work'><b>At work:</b> {esc(smart(box['work']))}</p>"
    if box.get("hist"):
        h += f"<p class='work'><b>In this history:</b> {esc(smart(box['hist']))}</p>"
    if box.get("turn"):
        h += f"<p class='turn'>{esc(box['turn'])}</p>"
    return h + "</div>"


def roots_html(links):
    lis = ""
    for m in links:
        e = E[m - 1]
        lis += (f"<li style='--c:var(--{e['lane']})'><i></i><b>{esc(e['y'])}</b>{esc(e['t'])}"
                f"<span>TREE {m}</span></li>")
    return f"<div class='roots'><div class='lab'>Connected trees</div><ul>{lis}</ul></div>"


def tree_slide2(n):
    e, t = E[n - 1], TREES[n]
    dark = is_dark(n)
    q = ""
    if t.get("q"):
        q = (f"<div class='q'><p>{esc(quote_display(t['q'][0]))}</p>"
             f"<div class='who'>John Charles Davis · from the report</div></div>")
    box = box_html(name_it(n, t))
    top = f"<div class='top'><span class='acc'>Under the surface</span><span>Tree {n} of {N} · {esc(e['y'])}</span></div>"
    foot = "<div class='foot'><span>On the Bus or Off the Bus</span><span>Full timeline: link in bio</span></div>"
    return (f"<section class='slide under{' dk' if dark else ''}' data-max='1.2'>{top}<div class='pad'>{q}{box}{roots_html(t['links'])}</div>{foot}</section>")


def era_slides(era):
    i = ERA_N[era["id"]]
    nums = [k + 1 for k, e in enumerate(E) if e["era"] == era["id"]]
    dark = era["id"] == "killing"
    lis = "".join(
        f"<li style='--c:var(--{E[m-1]['lane']})'><i></i><b>{esc(date_label(E[m-1]) if E[m-1].get('sub') == 'by' else E[m-1]['y'])}</b><span>{esc(E[m-1]['t'])}</span><small>TREE {m}</small></li>"
        for m in nums)
    lanes = []
    for m in nums:
        if E[m - 1]["lane"] not in lanes:
            lanes.append(E[m - 1]["lane"])
    legend = "".join(f"<span style='--c:var(--{l})'><i></i>{esc(LANES[l]['name'])}</span>" for l in lanes)
    dk = " dk" if dark else ""
    top = f"<div class='top'><span class='acc'>Era {i} of {len(ERAS)}</span><span>Trees {nums[0]}–{nums[-1]}</span></div>"
    cn = "<div class='cn'>Content note: forced sterilization and the killing of disabled children and adults.</div>" if dark else ""
    s1 = (f"<section class='slide era cover ledger{dk}' data-max='1.3'>{top}<div class='pad'>{cn}<div class='span'>{esc(era['span'])}</div>"
          f"<h2>{esc(era['t'])}</h2><div class='streak'></div><p class='lede'>{esc(era['p'])}</p>"
          f"<p class='count'>{len(nums)} trees · {nums[0]} to {nums[-1]}</p><div class='legend'>{legend}</div></div>"
          f"<div class='foot'><span>On the Bus or Off the Bus</span><span class='go'>Swipe: the trees in this era →</span></div></section>")
    top2 = f"<div class='top'><span class='acc'>The trees in this era</span><span>{esc(era['span'])}</span></div>"
    s2 = (f"<section class='slide era list ledger{dk}' data-max='1.3'>{top2}<div class='pad'><h3 class='lt'>{esc(era['t'])}</h3><ol>{lis}</ol></div>"
          f"<div class='foot'><span>On the Bus or Off the Bus</span><span>Full timeline: link in bio</span></div></section>")
    return [s1, s2], nums


def intro_slides():
    c = INTRO
    s1 = (f"<section class='slide photo'><div class='ph'><img src='{img_src(c['img'])}' alt=''></div>"
          f"<div class='pad'><div class='kick'>A ledger of 425 years</div><h1 class='big'>On the Bus<br>or <em>Off</em> the Bus</h1>"
          f"<p class='body'>{esc(c['lede'])}</p></div>"
          f"<div class='foot'><span>On the Bus or Off the Bus</span><span class='go'>Swipe: how to read it →</span></div></section>")
    lanes = "".join(f"<div style='--c:var(--{k})'><i></i>{esc(v['name'])}</div>" for k, v in LANES.items())
    s2 = (f"<section class='slide ledger'><div class='top'><span class='acc'>How to read the series</span><span>{N} trees · {len(ERAS)} eras</span></div>"
          f"<div class='pad'><h2 class='t'>One tree at a time, with the forest in view</h2>"
          f"<div class='steps'><p><b>Slide 1</b>The tree: one moment from the timeline, in the order it happened.</p>"
          f"<p><b>Slide 2</b>Under the surface: my own words from the report, the tactic it names, and the trees it connects to.</p></div>"
          f"<div class='lanes'>{lanes}</div>"
          f"<p class='note'>{esc(c['note'])}</p></div>"
          f"<div class='foot'><span>On the Bus or Off the Bus</span><span>Full timeline: link in bio</span></div></section>")
    return [s1, s2]


def closing_slides():
    c = CLOSING
    s1 = (f"<section class='slide photo'><div class='ph'><img src='{img_src(c['img'])}' alt=''></div>"
          f"<div class='pad'><div class='yr'>2026</div><h2 class='t'>Who holds the <em>acid</em>?</h2>"
          + "".join(f"<p class='body'>{esc(p)}</p>" for p in c["paras"]) +
          f"</div><div class='foot'><span>On the Bus or Off the Bus</span><span class='go'>Swipe: what it asks of us →</span></div></section>")
    lis = ""
    for k, v in COMMITMENTS.items():
        lis += f"<li><h3>{esc(v['name'])}</h3><p>{esc(smart(sentences(v['text'])[0]))}</p></li>"
    s2 = (f"<section class='slide under'><div class='top'><span class='acc'>What the history asks</span><span>Six commitments</span></div>"
          f"<div class='pad'><div class='kick'>From the closing of my report</div><ol class='commits'>{lis}</ol></div>"
          f"<div class='foot'><span>On the Bus or Off the Bus</span><span>Full timeline: link in bio</span></div></section>")
    return [s1, s2]


# ---------------------------------------------------------------- captions and documents
def tree_caption(n):
    e, t = E[n - 1], TREES[n]
    box = name_it(n, t)
    parts = []
    if n in CN:
        parts.append(f"Content note: {CN[n]}.")
    parts.append(t["h"])
    parts.append(f"{date_label(e)}. {plain_title(e['t'])}.\n{e['d']}")
    if t.get("q"):
        parts.append("From my report:\n" + "\n".join(quote_display(q) for q in t["q"]))
    if box:
        if box["kind"] == "term":
            s = f"Name it: {box['name']}. {smart(box['text'])}"
            if box.get("work"):
                s += f"\nAt work: {stop(smart(box['work']))}"
            if box.get("hist"):
                s += f"\nIn this history: {stop(smart(box['hist']))}"
            if box.get("turn"):
                s += f"\n{box['turn']}"
        else:
            s = f"What the history asks: {box['name']}. {smart(box['text'])}"
        parts.append(s)
    parts.append("Connected trees:\n" + "\n".join("↳ " + link_line(m) for m in t["links"]))
    if t.get("ask") and not is_dark(n):
        parts.append(t["ask"])
    parts.append(f"Tree {n} of {N} in On the Bus or Off the Bus. The full timeline is linked in my bio.")
    parts.append(" ".join(tags(n)))
    return "\n\n".join(parts)


def stop(s):
    s = s.strip()
    return s if s[-1:] in ".!?’”\"" else s + "."


def tree_alt(n):
    e, t = E[n - 1], TREES[n]
    box = name_it(n, t)
    a1 = (f"Card, tree {n} of {N}. " + (f"Content note: {CN[n]}. " if n in CN else "") +
          f"{date_label(e)}, {LANES[e['lane']]['name']}: {plain_title(e['t'])}. {e['d']}")
    if e.get("scene"):
        a1 += f" Photo: John Charles in the white duck dress: {stop(e['scene']['cap'])}"
    a2 = "Card, under the surface. "
    if t.get("q"):
        a2 += f"Quote from John Charles Davis's report: {quote_display(t['q'][0])} "
    if box:
        a2 += f"{box['label']}: {box['name']}. {stop(smart(box['text']))} "
        if box.get("work"):
            a2 += f"At work: {stop(smart(box['work']))} "
        if box.get("hist"):
            a2 += f"In this history: {stop(smart(box['hist']))} "
        if box.get("turn"):
            a2 += f"{stop(box['turn'])} "
    a2 += "Connected trees: " + "; ".join(link_line(m) for m in t["links"]) + "."
    return [a1.strip(), a2.strip()]


def whose_words(n):
    e, t = E[n - 1], TREES[n]
    out = [f"Year, title, and entry text: your On the Bus timeline (fact-checked{'; this entry was corrected, so use this version, not the essay draft' if e.get('fix') else ''})."]
    if e.get("scene"):
        out.append("Photo and scene caption: your timeline's scene for this entry.")
    if t.get("q"):
        out.append(f"{'Quotes' if len(t['q']) > 1 else 'Quote'}: your report, word for word.")
    if t.get("term"):
        fg = FIELD_GUIDE[t["term"]]
        out.append(f"Name it ({fg['term']}): your field guide, word for word"
                   + (f" ({fg['origin']})" if fg["origin"] else "") + ".")
    if t.get("commit"):
        out.append(f"What the history asks ({COMMITMENTS[t['commit']]['name']}): the closing of your report, word for word.")
    drafted = ["the first line"]
    if t.get("turn"):
        drafted.append("the short line under Name it")
    if t.get("ask") and not is_dark(n):
        drafted.append("the closing question")
    drafted.append("which trees connect")
    out.append("Drafted by Claude to weave it together (edit freely): " + ", ".join(drafted) + ".")
    return out


def tree_notes(n):
    e, t = E[n - 1], TREES[n]
    notes = []
    if n in CN:
        notes.append("Keep the content note as the first line of the caption.")
    if is_dark(n):
        notes.append("This is one of the darkest entries. It has no photo and no workplace line on purpose. "
                     "Consider turning off comments or not boosting it, and don't pair it with lighter posts the same day.")
    elif e["era"] == "killing":
        notes.append("This era has no photos and no workplace lines, on purpose.")
    if t.get("note"):
        notes.append(t["note"])
    if t.get("fresh"):
        notes.append(FRESH)
    if work_on(n, t):
        notes.append("The “At work” line comes from your field guide. It's a general example; if it mirrors your own "
                     "situation too closely, check with your lawyer before posting or drop that line.")
    notes.append("Instagram: post both slides as a carousel. LinkedIn: upload the PDF as a document post, or the two images.")
    return notes


def sources(n):
    return [f"{lab}: {url}" for lab, url in E[n - 1]["src"]]


posts, manifest = [], []


def add(slug, folder, slides, title, **kw):
    path = os.path.join(HTML_DIR, slug + ".html")
    open(path, "w", encoding="utf-8").write(page(slides, title))
    manifest.append(dict(slug=slug, html=path, kind="tree", folder=folder, n=len(slides)))
    posts.append(dict(slug=slug, folder=folder, title=title, slides=len(slides), **kw))


ROOT = "Timeline - Tree by Tree"
# Intro
add("00-intro", f"{ROOT}/00 Start here - On the Bus or Off the Bus", intro_slides(), "Start here: On the Bus or Off the Bus",
    kind="intro",
    caption="\n\n".join([
        "For four centuries, institutions sorted people with one question: can this person earn their keep?",
        "I built a timeline of that question, from a parish ledger in 1601 to a federal podium in 2025. Starting today I'm walking it one entry at a time: "
        f"{N} trees in {len(ERAS)} eras. Each post has two slides. The first is the moment itself. The second is what's under the surface: my own words from the report, the tactic it names, and the trees it connects to.",
        INTRO["note"],
        "“You're either on the bus or off the bus.” The question here is who built the bus, and who was never offered a seat.",
        INTRO["ask"],
        "The full timeline is linked in my bio.",
        "#OnTheBusOrOffTheBus #DisabilityHistory #Autism #Neurodiversity #WorkplaceBullying"]),
    alt=[f"Card: On the Bus or Off the Bus, a ledger of 425 years, 1601 to 2026. {INTRO['lede']} Photo: {INTRO['alt']}.",
         "Card: how to read the series. Slide 1 is the tree, one moment from the timeline. Slide 2 is under the surface: quotes from the report, the tactic it names, and connected trees. "
         "Six lanes: " + ", ".join(v["name"] for v in LANES.values()) + ". " + INTRO["note"]],
    sources=[f"Full timeline: {TIMELINE_URL}"],
    whose=["The lede, content note, and scene caption: your timeline's opening panel.",
           "Drafted by Claude (edit freely): the paragraph explaining how the series works, the first line of slide 2, and the closing question."],
    notes=["Pin this post once it's up, so new readers start here.",
           "Instagram: post both slides as a carousel. LinkedIn: upload the PDF as a document post."],
    numbers_ok=["1601", "2026", "2025", "425", str(N), str(len(ERAS)), "1", "2"])

order = []
for era in ERAS:
    i = ERA_N[era["id"]]
    ef = f"{ROOT}/{i:02d} Era {i} - {folder_safe(era['t'])} ({era['span'].replace('–', '-')})"
    slides, nums = era_slides(era)
    ask = ERA_ASK.get(era["id"])
    cap = [f"Era {i} of {len(ERAS)}: {era['t']} ({era['span']}).", era["p"],
           "The trees in this era:\n" + "\n".join(f"{date_label(E[m-1])}: {E[m-1]['t']}" for m in nums)]
    if era["id"] == "killing":
        cap.insert(0, "Content note: forced sterilization and the killing of disabled children and adults.")
        cap.append("The posts in this era have no photos and no workplace lines. That's on purpose.")
    if ask:
        cap.append(ask)
    cap += ["The full timeline is linked in my bio.", "#OnTheBusOrOffTheBus #DisabilityHistory"]
    add(f"era-{i}", f"{ef}/00 Era map", slides, f"Era {i} map: {era['t']}", kind="era",
        caption="\n\n".join(cap),
        alt=[f"Era map, era {i} of {len(ERAS)}: {era['t']}, {era['span']}. {era['p']} {len(nums)} trees, {nums[0]} to {nums[-1]}.",
             f"List of the trees in era {i}: "
             + "; ".join(f"{date_label(E[m-1]) if E[m-1].get('sub') == 'by' else E[m-1]['y']}, {plain_title(E[m-1]['t'])}" for m in nums) + "."],
        sources=[f"Full timeline: {TIMELINE_URL}"],
        whose=["Era title, span, summary, and entry list: your timeline.",
               "Drafted by Claude (edit freely): the closing question." if ask else "Nothing drafted beyond the layout."],
        notes=["Post this before the first tree of the era. It's the forest view for the trees that follow.",
               "Instagram: post both slides as a carousel. LinkedIn: upload the PDF as a document post."],
        numbers_ok=[str(len(nums)), str(nums[0]), str(nums[-1])], era=era["id"], trees=nums)
    for m in nums:
        e = E[m - 1]
        slug = f"tree-{m:02d}"
        folder = f"{ef}/Tree {m:02d} - {e['y']} - {folder_safe(e['t'])}"
        add(slug, folder, [tree_slide1(m), tree_slide2(m)], f"Tree {m} of {N}: {e['y']}, {plain_title(e['t'])}",
            kind="tree", n=m, caption=tree_caption(m), alt=tree_alt(m), sources=sources(m),
            whose=whose_words(m), notes=tree_notes(m), numbers_ok=[], era=era["id"],
            links=TREES[m]["links"], box=name_it(m, TREES[m]), quotes=TREES[m].get("q", []),
            dark=is_dark(m), cn=CN.get(m), photo=(e.get("scene") or {}).get("img"))

# Closing
add("99-closing", f"{ROOT}/{len(ERAS) + 1:02d} Closing - Who holds the acid", closing_slides(), "Closing: Who holds the acid?",
    kind="closing",
    caption="\n\n".join([
        "The last tree. 2026: the test, turned around.",
        CLOSING["paras"][0],
        "Sukhareva's five girls waited 93 years for English readers. Don Triplett played golf in a town that let him be himself. Lois Curtis left the hospital, made art, and handed a president her self-portrait.",
        CLOSING["paras"][1],
        "My report closes with six commitments: " + "; ".join(v["name"] for v in COMMITMENTS.values()) + ".",
        CLOSING["ask"],
        "The full timeline is linked in my bio.",
        "#OnTheBusOrOffTheBus #DisabilityHistory #Autism #Neurodiversity #DisabilityRights"]),
    alt=[f"Card: 2026, the test, turned around. Who holds the acid? {' '.join(CLOSING['paras'])} Photo: {CLOSING['alt']}.",
         "Card: what the history asks, six commitments from the report: "
         + "; ".join(f"{v['name']}: {sentences(v['text'])[0]}" for v in COMMITMENTS.values())],
    sources=[f"Full timeline: {TIMELINE_URL}"],
    whose=["Closing text and scene: your timeline's closing panel.",
           "The six commitments: the closing of your report, word for word.",
           "Drafted by Claude (edit freely): the first line and the closing question."],
    notes=["Post this after Tree 83.",
           "Instagram: post both slides as a carousel. LinkedIn: upload the PDF as a document post."],
    numbers_ok=["2026", "93"])

json.dump(manifest, open(os.path.join(HTML_DIR, "manifest.json"), "w"), indent=1)
json.dump(posts, open(os.path.join(OUT, "posts.json"), "w"), indent=1, ensure_ascii=False)
print(f"built {len(posts)} posts, {sum(p['slides'] for p in posts)} slides -> {OUT}")
