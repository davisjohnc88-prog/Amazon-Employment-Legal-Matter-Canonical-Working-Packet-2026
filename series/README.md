# The Vocabulary Nobody Gave You: social series

Social posts that drive readers to the Substack series. Never name the employer.

- `batch-NN/`: one folder per weekly batch, with carousels (PDF for LinkedIn, PNG slides for Instagram), single posts (PNG), and `POSTING-PLAN.md` (captions, schedule, Substack seeds, sources).
- `build/`: the generator. Edit `content.py`, then run:

```
python3 series/build/build.py series/build/fonts /tmp/html
node series/build/render.js /tmp/html series/batch-NN
```

- `img/`: Ohnnie's photos. Reuse freely.
- `topics-log.md`: topics already covered, so each week picks something new.
- `timeline/history-echoes.md`: maps series terms to entries in the history timeline [On the Bus or Off the Bus](https://claude.ai/artifact/U8XhxLs1m2Xs8o4ydrXA8k). Each weekly batch includes one history echo that links back to the timeline.
- `timeline/public-safe-timeline.md`: Ohnnie's work timeline, de-identified, with each beat marked pattern-safe or counsel first. Don't post a counsel-first beat until an employment lawyer has cleared it.
