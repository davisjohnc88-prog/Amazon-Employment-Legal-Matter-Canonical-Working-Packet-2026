// Renders each built HTML page to PNG slides and, for carousels, a PDF.
// Usage: node render.js <html_dir> <out_dir>
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [htmlDir, outDir] = process.argv.slice(2);
const manifest = JSON.parse(fs.readFileSync(path.join(htmlDir, 'manifest.json')));

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  for (const m of manifest) {
    await page.goto('file://' + m.html, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const dir = path.join(outDir, m.kind === 'carousel' ? 'carousels' : 'posts');
    fs.mkdirSync(dir, { recursive: true });
    const slides = await page.$$('section.slide');
    for (let i = 0; i < slides.length; i++) {
      const name = m.kind === 'carousel'
        ? path.join(dir, m.slug, `slide-${String(i + 1).padStart(2, '0')}.png`)
        : path.join(dir, `${m.slug}.png`);
      fs.mkdirSync(path.dirname(name), { recursive: true });
      await slides[i].screenshot({ path: name });
    }
    if (m.kind === 'carousel') {
      await page.pdf({ path: path.join(dir, `${m.slug}.pdf`), width: '1080px', height: '1350px', printBackground: true });
    }
    console.log('rendered', m.slug);
  }
  await browser.close();
})();
