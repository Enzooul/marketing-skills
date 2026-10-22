// Renders reel.html frame by frame and encodes it with ffmpeg.
// Usage: node render.js stills <t1,t2,...>   |   node render.js video
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const dir = __dirname;
const out = path.join(dir, 'out');

(async () => {
  const [mode, list] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(dir, 'reel.html'));
  await page.evaluate(() => document.fonts.ready);
  const meta = await page.evaluate(() => window.META);
  const canvas = await page.$('canvas');

  if (mode === 'stills') {
    for (const t of list.split(',').map(Number)) {
      await page.evaluate(t => window.render(t), t);
      await canvas.screenshot({ path: path.join(out, `still-${t.toFixed(2)}.png`) });
    }
  } else {
    fs.writeFileSync(path.join(out, 'events.json'), JSON.stringify(await page.evaluate(() => window.EVENTS), null, 1));
    const total = Math.round(meta.DURATION * meta.FPS);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(meta.FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'slow', '-crf', '18', '-movflags', '+faststart', path.join(out, 'video-sem-som.mp4')]);
    ff.stderr.pipe(process.stderr);
    for (let i = 0; i < total; i++) {
      await page.evaluate(t => window.render(t), i / meta.FPS);
      const buf = await canvas.screenshot({ type: 'jpeg', quality: 95 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 60 === 0) console.log(`frame ${i}/${total}`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
