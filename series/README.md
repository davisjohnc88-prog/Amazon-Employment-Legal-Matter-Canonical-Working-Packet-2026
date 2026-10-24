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
