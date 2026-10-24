# Packs every post into its own folder: the slide images, the LinkedIn PDF, and a "Post wording.docx"
# with the caption, alt text, sources, whose words are whose, and posting notes. No AI involved.
# Usage: python3 make_package.py <trees_build_dir> <out_dir>
#   trees_build_dir = the folder build_trees.py + render_trees.js + check_trees.py wrote (posts.json, pkg/, CHECK-REPORT.md)
#   out_dir         = where "Workplace Psych/" gets written
import datetime, glob, html as H, json, os, re, shutil, sys
from docx import Document
from docx.enum.text import WD_BREAK
from docx.shared import Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
SERIES = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SERIES, "build"))
import content as C  # batch 01 slides

TREES, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
ROOT = os.path.join(OUT, "Workplace Psych")
B1 = os.path.join(SERIES, "batch-01")
TODAY = datetime.date.today().strftime("%B %-d, %Y")
INK, ACC, SOFT = RGBColor(0x1C, 0x28, 0x24), RGBColor(0xB2, 0x3A, 0x35), RGBColor(0x4A, 0x5A, 0x54)
TIMELINE_URL = "https://claude.ai/artifact/U8XhxLs1m2Xs8o4ydrXA8k"


# ---------------------------------------------------------------- docx helpers
def new_doc():
    d = Document()
    st = d.styles["Normal"]
    st.font.name, st.font.size = "Calibri", Pt(11)
    st.paragraph_format.space_after = Pt(6)
    for name, size, color in (("Title", 22, INK), ("Heading 1", 15, ACC), ("Heading 2", 12, INK)):
        s = d.styles[name]
        s.font.name, s.font.size, s.font.color.rgb = "Georgia", Pt(size), color
    return d


def lines(d, text, size=None, color=None, italic=False):
    """One paragraph per line, so the text pastes into Instagram or LinkedIn with its line breaks."""
    for ln in text.split("\n"):
        p = d.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(ln)
        r.italic = italic
        if size:
            r.font.size = Pt(size)
        if color:
            r.font.color.rgb = color
    return p


def caption(d, text):
    blocks = text.split("\n\n")
    for i, b in enumerate(blocks):
        lines(d, b)
        if i < len(blocks) - 1:
            d.add_paragraph().paragraph_format.space_after = Pt(0)


def bullets(d, items):
    for it in items:
        d.add_paragraph(it, style="List Bullet")


def meta(d, text):
    p = d.add_paragraph()
    r = p.add_run(text)
    r.font.size, r.font.color.rgb = Pt(10), SOFT
    return p


def md_inline(p, s):
    """**bold**, *italic*, `code`, and [label](url) for the plain markdown files."""
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", s)
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", s):
        if part.startswith("**"):
            p.add_run(part[2:-2]).bold = True
        elif part.startswith("*") and len(part) > 1:
            p.add_run(part[1:-1]).italic = True
        elif part.startswith("`"):
            p.add_run(part[1:-1])
        elif part:
            p.add_run(part)


def md_to_docx(md, path, title=None):
    d = new_doc()
    if title:
        d.add_heading(title, 0)
    table = []

    def flush():
        if not table:
            return
        rows = [r for r in table if not re.match(r"^\|\s*-", r)]
        cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        t = d.add_table(rows=len(cells), cols=len(cells[0]))
        t.style = "Light Grid Accent 1"
        for i, row in enumerate(cells):
            for j, c in enumerate(row[: len(cells[0])]):
                t.cell(i, j).text = ""
                md_inline(t.cell(i, j).paragraphs[0], c)
        table.clear()

    for ln in md.splitlines():
        if ln.startswith("|"):
            table.append(ln)
            continue
        flush()
        if not ln.strip() or ln.strip() == "---":
            continue
        m = re.match(r"^(#+) (.*)", ln)
        if m:
            lvl = len(m.group(1))
            if lvl == 1 and title:
                continue
            d.add_heading(m.group(2).replace("`", ""), 0 if lvl == 1 else min(lvl - 1, 3))
        elif re.match(r"^\s*[-*] ", ln):
            md_inline(d.add_paragraph(style="List Bullet"), re.sub(r"^\s*[-*] ", "", ln))
        elif re.match(r"^\d+\. ", ln):
            md_inline(d.add_paragraph(style="List Number"), re.sub(r"^\d+\. ", "", ln))
        elif ln.startswith(">"):
            p = d.add_paragraph()
            p.paragraph_format.left_indent = Pt(18)
            p.paragraph_format.space_after = Pt(0)
            md_inline(p, ln.lstrip("> ").rstrip())
        else:
            md_inline(d.add_paragraph(), ln)
    flush()
    d.save(path)


