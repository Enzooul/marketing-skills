// Renders modelo.html for one client folder, frame by frame, and encodes it with ffmpeg.
// Usage: node render.js <client folder> stills <A|B> <t1,t2,...>
//        node render.js <client folder> video <A|B>
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

(async () => {
  const [client, mode, version = 'A', list] = process.argv.slice(2);
  const clientDir = path.resolve(client);
  const out = path.join(clientDir, 'out');
  fs.mkdirSync(out, { recursive: true });
  const rel = path.relative(__dirname, clientDir);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.error('erro na página:', e.message));
  await page.goto('file://' + path.join(__dirname, 'modelo.html') + `?p=${encodeURIComponent(rel)}&v=${version}`);
  await page.evaluate(() => window.READY);
  const meta = await page.evaluate(() => window.META);
  const canvas = await page.$('canvas');

  if (mode === 'stills') {
    for (const t of list.split(',').map(Number)) {
      await page.evaluate(t => window.render(t), t);
      await canvas.screenshot({ path: path.join(out, `still-${version}-${t.toFixed(2)}.png`) });
    }
  } else {
    const total = Math.round(meta.DURATION * meta.FPS);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(meta.FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'slow', '-crf', '18', '-movflags', '+faststart', path.join(out, `video-${version}-sem-som.mp4`)]);
    ff.stderr.pipe(process.stderr);
    for (let i = 0; i < total; i++) {
      await page.evaluate(t => window.render(t), i / meta.FPS);
      const buf = await canvas.screenshot({ type: 'jpeg', quality: 95 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
