// Finds text that spills off a slide, out of its box, or into the footer.
// Usage: node check-layout.js <html_dir>   Prints a JSON list of problems.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = process.argv[2];
  const man = JSON.parse(fs.readFileSync(path.join(dir, 'manifest.json')));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  const problems = [];
  for (const m of man) {
    await page.goto('file://' + m.html);
    await page.evaluate(() => document.fonts.ready);
    const found = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('.slide').forEach((s, i) => {
        const sr = s.getBoundingClientRect();
        const foot = s.querySelector('.foot');
        const fr = foot ? foot.getBoundingClientRect() : null;
        s.querySelectorAll('h1,h2,h3,p,li,.tag,.cn,.yr,.kick,.span,.legend,.who,.def,.q,.s,.sub,.label,.num,.lab,.d,.t,.a,.b,.f,.c,.note,.source,.b1,.b2,.body2,.lede,.small,.mini').forEach(el => {
          if (foot && foot.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.width === 0 || !el.textContent.trim()) return;
          const what = el.textContent.trim().slice(0, 40);
          if (r.bottom > sr.bottom + 1 || r.right > sr.right + 1 || r.left < sr.left - 1 || r.top < sr.top - 1)
            out.push(`slide ${i + 1}: runs off the slide: "${what}"`);
          else if (fr && r.bottom > fr.top + 2 && r.top < fr.bottom)
            out.push(`slide ${i + 1}: overlaps the footer: "${what}"`);
          if (el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow !== 'visible')
            out.push(`slide ${i + 1}: text is clipped: "${what}"`);
        });
        // overlapping text blocks inside .pad (e.g. kicker on top of a title)
        const blocks = [...s.querySelectorAll('.pad > *')].filter(e => e.textContent.trim());
        for (let a = 0; a < blocks.length; a++) for (let b = a + 1; b < blocks.length; b++) {
          const ra = blocks[a].getBoundingClientRect(), rb = blocks[b].getBoundingClientRect();
          const ov = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
          const ox = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left);
          if (ov > 4 && ox > 4 && !blocks[a].classList.contains('source') && !blocks[b].classList.contains('source'))
            out.push(`slide ${i + 1}: "${blocks[a].textContent.trim().slice(0, 25)}" overlaps "${blocks[b].textContent.trim().slice(0, 25)}"`);
        }
      });
      return out;
    });
    found.forEach(p => problems.push(`${m.slug} ${p}`));
  }
  await browser.close();
  console.log(JSON.stringify(problems));
})();