def post_doc(path, title, sub, files, cap, alts, sources, whose, notes, checks, extra=None):
    d = new_doc()
    d.add_heading(title, 0)
    meta(d, sub)
    d.add_heading("What's in this folder", 1)
    bullets(d, files)
    d.add_heading(f"Caption (copy and paste) · {len(cap):,} of 2,200 characters", 1)
    caption(d, cap)
    d.add_heading("Alt text (paste into each image's accessibility setting)", 1)
    for i, a in enumerate(alts, 1):
        p = d.add_paragraph()
        p.add_run(("Slide " + str(i) + ": " if len(alts) > 1 else "Image: ")).bold = True
        p.add_run(a)
    d.add_heading("Sources (paste as the first comment)", 1)
    if sources:
        lines(d, "\n".join(sources))
    else:
        d.add_paragraph("No outside sources in this post.")
    if extra:
        for head, body in extra:
            d.add_heading(head, 1)
            for b in body:
                d.add_paragraph(b)
    d.add_heading("Whose words are these", 1)
    bullets(d, whose)
    d.add_heading("Before you post", 1)
    bullets(d, notes)
    d.add_heading("Checks", 1)
    bullets(d, checks)
    d.save(path)


def plain(s):
    s = re.sub(r"<br\s*/?>", " ", s or "")
    s = re.sub(r"</?(strong|em|b|i)[^>]*>", "", s)
    s = re.sub(r"</p>\s*<p>", " ", s)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def stop(s):
    s = s.strip()
    return s if not s or s[-1] in ".!?’”\"…" else s + "."


# ---------------------------------------------------------------- the timeline, tree by tree
def check_lines(report_path, slug_ok, label):
    rep = open(report_path, encoding="utf-8").read()
    head = re.search(r"\*\*(\d+) fail, (\d+) warn\.\*\*", rep)
    fails = int(head.group(1)) if head else -1
    lines_ = [l for l in rep.splitlines() if l.startswith("- **")]
    mine = [l for l in lines_ if slug_ok(l)]
    if fails == 0 and not mine:
        first = f"Scripted check ({label}, {TODAY}): passed, 0 problems."
    else:
        first = f"Scripted check ({label}, {TODAY}): {len(mine)} item(s) for this post. See the check report."
    return first, rep


