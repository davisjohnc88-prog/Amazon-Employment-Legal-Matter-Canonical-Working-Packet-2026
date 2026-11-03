// Renders every tree-series page into its own post folder: Slide 1.png, Slide 2.png, and a PDF for LinkedIn.
// Usage: node render_trees.js <html_dir> <package_dir> [slug ...]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [htmlDir, outDir, ...only] = process.argv.slice(2);
const manifest = JSON.parse(fs.readFileSync(path.join(htmlDir, 'manifest.json')));

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  const scales = {};
  for (const m of manifest) {
    if (only.length && !only.includes(m.slug)) continue;
    await page.goto('file://' + m.html, { waitUntil: 'load' });
    await page.waitForSelector('body[data-ready="1"]');
    const dir = path.join(outDir, m.folder);
    fs.mkdirSync(dir, { recursive: true });
    const slides = await page.$$('section.slide');
    for (let i = 0; i < slides.length; i++) {
      const name = slides.length === 1 ? 'Slide.png' : `Slide ${i + 1}.png`;
      await slides[i].screenshot({ path: path.join(dir, name) });
    }
    if (slides.length > 1) {
      await page.pdf({ path: path.join(dir, 'LinkedIn carousel.pdf'), width: '1080px', height: '1350px', printBackground: true });
    }
    scales[m.slug] = await page.$$eval('section.slide', ss => ss.map(s => +(s.dataset.scale || 1)));
  }
  await browser.close();
  fs.writeFileSync(path.join(htmlDir, 'scales.json'), JSON.stringify(scales, null, 1));
  console.log('rendered', Object.keys(scales).length, 'posts');
})();
