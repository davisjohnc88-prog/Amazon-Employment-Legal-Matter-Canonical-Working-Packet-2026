# Packs the standalone LinkedIn post into one folder (and a zip): the PDF, the slide images,
# "Post wording.docx", and the check report. No AI involved.
# Usage: python3 package_linkedin.py <render_dir> <out_dir>
#   render_dir = the folder render.js wrote (carousels/<slug>/slide-NN.png and carousels/<slug>.pdf)
#   out_dir    = where the post folder and its zip get written
import datetime, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SERIES = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SERIES, "package"))
os.environ.setdefault("SERIES_CONTENT", os.path.join(HERE, "content.py"))
sys.path.insert(0, os.path.join(SERIES, "build"))
from build_content import load_content
import make_package as M

C = load_content()
RENDER, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
NAME = "LinkedIn - The playbook was handed down"
TODAY = datetime.date.today().strftime("%B %-d, %Y")


def section(md, head):
    m = re.search(rf"^## {re.escape(head)}\n(.*?)(?=^## |\Z)", md, re.M | re.S)
    return m.group(1) if m else ""


def quoted(body):
    return re.sub(r"\n{3,}", "\n\n", "\n".join(l[1:].strip() for l in body.splitlines() if l.startswith(">"))).strip()


def bullets(body):
    return [re.sub(r"^- ", "", l).replace("**", "") for l in body.splitlines() if l.startswith("- ")]


plan = open(os.path.join(HERE, "POSTING-PLAN.md"), encoding="utf-8").read()
cap = quoted(section(plan, "Caption"))
first = quoted(section(plan, "First comment")).replace("\n\n", "\n").split("\n")
doc_title = quoted(section(plan, "Document title"))
whose, notes = bullets(section(plan, "Whose words are these")), bullets(section(plan, "Before you post"))
assert cap and first and doc_title and whose and notes
assert len(cap) <= 3000, f"caption is {len(cap)} characters; LinkedIn allows 3,000"

c = C.CAROUSELS[0]
folder = os.path.join(OUT, NAME)
if os.path.exists(folder):
    shutil.rmtree(folder)
os.makedirs(folder)
src = os.path.join(RENDER, "carousels", c["slug"])
pngs = sorted(f for f in os.listdir(src) if f.endswith(".png"))
assert len(pngs) == len(c["slides"])
for f in pngs:
    n = int(re.search(r"\d+", f).group())
    shutil.copy2(os.path.join(src, f), os.path.join(folder, f"Slide {n:02d}.png"))
shutil.copy2(os.path.join(RENDER, "carousels", c["slug"] + ".pdf"), os.path.join(folder, "LinkedIn carousel.pdf"))

report = open(os.path.join(HERE, "CHECK-REPORT.md"), encoding="utf-8").read()
head = re.search(r"\*\*(\d+) fail, (\d+) warn\.\*\*", report)
checks = [f"Scripted check ({TODAY}): {head.group(1)} fail, {head.group(2)} warn. The full report is in this folder as “Check report.”",
          "What the script checked: the employer is never named, every number on a slide traces to a source, spelling, "
          "repeated words, the crisis line, and the layout of every slide.",
          "Also checked by script: every quote and field-guide line on the slides against your report, word for word.",
          "Editorial read for human eyes: done. Every slide looked at, line breaks tidied, caption read out loud."]
files = ["LinkedIn carousel.pdf: upload to LinkedIn as a document post. This is the main file.",
         f"Slide 01.png to Slide {len(pngs):02d}.png: the same slides as images (1080 × 1350), if you'd rather post images or reuse one.",
         "Post wording.docx: this document.",
         "Check report.docx: the scripted proof and fact-check."]
alts = [M.slide_alt(s) for s in c["slides"]]
M.post_doc(os.path.join(folder, "Post wording.docx"), "The playbook was handed down",
           f"The Vocabulary Nobody Gave You · standalone LinkedIn document post · {len(pngs)} slides · the bird's-eye view",
           files, cap, alts, first, whose, notes, checks,
           extra=[("Document title (LinkedIn asks for one when you upload the PDF)", [doc_title])], limit=3000)
M.md_to_docx(report, os.path.join(folder, "Check report.docx"))
zp = shutil.make_archive(os.path.join(OUT, NAME), "zip", OUT, NAME)
print(f"wrote {len(os.listdir(folder))} files into {folder}\nzip: {zp} ({os.path.getsize(zp) // 1024:,} KB)\ncaption: {len(cap):,} characters")