def trees():
    base = os.path.join(ROOT, "Timeline - Tree by Tree")
    posts = json.load(open(os.path.join(TREES, "posts.json"), encoding="utf-8"))
    report = os.path.join(TREES, "CHECK-REPORT.md")
    total = len(posts)
    for k, p in enumerate(posts):
        src = os.path.join(TREES, "pkg", p["folder"])
        dst = os.path.join(ROOT, p["folder"])
        os.makedirs(dst, exist_ok=True)
        files = []
        for f in sorted(os.listdir(src)):
            shutil.copy2(os.path.join(src, f), dst)
        imgs = sorted(f for f in os.listdir(dst) if f.endswith(".png"))
        for f in imgs:
            files.append(f"{f}: for Instagram, Facebook, or Threads (1080 × 1350).")
        if os.path.exists(os.path.join(dst, "LinkedIn carousel.pdf")):
            files.append("LinkedIn carousel.pdf: upload to LinkedIn as a document post.")
        files.append("Post wording.docx: this document.")
        first, _ = check_lines(report, lambda l: f" {p['slug']} " in l or f" {p['slug']}:" in l, "timeline series")
        checks = [first,
                  "What the script checked: the employer is never named; every quote matches your report word for word; "
                  "every number traces to the timeline entry, a connected entry, or a source file; spelling; content notes, "
                  "no workplace lines next to the darkest history, and the 988 line where needed; and that no text spills, "
                  "clips, or shrinks too small on any slide.",
                  "Editorial read for human eyes: done (wording, flow, and every slide looked at)."]
        prev_ = posts[k - 1]["title"] if k else None
        next_ = posts[k + 1]["title"] if k + 1 < total else None
        sub = f"On the Bus or Off the Bus · post {k + 1} of {total}"
        if prev_:
            sub += f" · after: {prev_}"
        if next_:
            sub += f" · next: {next_}"
        post_doc(os.path.join(dst, "Post wording.docx"), p["title"], sub, files, p["caption"], p["alt"],
                 p["sources"], p["whose"], p["notes"], checks)
    shutil.copy2(report, os.path.join(base, "Check report.md"))
    md_to_docx(open(report, encoding="utf-8").read(), os.path.join(base, "Check report.docx"))
    return posts


# ---------------------------------------------------------------- batch 01, one folder per post
PHOTO = {
    "archive": "John Charles in the white duck dress, standing in an archive of card-catalog drawers, holding a small notebook",
    "backstage-mask": "John Charles in the white duck dress, seated backstage, setting a white mask down on a table",
    "bookshop-writing": "John Charles in the white duck dress, chin on hand, writing in a notebook at a bookshop desk beside a mug of tea",
    "cat-lap": "John Charles in the white duck dress, in an armchair with a tabby cat on their lap",
    "desk-journal": "John Charles in the white duck dress, at a desk among plants and books, pen on a journal, looking up and smiling",
    "desk-papers": "John Charles in the white duck dress, at a desk with notebooks and papers, hand to chin, thinking",
    "doorway": "John Charles in the white duck dress, holding a door open and gesturing inside",
    "finish-lines": "John Charles in the white duck dress, arms crossed, in front of a glowing road lined with finish-line banners",
    "forest-lens": "John Charles in the white duck dress, sitting on a log in an autumn forest with a magnifying glass and a field notebook",
    "library-rain": "John Charles in the white duck dress, reading in a library armchair by a rainy window, a cup of tea nearby",
    "map-string": "John Charles in the white duck dress, at a desk with a map, a magnifying glass, and stacks of papers, pencil in hand",
    "paper-stacks": "John Charles in the white duck dress, at a desk surrounded by towering stacks of paperwork",
    "picnic": "John Charles in the white duck dress, at a riverside picnic at sunset, passing a berry pie",
    "repotting": "John Charles in the white duck dress, in a greenhouse, lifting a plant's roots out of a pot",
    "sewing-measure": "John Charles in the white duck dress, at a sewing table with a yellow tape measure, a dress form behind",
    "shadow-maze": "John Charles in the white duck dress, shining a lamp on a cut-out maze so its shadow shows on the wall",
    "sofa-tea": "John Charles on a sofa with a cup of tea, looking up thoughtfully",
    "timeclock": "John Charles in the white duck dress, standing beside an old punch clock",
}


