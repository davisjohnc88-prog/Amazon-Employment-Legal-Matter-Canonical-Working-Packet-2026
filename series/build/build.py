# Builds HTML pages for every carousel, single post, and the poster.
# Usage: python3 build.py <fonts_dir> <out_dir>   (photos come from series/img, or $SERIES_IMG)
import sys, os, html, json
sys.path.insert(0, os.path.dirname(__file__))
from content import SERIES, CAROUSELS, SINGLES, POSTER_TERMS

FONTS = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
IMG = os.environ.get("SERIES_IMG", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img")))
os.makedirs(OUT, exist_ok=True)

CSS = open(os.path.join(FONTS, "fonts.css")).read().replace("url(f", f"url(file://{FONTS}/f") + """
:root{--cream:#F5EEE2;--paper:#FBF7F0;--ink:#1E2528;--teal:#1D5B5B;--teal2:#2E7A76;--mari:#E3892B;--rose:#C2574A;--sand:#E7D9C2;--muted:#6B6259}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--cream)}
@page{size:1080px 1350px;margin:0}
.slide{width:1080px;height:1350px;position:relative;overflow:hidden;background:var(--cream);color:var(--ink);font-family:Inter,sans-serif;page-break-after:always;break-after:page}
.serif{font-family:Fraunces,serif}
.pad{position:absolute;inset:96px 92px 150px 92px;display:flex;flex-direction:column;justify-content:center}
.pad>.kicker{position:absolute;top:0;left:0}
.kicker{font:700 26px/1 Inter;letter-spacing:.18em;text-transform:uppercase;color:var(--mari);margin-bottom:34px;display:flex;align-items:center;gap:16px}
.kicker:before{content:"";width:46px;height:4px;background:var(--mari);border-radius:2px}
h1,h2{font-family:Fraunces,serif;font-weight:700;letter-spacing:-.01em}
h2{font-size:76px;line-height:1.04;margin-bottom:40px}
h1 em,h2 em{font-style:italic;font-weight:500;color:var(--mari)}
.body p{font-size:38px;line-height:1.42;margin-bottom:28px;color:#2b3236}
.body strong{color:var(--teal)}
.big-line{font-family:Fraunces,serif;font-weight:700;font-size:50px!important;line-height:1.15!important;color:var(--ink)!important;margin-top:14px}
.source{position:absolute;left:0;right:0;bottom:0;font-size:22px;line-height:1.4;color:var(--muted);border-top:2px solid var(--sand);padding-top:20px}
.foot{position:absolute;left:92px;right:92px;bottom:58px;display:flex;justify-content:space-between;align-items:center;font:600 21px/1 Inter;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.foot .pg{color:var(--teal)}
.dark .foot,.dark .foot .pg{color:rgba(255,255,255,.85)}
.photo{position:absolute;inset:0;background-size:cover;background-position:center 18%}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,40,40,0) 22%,rgba(18,40,40,.86) 48%,rgba(14,30,30,.97) 100%)}
.dark:after{content:"";position:absolute;left:0;right:0;bottom:0;height:130px;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.55))}
.dark .foot{z-index:2}
.cover .txt{position:absolute;left:92px;right:92px;bottom:150px;color:#fff}
.cover .kicker{color:#F6B66A}.cover .kicker:before{background:#F6B66A}
.cover h1{font-size:84px;line-height:1.03;margin-bottom:30px}
.cover h1 em{color:#F6B66A}
.cover .huge{display:block;font-size:150px;line-height:1;color:#F6B66A;margin-bottom:14px}
.cover .sub{font-size:34px;line-height:1.38;color:rgba(255,255,255,.88);max-width:860px}
.statement .card{position:absolute;left:70px;right:70px;bottom:140px;background:var(--paper);border-radius:28px;padding:60px 64px;box-shadow:0 20px 60px rgba(0,0,0,.25)}
.statement h2{font-size:64px;margin-bottom:22px}
.statement .sub{font:italic 500 44px/1.2 Fraunces;color:var(--teal)}
.statement .small{font-size:24px;color:var(--muted);margin-top:26px}
.term .num{font:900 230px/0.8 Fraunces;color:var(--sand);position:absolute;right:70px;top:70px}
.term h2{font-size:104px;margin-top:40px;margin-bottom:34px;max-width:860px}
.term .def{font-size:46px;line-height:1.38;margin-bottom:52px}
.term .def strong{color:var(--mari)}
.says{background:#fff;border-left:10px solid var(--mari);border-radius:6px 22px 22px 6px;padding:36px 44px;box-shadow:0 8px 30px rgba(30,37,40,.07)}
.says .lab{font:700 22px/1 Inter;letter-spacing:.16em;text-transform:uppercase;color:var(--teal);margin-bottom:20px}
.says p{font:italic 500 44px/1.3 Fraunces;margin-bottom:12px}
.list ol{list-style:none;counter-reset:i}
.list li{counter-increment:i;position:relative;padding-left:88px;font-size:34px;line-height:1.36;margin-bottom:30px}
.list li:before{content:counter(i);position:absolute;left:0;top:-4px;width:60px;height:60px;border-radius:50%;background:var(--teal);color:#fff;font:700 30px/60px Fraunces;text-align:center}
.list h2{font-size:64px}
.bars .row{display:flex;align-items:center;margin-bottom:34px}
.bars .lab{width:230px;font:600 34px Inter}
.bars .track{flex:1;height:70px;background:var(--sand);border-radius:35px;overflow:hidden}
.bars .fill{height:100%;border-radius:35px}
.teal{background:var(--teal2)}.rose{background:var(--rose)}
.note{font-size:30px;line-height:1.42;color:#3b4245;margin-top:30px;background:var(--paper);border-radius:20px;padding:30px 36px}
.stat .num{font:900 260px/0.9 Fraunces;color:var(--teal);letter-spacing:-.03em;margin-top:10px}
.stat .label{font:600 46px/1.25 Inter;margin:26px 0 40px;max-width:880px}
.minis{display:flex;gap:28px;margin-bottom:34px}
.mini{flex:1;background:var(--paper);border-radius:22px;padding:30px 32px}
.mini b{display:block;font:800 66px/1 Fraunces;color:var(--mari);margin-bottom:12px}
.mini span{font-size:27px;line-height:1.3;color:#3b4245}
.stat .body2{font:italic 500 38px/1.35 Fraunces;color:var(--ink)}
.compare .row{margin-bottom:56px}
.compare .lab{font:600 36px/1.2 Inter;margin-bottom:18px}
.compare .track{height:110px;background:var(--sand);border-radius:20px;position:relative;overflow:hidden}
.compare .fill{height:100%;border-radius:20px;display:flex;align-items:center;justify-content:flex-end;padding-right:30px;color:#fff;font:900 64px Fraunces}
.map .grid{display:grid;grid-template-columns:1fr 70px 1fr;row-gap:22px;align-items:stretch}
.map .hd{font:700 22px Inter;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.map .a,.map .b{border-radius:18px;padding:24px 26px;font-size:30px;line-height:1.28}
.map .a{background:var(--paper)}
.map .b{background:var(--teal);color:#fff}
.map .ar{display:flex;align-items:center;justify-content:center;font:700 44px Fraunces;color:var(--mari)}
.ladder .rung{display:flex;gap:30px;align-items:stretch;margin-bottom:22px}
.ladder .t{width:170px;flex:none;background:var(--teal);color:#fff;border-radius:18px;font:800 36px/1 Fraunces;display:flex;align-items:center;justify-content:center}
.ladder .rung:last-child .t{background:var(--mari)}
.ladder .d{flex:1;background:var(--paper);border-radius:18px;padding:26px 30px;font-size:31px;line-height:1.32}
.record .sheet{background:#fff;border-radius:22px;padding:34px 44px;box-shadow:0 10px 40px rgba(30,37,40,.08);background-image:repeating-linear-gradient(#fff 0 86px,#E9E1D3 86px 88px)}
.record .f{height:88px;display:flex;align-items:flex-end;padding-bottom:14px;font:700 26px Inter;letter-spacing:.06em;text-transform:uppercase;color:var(--teal)}
.record h2{font-size:62px}
.cta .card{position:absolute;left:70px;right:70px;bottom:130px;background:var(--teal);color:#fff;border-radius:28px;padding:58px 64px}
.cta .kicker{color:#F6B66A}.cta .kicker:before{background:#F6B66A}
.cta h2{font-size:68px;margin-bottom:22px}
.cta .b1{font-size:34px;line-height:1.38;opacity:.92;margin-bottom:30px}
.cta .b2{font:600 28px/1.4 Inter;color:#F6B66A;border-top:2px solid rgba(255,255,255,.25);padding-top:24px}
.swipe{position:absolute;right:92px;top:96px;font:700 22px Inter;letter-spacing:.14em;text-transform:uppercase;color:#fff;background:rgba(0,0,0,.35);padding:14px 20px;border-radius:30px}
/* singles */
.single .panel{position:absolute;left:0;right:0;bottom:0;background:var(--paper);padding:58px 80px 120px;border-radius:40px 40px 0 0}
.single .q{font:700 68px/1.08 Fraunces;margin-bottom:24px}
.single .q.long{font-size:54px;line-height:1.16;font-style:italic;font-weight:500}
.single .s{font-size:33px;line-height:1.4;color:#3b4245}
.single .foot{bottom:46px}
/* poster */
.poster .pad>.kicker{position:static}
.poster h2{font-size:70px;margin-bottom:14px}
.poster .lede{font-size:32px;color:var(--muted);margin-bottom:40px}
.poster .g{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.poster .c{background:var(--paper);border-radius:18px;padding:22px 26px;border-top:8px solid var(--teal)}
.poster .c:nth-child(3n+2){border-top-color:var(--mari)}.poster .c:nth-child(3n){border-top-color:var(--rose)}
.poster .c b{display:block;font:700 29px/1.1 Fraunces;margin-bottom:8px}
.poster .c span{font-size:22px;line-height:1.3;color:#3b4245}
.poster .tag{margin-top:34px;font:italic 600 38px/1.2 Fraunces;color:var(--teal);text-align:center}
"""

def img(name): return f"file://{IMG}/{name}.jpg"
def foot(i, n, dark=False, swipe=True):
    arrow = " →" if (swipe and i < n) else ""
    return f'<div class="foot"><span>{SERIES}</span><span class="pg">{i:02d} / {n:02d}{arrow}</span></div>'

def src(s): return f'<div class="source">Source: {s}</div>' if s else ""

def slide(s, i, n):
    t = s["type"]
    if t == "cover":
        return f'''<section class="slide cover dark"><div class="photo" style="background-image:url({img(s['img'])})"></div><div class="shade"></div>
<div class="swipe">Swipe →</div><div class="txt"><div class="kicker">{s['kicker']}</div><h1>{s['title']}</h1><div class="sub">{s['sub']}</div></div>{foot(i,n,True)}</section>'''
    if t == "text":
        return f'''<section class="slide text"><div class="pad"><div class="kicker">{s['kicker']}</div><h2>{s['title']}</h2><div class="body">{s['body']}</div>{src(s.get('source'))}</div>{foot(i,n)}</section>'''
    if t == "statement":
        small = f'<div class="small">{s["small"]}</div>' if s.get("small") else ""
        return f'''<section class="slide statement dark"><div class="photo" style="background-image:url({img(s['img'])})"></div>
<div class="card"><h2>{s['title']}</h2><div class="sub">{s['sub']}</div>{small}</div>{foot(i,n,True)}</section>'''
    if t == "term":
        says = "".join(f"<p>{x}</p>" for x in s["says"])
        return f'''<section class="slide term"><div class="num">{s['n']}</div><div class="pad"><div class="kicker">Name it</div><h2>{s['term']}</h2>
<div class="def">{s['def']}</div><div class="says"><div class="lab">What it sounds like</div>{says}</div>{src(s['origin']).replace('Source: ','Where the term comes from: ')}</div>{foot(i,n)}</section>'''
    if t == "list":
        lis = "".join(f"<li>{x}</li>" for x in s["items"])
        return f'''<section class="slide list"><div class="pad"><div class="kicker">{s['kicker']}</div><h2>{s['title']}</h2><ol>{lis}</ol></div>{foot(i,n)}</section>'''
    if t == "bars":
        rows = "".join(f'<div class="row"><div class="lab">{l}</div><div class="track"><div class="fill {c}" style="width:{v}%"></div></div></div>' for l, v, c in s["bars"])
        return f'''<section class="slide bars"><div class="pad"><div class="kicker">{s['kicker']}</div><h2>{s['title']}</h2>{rows}<div class="note">{s['note']}</div></div>{foot(i,n)}</section>'''
    if t == "stat":
        minis = ""
        if s.get("minis"):
            minis = '<div class="minis">' + "".join(f'<div class="mini"><b>{a}</b><span>{b}</span></div>' for a, b in s["minis"]) + "</div>"
        body = f'<div class="body2">{s["body"]}</div>' if s.get("body") else ""
        return f'''<section class="slide stat"><div class="pad"><div class="kicker">{s['kicker']}</div><div class="num">{s['num']}</div><div class="label">{s['label']}</div>{minis}{body}{src(s.get('source'))}</div>{foot(i,n)}</section>'''
    if t == "compare":
        rows = "".join(f'<div class="row"><div class="lab">{l}</div><div class="track"><div class="fill {c}" style="width:{v}%">{v}%</div></div></div>' for l, v, c in s["rows"])
        return f'''<section class="slide compare"><div class="pad"><div class="kicker">{s['kicker']}</div><h2>{s['title']}</h2>{rows}<div class="note">{s['note']}</div>{src(s.get('source'))}</div>{foot(i,n)}</section>'''
    if t == "map":
        cells = '<div class="hd">At home</div><div></div><div class="hd">At work</div>' + "".join(f'<div class="a">{a}</div><div class="ar">→</div><div class="b">{b}</div>' for a, b in s["rows"])
        return f'''<section class="slide map"><div class="pad"><div class="kicker">{s['kicker']}</div><h2>{s['title']}</h2><div class="grid">{cells}</div></div>{foot(i,n)}</section>'''
    if t == "ladder":
        r = "".join(f'<div class="rung"><div class="t">{a}</div><div class="d">{b}</div></div>' for a, b in s["rungs"])
        return f'''<section class="slide ladder"><div class="pad"><div class="kicker">{s['kicker']}</div><h2>{s['title']}</h2>{r}</div>{foot(i,n)}</section>'''
    if t == "record":
        f = "".join(f'<div class="f">{x}</div>' for x in s["fields"])
        return f'''<section class="slide record"><div class="pad"><div class="kicker">{s['kicker']}</div><h2>{s['title']}</h2><div class="sheet">{f}</div><div class="note">{s['note']}</div></div>{foot(i,n)}</section>'''
    if t == "cta":
        return f'''<section class="slide cta dark"><div class="photo" style="background-image:url({img(s['img'])})"></div>
<div class="card"><div class="kicker">{s['kicker']}</div><h2>{s['title']}</h2><div class="b1">{s['body']}</div><div class="b2">{s['foot']}</div></div>{foot(i,n,True,False)}</section>'''
    raise ValueError(t)

def page(body, title):
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>"

manifest = []
for c in CAROUSELS:
    n = len(c["slides"])
    body = "".join(slide(s, i + 1, n) for i, s in enumerate(c["slides"]))
    p = os.path.join(OUT, c["slug"] + ".html")
    open(p, "w").write(page(body, c["title"]))
    manifest.append({"slug": c["slug"], "html": p, "kind": "carousel", "n": n})

for s in SINGLES:
    long = " long" if len(s["quote"]) > 70 else ""
    sub = f'<div class="s">{s["sub"]}</div>' if s.get("sub") else ""
    body = f'''<section class="slide single"><div class="photo" style="background-image:url({img(s['img'])});background-position:center 10%;height:880px"></div>
<div class="panel"><div class="kicker">{s['kicker']}</div><div class="q{long}">{s['quote']}</div>{sub}</div>
<div class="foot"><span>{SERIES}</span><span class="pg">Link in bio</span></div></section>'''
    p = os.path.join(OUT, s["slug"] + ".html")
    open(p, "w").write(page(body, s["slug"]))
    manifest.append({"slug": s["slug"], "html": p, "kind": "single", "n": 1})

cards = "".join(f"<div class='c'><b>{a}</b><span>{b}</span></div>" for a, b in POSTER_TERMS)
body = f'''<section class="slide poster"><div class="pad" style="bottom:120px"><div class="kicker">Save this</div><h2>The vocabulary nobody gave you</h2>
<div class="lede">Twelve tactics, in plain words. When you can name a tactic, it gets harder to use on you.</div><div class="g">{cards}</div>
</div><div class="foot"><span>{SERIES}</span><span class="pg">Full series: link in bio</span></div></section>'''
p = os.path.join(OUT, "p11-vocabulary-poster.html")
open(p, "w").write(page(body, "poster"))
manifest.append({"slug": "p11-vocabulary-poster", "html": p, "kind": "single", "n": 1})

json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
print(len(manifest), "pages")
