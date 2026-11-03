# The Vocabulary Nobody Gave You: social series

Social posts that drive readers to the Substack series. Never name the employer.

- `batch-NN/`: the source files for each weekly batch: carousels (PDF for LinkedIn, PNG slides for Instagram), single posts (PNG), and `POSTING-PLAN.md` (captions, schedule, Substack seeds, sources). `package/` turns these into one folder per post for Ohnnie.
- `build/`: the generator. Edit `content.py`, then run:

```
python3 series/build/build.py series/build/fonts /tmp/html
node series/build/render.js /tmp/html series/batch-NN
```

- `img/`: Ohnnie's photos. Reuse freely.
- `topics-log.md`: topics already covered, so each week picks something new.
- `timeline/history-echoes.md`: maps series terms to entries in the history timeline [On the Bus or Off the Bus](https://claude.ai/artifact/U8XhxLs1m2Xs8o4ydrXA8k). Each weekly batch includes one history echo that links back to the timeline.
- `timeline/public-safe-timeline.md`: Ohnnie's work timeline, de-identified, with each beat marked pattern-safe or counsel first. Don't post a counsel-first beat until an employment lawyer has cleared it.
- `build/check.py`: the proof and fact-check, run on every batch before delivery. It uses no AI. It scans for employer terms, makes sure every number on a slide traces to evidence listed in `build/facts.tsv`, checks spelling (add real words to `build/wordlist.txt`), checks that text doesn't spill off any slide or overlap other text, and checks for the crisis line. It writes `batch-NN/CHECK-REPORT.md`. After it passes, the batch gets an editorial read for flow and design.

```
python3 series/build/check.py /tmp/html series/batch-NN
```

## Timeline, tree by tree

`trees/` turns the [On the Bus or Off the Bus](https://claude.ai/artifact/U8XhxLs1m2Xs8o4ydrXA8k) timeline into 91 posts: a start-here post, an era map for each of the six eras, one two-slide post for each of the 83 entries ("trees"), and a closing post. Slide 1 is the entry itself. Slide 2 ("under the surface") holds Ohnnie's own words from the report, the field-guide tactic or closing commitment it names, and the connected trees.

- `trees/timeline.json`: the timeline's entries, lanes, and eras, copied from the artifact.
- `trees/trees.py`: the per-entry choices (hook line, report quotes, which field-guide term or commitment, connected trees, closing question). The header says whose words are whose.
- `trees/source.py`: reads the report so quotes stay word for word.
- `trees/build_trees.py`, `trees/render_trees.js`: HTML, then PNG slides and a LinkedIn PDF per post.
- `trees/check_trees.py`: the scripted check (no AI). Employer blocklist, quotes against the report, every number traced to the timeline or `facts-trees.tsv`, spelling, safety rules (content notes, no workplace lines next to the darkest history, no photos or questions on the darkest entries, political and still-moving notes), and layout. Writes `CHECK-REPORT.md`.

```
python3 series/trees/build_trees.py /tmp/trees
node series/trees/render_trees.js /tmp/trees/html /tmp/trees/pkg
python3 series/trees/check_trees.py /tmp/trees
```

## Packaging: one folder per post

`package/make_package.py` builds the "Workplace Psych" folder that goes on Ohnnie's PC. Every post gets its own folder with its images, the LinkedIn PDF for carousels, and `Post wording.docx` (caption, alt text per image, sources for the first comment, whose words are whose, posting notes, check results). It also writes `READ ME FIRST.docx`, the Batch 01 plan as a document, and the check reports. `package/verify_package.py` reads every document back and checks the folders.

```
python3 series/package/make_package.py /tmp/trees /tmp/out
python3 series/package/verify_package.py "/tmp/out/Workplace Psych"
```

Weekly batches follow the same layout: `Batch NN - <title>/NN - <day> - <post title>/` with the slides, the PDF, and `Post wording.docx`.