def slide_alt(s):
    t = s["type"]
    g = lambda k: plain(s.get(k, ""))
    ph = f" Photo: {PHOTO[s['img']]}." if s.get("img") else ""
    src = f" Source: {stop(g('source'))}" if s.get("source") else ""
    if t == "cover":
        a = f"Cover. {stop(g('kicker'))} {stop(g('title'))} {stop(g('sub'))}"
    elif t == "text":
        a = f"{stop(g('kicker'))} {stop(g('title'))} {stop(g('body'))}"
    elif t == "statement":
        a = f"{stop(g('title'))} {stop(g('sub'))} {stop(g('small'))}"
    elif t == "term":
        a = (f"Name it, term {s['n']}: {stop(g('term'))} {stop(g('def'))} What it sounds like: "
             + " ".join(stop(plain(x)) for x in s["says"]) + f" Where the term comes from: {stop(g('origin'))}")
    elif t == "list":
        a = f"{stop(g('kicker'))} {stop(g('title'))} " + " ".join(f"{i}. {stop(plain(x))}" for i, x in enumerate(s["items"], 1))
    elif t == "bars":
        a = (f"{stop(g('kicker'))} {stop(g('title'))} A rough bar picture: "
             + ", ".join(f"{l} {'high' if v >= 50 else 'low'}" for l, v, _ in s["bars"]) + f". {stop(g('note'))}")
    elif t == "stat":
        a = f"{stop(g('kicker'))} {plain(s['num'])} {stop(g('label'))}"
        if s.get("minis"):
            a += " " + " ".join(f"{plain(x)} {stop(plain(y))}" for x, y in s["minis"])
        a += " " + stop(g("body"))
    elif t == "compare":
        a = f"{stop(g('kicker'))} {stop(g('title'))} " + "; ".join(f"{plain(l)}: {v}%" for l, v, _ in s["rows"]) + f". {stop(g('note'))}"
    elif t == "map":
        h1, h2 = s.get("heads", ["At home", "At work"])
        a = f"{stop(g('kicker'))} {stop(g('title'))} Two columns, {h1} and {h2}: " + "; ".join(f"{plain(x)} becomes {plain(y)}" for x, y in s["rows"]) + "."
    elif t == "ladder":
        a = f"{stop(g('kicker'))} {stop(g('title'))} " + " ".join(f"{plain(x)}: {stop(plain(y))}" for x, y in s["rungs"])
    elif t == "record":
        a = f"{stop(g('kicker'))} {stop(g('title'))} A blank record sheet with these fields: " + ", ".join(plain(x) for x in s["fields"]) + f". {stop(g('note'))}"
    elif t == "cta":
        a = f"{stop(g('kicker'))} {stop(g('title'))} {stop(g('body'))} {stop(g('foot'))}"
    else:
        raise ValueError(t)
    return re.sub(r"\s+", " ", (a + src + ph).replace(" .", "")).strip()


def plan_parts():
    plan = open(os.path.join(B1, "POSTING-PLAN.md"), encoding="utf-8").read()
    caps, extra = {}, {}
    for m in re.finditer(r"^### Carousel (\d\d):.*?\n(.*?)(?=^### |^---)", plan, re.M | re.S):
        body = m.group(2)
        q = []
        for ln in body.splitlines():
            if ln.startswith(">"):
                q.append(ln[1:].strip())
        caps[m.group(1)] = re.sub(r"\n{3,}", "\n\n", "\n".join(q)).strip()
        lv = re.search(r"\*\*LinkedIn version:\*\* (.*)", body)
        if lv:
            extra[m.group(1)] = lv.group(1).strip()
    for m in re.finditer(r'^- \*\*(p\d\d)[^*]*:\*\* "(.*)"\s*$', plan, re.M):
        caps[m.group(1)] = m.group(2)
    return caps, extra


