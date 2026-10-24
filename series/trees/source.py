# Reads John Charles's report so the tree posts can quote it word for word.
# Everything pulled from here is the author's own wording; nothing is paraphrased.
import json, os, re

ESSAY = os.environ.get("ESSAY", "/mnt/project-files/notes/factcheck/essay-draft-2026-10-08.md")
TIMELINE = os.environ.get("TIMELINE_JSON", os.path.join(os.path.dirname(__file__), "timeline.json"))

_text = open(ESSAY, encoding="utf-8").read()


def norm(s):
    """Flatten quote marks, markdown, and spacing so a quote can be matched against the report."""
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)  # [label](url) -> label
    s = s.replace("*", "").replace("_", "")
    for a, b in (("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'"), ("–", "-"), ("—", "-")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


BODY = norm(_text.split("## Threads to pull later")[0])


def in_report(q):
    return norm(q) in BODY


def _field_guide():
    part = _text.split("## Part XV.")[1].split("## Closing")[0]
    rows = {}
    for line in part.splitlines():
        if not line.startswith("|") or line.startswith("| Term") or line.startswith("| ---"):
            continue
        cells = [c.strip().replace("*", "") for c in line.strip().strip("|").split("|")]
        term, plain, hist, work = cells[:4]
        # "(author's term)" style origin notes stay in the doc but not on the card
        origin = re.search(r"\(([^()]*(?:term|usage|idiom|Freyd|Bateson|Leymann|camouflaging)[^()]*(?:\([^()]*\))?[^()]*)\)\s*$", plain)
        short = plain[: origin.start()].strip() if origin else plain
        rows[term.lower()] = dict(term=term, plain=plain, short=short, origin=origin.group(1) if origin else "",
                                  hist=hist, work=work)
    return rows


FIELD_GUIDE = _field_guide()


def _commitments():
    part = _text.split("## Closing: what the history asks of us")[1].split("## Threads to pull later")[0]
    out = {}
    for m in re.finditer(r"\*\*([^*]+)\.\*\* (.+)", part):
        out[m.group(1).lower()] = dict(name=m.group(1), text=m.group(2).strip())
    return out


COMMITMENTS = _commitments()


def first_sentences(s, n=1):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z“\"])", s)
    return " ".join(parts[:n])


def timeline():
    return json.load(open(TIMELINE, encoding="utf-8"))


if __name__ == "__main__":
    print(len(FIELD_GUIDE), "field guide terms;", len(COMMITMENTS), "commitments")
    for k, v in FIELD_GUIDE.items():
        print(f"- {v['term']}: {v['short']}  [{v['origin']}]  AT WORK: {v['work']}")
    for k, v in COMMITMENTS.items():
        print(f"* {v['name']}: {first_sentences(v['text'], 2)}")
