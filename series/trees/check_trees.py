# Scripted proof and fact-check for the tree-by-tree series. No AI involved: every rule is code.
# Usage: python3 check_trees.py <build_dir>      (the folder build_trees.py wrote: posts.json + html/)
# Writes <build_dir>/CHECK-REPORT.md and exits 1 if anything fails.
import html as H, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from source import BODY, norm, in_report, FIELD_GUIDE, COMMITMENTS, timeline
from trees import TREES

OUT = os.path.abspath(sys.argv[1])
HTML_DIR = os.path.join(OUT, "html")
posts = json.load(open(os.path.join(OUT, "posts.json")))
E = timeline()["E"]
ERA_SPAN = {e["id"]: e["span"] for e in timeline()["ERAS"]}
results = []


def add(level, check, msg):
    results.append((level, check, msg))


def card_text(slug):
    s = open(os.path.join(HTML_DIR, slug + ".html"), encoding="utf-8").read()
    s = re.sub(r"<style>.*?</style>|<script>.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"</?(em|i)>", "", s)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


texts = {p["slug"]: dict(caption=p["caption"], alt=" ".join(p["alt"]), card=card_text(p["slug"]),
                         notes=" ".join(p["notes"] + p["whose"])) for p in posts}

# 1. Never name the employer (slides, captions, alt text, notes)
block = [r"\bamazon\b", r"\baws\b", r"whole foods", r"wow project", r"fulfil+ment cent(er|re)", r"\bprime day\b", r"\bpeak season\b"]
priv = "/mnt/project-files/series/private-blocklist.txt"
if os.path.exists(priv):
    block += [re.escape(l.strip()) for l in open(priv) if l.strip() and not l.startswith("#")]
for slug, t in texts.items():
    for part, s in t.items():
        for b in block:
            m = re.search(b, s, re.I)
            if m:
                add("FAIL", "never name the employer", f'{slug} {part}: "{m.group()}"')

# 2. Quotes are the report's own words, letter for letter (quote marks and citations aside)
cited = re.sub(r" \([^()]*\)(?=[.,;:])", "", BODY)
nq = 0
for n, t in TREES.items():
    for q in t.get("q", []):
        nq += 1
        if not (in_report(q) or norm(q) in cited):
            add("FAIL", "quote not in report", f"tree {n}: {q[:70]}")
    if t.get("term") and t["term"] not in FIELD_GUIDE:
        add("FAIL", "field guide", f"tree {n}: no field guide term {t['term']!r}")
    if t.get("commit") and norm(COMMITMENTS[t["commit"]]["text"]) not in BODY:
        add("FAIL", "commitment", f"tree {n}: commitment text not found in the report")
for k, v in FIELD_GUIDE.items():
    for col in ("short", "work", "hist"):
        if norm(v[col]) not in norm(open(os.environ.get("ESSAY", "/mnt/project-files/notes/factcheck/essay-draft-2026-10-08.md")).read().replace("*", "")):
            add("FAIL", "field guide", f"{v['term']}: {col} drifted from the report")

# 3. Every number traces to the timeline entry itself, a connected entry, or facts-trees.tsv / facts.tsv evidence
facts = {}
for fn in (os.path.join(HERE, "facts-trees.tsv"), os.path.join(HERE, "..", "build", "facts.tsv")):
    base = os.path.dirname(fn)
    for line in open(fn, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        tok, f, needle = line.rstrip("\n").split("\t")
        if f == "-":
            continue
        path = f if f.startswith("/") else os.path.join(base, f)
        if not os.path.exists(path) or needle not in open(path, encoding="utf-8").read():
            add("FAIL", "evidence", f"{os.path.basename(fn)}: {tok!r} evidence not found in {f}")
        facts[tok] = f

NUM = re.compile(r"\d[\d,.]*\d|\d")


def nums(s):
    s = re.sub(r"https?://\S+", "", s)
    s = re.sub(r"#\w+", "", s)
    s = re.sub(r"\b(?:trees?|eras?|slide)\s+\d+(?:\s*(?:of|–|-)\s*\d+)?", "", s, flags=re.I)
    return {m.group().rstrip(".,") for m in NUM.finditer(s)}


def entry_nums(m):
    e = E[m - 1]
    return nums(" ".join([e["y"], e.get("sub", ""), e["t"], e["d"]]))


all_tl = set().union(*(entry_nums(m) for m in range(1, len(E) + 1)))
for p in posts:
    allowed = set(p.get("numbers_ok", [])) | set(facts)
    if p["kind"] == "tree":
        allowed |= entry_nums(p["n"])
        for m in p["links"]:
            allowed |= nums(E[m - 1]["y"] + " " + E[m - 1].get("sub", "") + " " + E[m - 1]["t"])
        allowed |= nums(ERA_SPAN[p["era"]])
    elif p["kind"] == "era":
        for m in p["trees"]:
            allowed |= entry_nums(m)
        allowed |= nums(" ".join(x for x in p["title"].split()))
        allowed |= {"1601", "1899", "1900", "1932", "1933", "1945", "1946", "1979", "1980", "2012", "2013", "2026"}
    else:
        allowed |= all_tl
    t = texts[p["slug"]]
    for part in ("caption", "alt", "card"):
        for tok in sorted(nums(t[part]) - allowed):
            add("FAIL", "unsourced number", f'{p["slug"]} {part}: "{tok}"')

# 4. Spelling (names and proper nouns are skipped; they're checked against the timeline by hand)
try:
    from spellchecker import SpellChecker
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyspellchecker"], check=True)
    from spellchecker import SpellChecker
sp = SpellChecker()
ok = set()
for fn in (os.path.join(HERE, "wordlist.txt"), os.path.join(HERE, "..", "build", "wordlist.txt")):
    if os.path.exists(fn):
        ok |= {w.strip().lower() for w in open(fn) if w.strip()}
seen = set()
for slug, t in texts.items():
    for part in ("caption", "card", "alt"):
        for w in re.findall(r"[^\W\d_][^\W\d_'’]*(?:['’][^\W\d_]+)?", t[part]):
            lw = w.lower().replace("’", "'")
            if lw.endswith("'s"):
                lw = lw[:-2]
            if len(lw) < 3 or lw in ok or (w[0].isupper()):
                continue
            if sp.unknown([lw]) and (lw not in seen):
                seen.add(lw)
                add("FAIL", "spelling", f'{slug} {part}: "{w}"')
        for m in re.finditer(r"\b(\w+) \1\b", t[part], re.I):
            if m.group(1).lower() not in ("that", "had"):
                add("FAIL", "repeated word", f'{slug} {part}: "{m.group()}"')
        if "  " in t[part].replace("\n\n", "\n"):
            add("WARN", "double space", f"{slug} {part}")

# 5. Safety and structure rules for this series
for p in posts:
    slug, cap = p["slug"], p["caption"]
    if len(cap) > 2200:
        add("FAIL", "caption length", f"{slug}: {len(cap)} characters; Instagram allows 2,200")
    tags = re.findall(r"#\w+", cap)
    if len(tags) != len(set(tags)) or len(tags) > 8:
        add("FAIL", "hashtags", f"{slug}: {len(tags)} hashtags or duplicates")
    if re.search(r"crisis|suicid", cap + texts[slug]["card"], re.I) and "988" not in cap:
        add("FAIL", "safety", f"{slug}: mentions crisis without the 988 line")
    if p["kind"] != "tree":
        continue
    n, e, box = p["n"], E[p["n"] - 1], p.get("box") or {}
    harsh = e["lane"] in ("cut", "kill") or e.get("dark") or e["era"] == "killing"
    if harsh and not p.get("cn") and e["lane"] != "speak" and e["lane"] != "measure":
        add("FAIL", "content note", f"{slug}: {e['lane']} entry has no content note")
    if (e["lane"] in ("cut", "kill") or e.get("dark")) and not cap.startswith("Content note"):
        add("FAIL", "content note", f"{slug}: caption doesn't open with the content note")
    if box.get("work") and harsh:
        add("FAIL", "no workplace line here", f"{slug}: a workplace line on a {e['lane']}/{e['era']} entry")
    if box.get("work"):
        for m in p["links"]:
            x = E[m - 1]
            if x.get("dark") or x["lane"] == "kill" or (x["era"] == "killing" and x["lane"] != "measure"):
                add("FAIL", "pattern, not equivalence", f"{slug}: workplace line next to a link to tree {m}")
    if e.get("dark") and (p.get("photo") or TREES[n].get("ask") and TREES[n]["ask"] in cap):
        add("FAIL", "dark entry", f"{slug}: dark entries carry no photo and no engagement question")
    if e["era"] == "present" and n >= 78 and n <= 82 and not any("federal" in x for x in p["notes"]):
        add("FAIL", "posting note", f"{slug}: present-day political entry without the LinkedIn caution")
    if TREES[n].get("fresh") and not any("still moving" in x for x in p["notes"]):
        add("FAIL", "posting note", f"{slug}: fresh entry without the check-the-news note")
    if not (TREES[n].get("q") or box):
        add("WARN", "structure", f"{slug}: slide 2 has neither a quote nor a Name it box")
    if n in p["links"]:
        add("FAIL", "structure", f"{slug}: links to itself")

# 6. Layout: text that spills, clips, or collides; and text the auto-fit had to shrink a lot
r = subprocess.run(["node", os.path.join(HERE, "..", "build", "check-layout.js"), HTML_DIR], capture_output=True, text=True)
if r.returncode != 0:
    add("WARN", "layout", "layout check didn't run: " + r.stderr[-300:])
else:
    for prob in json.loads(r.stdout):
        add("FAIL", "layout", prob)
sc = os.path.join(HTML_DIR, "scales.json")
if os.path.exists(sc):
    for slug, ss in json.load(open(sc)).items():
        for i, s in enumerate(ss):
            if s < 0.75:
                add("WARN", "small text", f"{slug} slide {i + 1}: text shrunk to {int(s * 100)}% to fit")

order = {"FAIL": 0, "WARN": 1}
results.sort(key=lambda x: order[x[0]])
fails = sum(1 for x in results if x[0] == "FAIL")
warns = len(results) - fails
out = ["# Check report: On the Bus or Off the Bus, tree by tree", "",
       f"**{fails} fail, {warns} warn.** Checked {len(posts)} posts ({sum(p['slides'] for p in posts)} slides): "
       f"{nq} report quotes, {len(FIELD_GUIDE)} field guide terms, every number against the timeline and evidence files, "
       "the employer blocklist, spelling, safety rules, and the rendered layout.", ""]
out += [f"- **{l}** · {c}: {m}" for l, c, m in results] or ["Everything passed."]
open(os.path.join(OUT, "CHECK-REPORT.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out[:80]))
sys.exit(1 if fails else 0)