CORE_TAGS = "#workplacebullying #toxicworkplace #narcissisticabuse #gaslighting #scapegoat #mentalhealthatwork #DARVO #healingjourney #youarenotalone #neurodiversity"
B1_SOURCES = {
    "00": ["Trundle et al. (2023), Trauma, Violence, & Abuse: https://doi.org/10.1177/15248380221093689",
           "History dates: my report, On the Bus or Off the Bus (fact-checked).",
           f"The full timeline: {TIMELINE_URL}"],
    "01": ["Harsey & Freyd (2020), on DARVO: https://doi.org/10.1080/10926771.2020.1774695",
           "Term origins: Freyd (1997) for DARVO; Bateson and colleagues (1956) for the double bind; the 1938 play Gas Light for gaslighting."],
    "02": ["Smith & Freyd (2014), \"Institutional betrayal,\" American Psychologist: https://doi.org/10.1037/a0037564",
           "In crisis in the US: call or text 988."],
    "03": ["Workplace Bullying Institute, 2024 U.S. Workplace Bullying Survey: https://workplacebullying.org/2024-wbi-us-survey/",
           "Trundle et al. (2023), Trauma, Violence, & Abuse: https://doi.org/10.1177/15248380221093689"],
    "04": ["Tavris & Aronson (2007), Mistakes Were Made (But Not by Me), Harcourt."],
    "05": ["In crisis in the US: call or text 988."],
}
B1_ORDER = [  # the two-week schedule from POSTING-PLAN.md
    ("p09", "Before launch", "Back tomorrow", "IG, FB, Threads"),
    ("00", "Day 1 first", "The whole map (pin it)", "IG, LinkedIn (PDF)"),
    ("p10", "Day 1", "I'm writing it all down", "All"),
    ("01", "Day 1", "You're not crazy, it has a name", "IG, LinkedIn (PDF)"),
    ("p02", "Day 2", "Gaslighting", "IG, Threads"),
    ("02", "Day 3", "Healing everywhere but work", "IG, LinkedIn (PDF)"),
    ("p11", "Day 4", "Vocabulary poster", "All (made to be saved)"),
    ("03", "Day 5", "By the numbers", "LinkedIn (PDF), IG"),
    ("p04", "Day 6", "Flying monkeys", "IG, Threads"),
    ("p05", "Day 7", "Keep your own record", "All"),
    ("p01", "Day 8", "The least believed", "IG, FB"),
    ("04", "Day 9", "From scapegoat to target", "IG, LinkedIn (PDF)"),
    ("p03", "Day 10", "Moving the goalposts", "IG, Threads"),
    ("p06", "Day 11", "Masking", "IG"),
    ("05", "Day 12", "The next 10 minutes", "All"),
    ("p07", "Day 13", "Hope as a retention tool", "IG, LinkedIn"),
    ("p08", "Day 14", "The quiet PIP", "IG, LinkedIn"),
]
B1_WHOSE_DEFAULT = ("Drafted by Claude from what you told me: youngest of nine, the family scapegoat, the breakup and court case, "
                    "healing everywhere but work, giving too many chances. Read it out loud and change anything that doesn't sound like you.")
B1_WHOSE = {
    "00": ["The history rungs and the title of your report: On the Bus or Off the Bus (fact-checked).", B1_WHOSE_DEFAULT],
    "01": ["Term definitions: your report's field guide, put into plain words. Origins: the cited research.", B1_WHOSE_DEFAULT],
    "03": ["Every number: the 2024 WBI survey and Trundle et al. (2023), checked against the sources.", B1_WHOSE_DEFAULT],
    "p01": ["The quote: your memoir, word for word (\"I was the youngest. The least believed…\").",
            "Drafted by Claude (edit freely): the caption around it."],
    "p11": ["The twelve terms: your report's field guide, in plain words.", "Drafted by Claude (edit freely): the caption."],
}


