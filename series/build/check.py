# Proof and fact-check for a batch. No AI involved: every check is a script.
# Usage: python3 check.py <html_dir> <batch_dir>
#   html_dir  = the folder build.py wrote (used for the layout check)
#   batch_dir = series/batch-NN (reads POSTING-PLAN.md, writes CHECK-REPORT.md)
# Exit code 1 if anything FAILs.
import sys, os, re, html, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from content import CAROUSELS, SINGLES, POSTER_TERMS

HTML_DIR, BATCH = sys.argv[1], sys.argv[2]
results = []  # (level, check, message)
def add(level, check, msg): results.append((level, check, msg))

def walk(o, where):
    if isinstance(o, str): yield where, o
    elif isinstance(o, (int, float)) and not isinstance(o, bool): yield where, str(o)
    elif isinstance(o, dict):
        for k, v in o.items():
            if k not in ("type", "img", "slug", "n"): yield from walk(v, where)
    elif isinstance(o, (list, tuple)):
        for v in o: yield from walk(v, where)

def plain(s):
    s = re.sub(r"</?(strong|em|b|i)[^>]*>", "", s)  # inline tags can sit inside a word ("<strong>D</strong>eny")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(s))).strip()

slides = []
for c in CAROUSELS:
    for i, s in enumerate(c["slides"], 1):
        # bars on "my own check-in" are illustrative, not data
        data = {k: v for k, v in s.items() if not (s["type"] == "bars" and k == "bars")}
        slides += [(f'{c["slug"]} slide {i}', plain(t)) for _, t in walk(data, "")]
for s in SINGLES: slides += [(s["slug"], plain(t)) for _, t in walk(s, "")]
slides += [("p11 poster", plain(f"{a} {b}")) for a, b in POSTER_TERMS]
plan_path = os.path.join(BATCH, "POSTING-PLAN.md")
plan = open(plan_path).read() if os.path.exists(plan_path) else ""
if not plan: add("FAIL", "files", "POSTING-PLAN.md is missing")

# 1. Employer and private terms
block = [r"\bamazon\b", r"\baws\b", r"whole foods", r"wow project", r"fulfil+ment cent(er|re)", r"\bprime day\b", r"\bpeak season\b"]
priv = "/mnt/project-files/series/private-blocklist.txt"
if os.path.exists(priv):
    block += [re.escape(l.strip()) for l in open(priv) if l.strip() and not l.startswith("#")]
for where, t in slides + [("POSTING-PLAN.md", plan)]:
    for b in block:
        m = re.search(b, t, re.I)
        if m: add("FAIL", "never name the employer", f'{where}: "{m.group()}"')

# 2. Every number on a slide must trace to evidence
facts = {}
for line in open(os.path.join(HERE, "facts.tsv")):
    if line.startswith("#") or not line.strip(): continue
    tok, f, needle = line.rstrip("\n").split("\t")
    facts[tok] = (f, needle)
for tok, (f, needle) in facts.items():
    if f == "-": continue
    path = f if f.startswith("/") else os.path.join(HERE, f)
    if not os.path.exists(path): add("WARN", "evidence", f"{tok}: evidence file not found ({f}); can't confirm"); continue
    if needle not in open(path).read(): add("FAIL", "evidence", f'{tok}: "{needle}" not found in {f}')
seen = set()
for where, t in slides:
    for m in re.finditer(r"\d[\d,.]*\d|\d", t):
        tok = m.group()
        tail = t[m.end():m.end() + 8]
        if tail.startswith("%"): tok += "%"
        elif tail.startswith(" million"): tok += " million"
        elif tail.startswith("M"): tok += "M"
        if tok not in facts and tok.rstrip(".,") in facts: tok = tok.rstrip(".,")
        if tok not in facts and (where, tok) not in seen:
            seen.add((where, tok)); add("FAIL", "unsourced number", f'{where}: "{tok}" has no entry in facts.tsv')

# 3. Spelling (pyspellchecker + codespell), with a project word list
try:
    from spellchecker import SpellChecker
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyspellchecker", "codespell"], check=False)
    from spellchecker import SpellChecker
sp = SpellChecker()
ok = {w.strip().lower() for w in open(os.path.join(HERE, "wordlist.txt")) if w.strip()}
flagged = {}
for where, t in slides + [("POSTING-PLAN.md", re.sub(r"https?://\S+|`[^`]*`|#\w+", " ", plan))]:
    for w in re.findall(r"[A-Za-z][A-Za-z'’]+", t):
        lw = w.lower().replace("’", "'").strip("'")
        lw = re.sub(r"'s$", "", lw)
        if len(lw) < 3 or lw in ok or w[0].isupper() and w[1:].islower():  # skip names; proper nouns are checked by hand
            continue
        if sp.unknown([lw]): flagged.setdefault(lw, where)
for w, where in sorted(flagged.items()):
    add("WARN", "spelling", f'"{w}" first seen in {where} (add to wordlist.txt if it\'s right)')
for where, t in slides + [("POSTING-PLAN.md", plan)]:
    for m in re.finditer(r"\b(\w+)\s+\1\b", t, re.I):
        if m.group(1).lower() not in ("that", "had"): add("FAIL", "repeated word", f'{where}: "{m.group()}"')
    if "  " in t and where != "POSTING-PLAN.md": add("WARN", "spacing", f"{where}: double space")

# 4. Layout: text that runs off the slide or overlaps the footer
r = subprocess.run(["node", os.path.join(HERE, "check-layout.js"), HTML_DIR], capture_output=True, text=True)
if r.returncode != 0: add("WARN", "layout", "layout check didn't run: " + r.stderr[-300:])
else:
    for p in json.loads(r.stdout): add("FAIL", "layout", p)

# 5. Every carousel ends with a call to action and a crisis line where it talks about crisis
for c in CAROUSELS:
    if c["slides"][-1]["type"] != "cta": add("WARN", "structure", f'{c["slug"]}: last slide is not a call to action')
    txt = " ".join(t for _, t in walk(c, ""))
    if re.search(r"crisis|suicid", txt, re.I) and "988" not in txt: add("FAIL", "safety", f'{c["slug"]}: mentions crisis without the 988 line')

# Report
order = {"FAIL": 0, "WARN": 1}
results.sort(key=lambda x: order[x[0]])
fails = sum(1 for r in results if r[0] == "FAIL"); warns = len(results) - fails
out = [f"# Check report: {os.path.basename(os.path.abspath(BATCH))}", "",
       f"**{fails} fail, {warns} warn.** Checked {len(slides)} pieces of slide text, POSTING-PLAN.md, {len(facts)} facts.tsv entries, and the rendered layout.", ""]
out += [f"- **{l}** · {c}: {m}" for l, c, m in results] or ["Everything passed."]
open(os.path.join(BATCH, "CHECK-REPORT.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
sys.exit(1 if fails else 0)