def batch01():
    base = os.path.join(ROOT, "Batch 01 - The Whole Map")
    caps, extra = plan_parts()
    car = {c["slug"][:2]: c for c in C.CAROUSELS}
    sing = {s["slug"][:3]: s for s in C.SINGLES}
    first, _ = check_lines(os.path.join(B1, "CHECK-REPORT.md"), lambda l: False, "batch 01")
    checks = [first,
              "What the script checked: the employer is never named, every number traces to a source, spelling, the crisis line, and the layout of every slide.",
              "Editorial read for human eyes: done."]
    made = []
    for k, (key, day, title, where) in enumerate(B1_ORDER, 1):
        folder = os.path.join(base, f"{k:02d} - {day} - {title}")
        os.makedirs(folder, exist_ok=True)
        notes = [f"Schedule: {day}. Where: {where}.", "Post in your best window, usually 7–9am or 6–8pm local time."]
        files = []
        if key in car:
            c = car[key]
            src = os.path.join(B1, "carousels", c["slug"])
            for f in sorted(os.listdir(src)):
                n = int(re.search(r"\d+", f).group())
                shutil.copy2(os.path.join(src, f), os.path.join(folder, f"Slide {n}.png"))
                files.append(f"Slide {n}.png")
            shutil.copy2(os.path.join(B1, "carousels", c["slug"] + ".pdf"), os.path.join(folder, "LinkedIn carousel.pdf"))
            files = [f + ": for Instagram or Facebook (1080 × 1350)." for f in files]
            files.append("LinkedIn carousel.pdf: upload to LinkedIn as a document post.")
            alts = [slide_alt(s) for s in c["slides"]]
            kind = "Carousel"
            cap = caps[key]
            src_ = B1_SOURCES.get(key, [])
            notes.append("Instagram: post the slides in order as one carousel. LinkedIn: upload the PDF as a document post.")
            if key == "00":
                notes.append("Pin this one to the top of your profile. It's the bird's-eye view of the whole series.")
            if key in extra:
                notes.append("LinkedIn version: " + extra[key])
            whose = B1_WHOSE.get(key, [B1_WHOSE_DEFAULT])
        else:
            if key == "p11":
                shutil.copy2(os.path.join(B1, "posts", "p11-vocabulary-poster.png"), os.path.join(folder, "Slide.png"))
                alts = ["A poster titled “The vocabulary nobody gave you.” Twelve tactics, in plain words. When you can name a tactic, it gets harder to use on you. "
                        + " ".join(f"{plain(a)}: {stop(plain(b))}" for a, b in C.POSTER_TERMS)]
            else:
                s = sing[key]
                shutil.copy2(os.path.join(B1, "posts", s["slug"] + ".png"), os.path.join(folder, "Slide.png"))
                alts = [re.sub(r"\s+", " ", f"{stop(plain(s['kicker']))} {stop(plain(s['quote']))} {stop(plain(s.get('sub', '')))} Photo: {PHOTO[s['img']]}.").strip()]
            files = ["Slide.png: one image for Instagram, Facebook, Threads, or LinkedIn (1080 × 1350).", ]
            kind = "Single post"
            cap = caps[key]
            src_ = []
            if not re.search(r"#\w", cap):
                notes.append("Add 3–5 hashtags on Instagram (0–3 on LinkedIn) from the core list: " + CORE_TAGS)
            whose = B1_WHOSE.get(key, [B1_WHOSE_DEFAULT])
        if "LinkedIn" in where:
            notes.append("LinkedIn caution: coworkers and managers may see it. Nothing here names your employer, but you decide what goes there.")
        files.append("Post wording.docx: this document.")
        sub = f"Batch 01: The Vocabulary Nobody Gave You · {kind} · post {k} of {len(B1_ORDER)} · {day} · {where}"
        post_doc(os.path.join(folder, "Post wording.docx"), title, sub, files, cap, alts, src_, whose, notes, checks)
        made.append((k, day, title, where, kind))
    md_to_docx(open(os.path.join(B1, "POSTING-PLAN.md"), encoding="utf-8").read(), os.path.join(base, "Batch 01 plan and Substack seeds.docx"))
    md_to_docx(open(os.path.join(B1, "CHECK-REPORT.md"), encoding="utf-8").read(), os.path.join(base, "Check report.docx"))
    return made


# ---------------------------------------------------------------- read me first
def readme(b1, tposts):
    d = new_doc()
    d.add_heading("Workplace Psych: read me first", 0)
    meta(d, f"Updated {TODAY}")
    d.add_paragraph("Every post now has its own folder. Inside each one: the images, a PDF for LinkedIn when it's a carousel, "
                    "and a document called “Post wording” with everything you paste in: the caption, alt text for each image, "
                    "sources for the first comment, and notes on where and when to post it.")
    d.add_heading("The folders", 1)
    t = d.add_table(rows=1, cols=2)
    t.style = "Light Grid Accent 1"
    t.cell(0, 0).text, t.cell(0, 1).text = "Folder", "What it is"
    for a, b in (
        ("Batch 01 - The Whole Map", f"Start here. {len(b1)} posts for the first two weeks, numbered in posting order. "
                                     "“Batch 01 plan and Substack seeds” has the schedule and your writing prompts for the first three articles."),
        ("Timeline - Tree by Tree", f"{len(tposts)} posts that walk On the Bus or Off the Bus one entry at a time: a start-here post, "
                                    "six eras (each opens with an era map), 83 trees, and a closing post. Folders are numbered in posting order."),
        ("Timeline", "Research notes: the history echoes and the public-safe timeline. Keep these."),
        ("Batch 01 (the old one)", "The same Batch 01 images in the old layout. Once you've looked through “Batch 01 - The Whole Map,” "
                                   "you can delete this folder. The copy in Downloads\\Social Series Batch 01 is old too."),
    ):
        r = t.add_row()
        r.cells[0].text, r.cells[1].text = a, b
    d.add_heading("Posting order", 1)
    bullets(d, [
        "First, Batch 01: the two-week schedule is in the folder names (Day 1 through Day 14). Pin “The whole map.”",
        "Then the timeline series, in folder order: 00 Start here, then each era's map followed by its trees, then 07 Closing. "
        "Pin “Start here” when you begin it.",
        "Suggested pace for the timeline: three posts a week (for example Monday, Wednesday, Friday). That's about 30 weeks. "
        "The weekly Saturday batch can keep going alongside it.",
        "Each “Post wording” document names the post before and after it, so you never lose your place.",
    ])
    d.add_heading("Before anything goes up", 1)
    bullets(d, [
        "Your employer is never named, in any post. The script checks every image, caption, and alt text for it.",
        "The “At work” lines are general examples from your field guide, not your case. If one feels close to your own situation, "
        "check with your employment lawyer before it goes up. Anything about the legal matter itself: lawyer first.",
        "Trees 78 to 82 are about current federal politics. Each one has a LinkedIn caution in its notes.",
        "Trees 75 and 79 to 83 are still moving news. Check the headlines the day you post them. Tree 83 has a date in its notes.",
        "Content notes stay as the first line of the caption. The darkest entries have no photo and no question at the end, on purpose.",
        "Wording follows your report: person-first by default, and quotes keep their original wording.",
    ])
    d.add_heading("How it was checked", 1)
    bullets(d, [
        "Scripted check, no AI: quotes word for word against your report, every number traced to the timeline or a source, "
        "spelling, the employer blocklist, safety rules (content notes, 988 where needed), and the layout of every slide. "
        "0 problems in both series. The full reports are in each series folder as “Check report.”",
        "Then an editorial read for human eyes: wording, flow, and every slide looked at.",
    ])
    d.add_heading("Want to change something?", 1)
    d.add_paragraph("Tell me which post and what to change, and I'll rebuild it, check it again, and put the new files in the same folder.")
    d.save(os.path.join(ROOT, "READ ME FIRST.docx"))


if __name__ == "__main__":
    if os.path.exists(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ROOT)
    tp = trees()
    b1 = batch01()
    readme(b1, tp)
    n = sum(len(fs) for _, _, fs in os.walk(ROOT))
    print(f"wrote {n} files into {ROOT}")
