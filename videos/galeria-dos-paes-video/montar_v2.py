"""Version 2 of the Galeria dos Pães ad, built from the same Mixkit clips as montar.py.

What changed from v1 (see ANALISE.md):
- hook on screen from the first frame, opening on the croissant being torn (motion stops the scroll);
- cuts land on the soundtrack's beat, hard cuts instead of slow dissolves, ~16 s instead of 22 s;
- dropped the dark tattooed-hands shot and the blurry display case with a Danish price sign;
- brand name visible the whole time (top label), key words highlighted, bigger text inside the Reels safe zone;
- warmer colour grade; shorter end card with a direct call to action;
- renders 9:16 (Reels/Stories) and 4:5 (feed and feed ads).

Usage: python montar_v2.py   (needs the clips in clipes/, see FONTES.md)
"""
import pathlib
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import montar  # reuses the soundtrack generator

DIR = pathlib.Path(__file__).parent
FPS = 30
BEAT = 60 / 76  # the soundtrack runs at 76 bpm; every cut lands on a beat
FONTS = pathlib.Path('/usr/share/fonts/opentype/inter')
CREAM, INK, ACCENT, SOFT, GOLD = (246, 239, 228), (42, 29, 20), (168, 90, 31), (140, 122, 104), (255, 204, 120)
FORMATS = {'reels': (1080, 1920), 'feed': (1080, 1350)}

# (file, start in the source clip, length in beats, horizontal centre of the crop 0..1)
CLIPS = [
    ('croissant-partido', 3.3, 3, 0.30),
    ('forno', 4.3, 2, 0.40),
    ('pao-fatiado', 3.0, 2, 0.50),
    ('doces-assados', 4.0, 2, 0.48),
    ('cafe-maquina', 4.0, 2, 0.50),
    ('latte-art', 18.0, 2, 0.58),
    ('cafe-da-manha', 5.0, 3, 0.38),
]
END_BEATS = 4
XF = 0.3  # only the end card dissolves in
# text blocks: (first clip, last clip, lines); words between * are highlighted
TEXTS = [
    (0, 0, ['Sentiu o cheirinho', 'de *pão quente*?']),
    (1, 2, ['Fresquinho,', '*saindo do forno*.']),
    (3, 3, ['Pães, doces', 'e *delícias*.']),
    (4, 5, ['E um *cafezinho*', 'pra acompanhar.']),
    (6, 6, ['Seu café da manhã', '*começa aqui*.']),
]
LABEL = 'GALERIA DOS PÃES'
CTA = 'Passa aqui hoje'
ADDRESS = 'Av. Praia de Itapoan · Vilas do Atlântico'
FOOTER = 'Modelo de demonstração · imagens ilustrativas (Mixkit)'


def run(*cmd):
    subprocess.run(cmd, check=True)


def font(name, size):
    return ImageFont.truetype(str(FONTS / f'{name}.otf'), size)


def frames(beats):
    return round(beats * BEAT * FPS)


def timeline():
    """Start frame of each clip and the frame where the clips end, without rounding drift."""
    starts, b = [], 0
    for clip in CLIPS:
        starts.append(frames(b))
        b += clip[2]
    return starts, frames(b), frames(b + END_BEATS)


def prepare_clips(out, W, H):
    starts, clips_end, _ = timeline()
    ends = starts[1:] + [clips_end]
    for i, (name, start, _, cx) in enumerate(CLIPS):
        src = DIR / 'clipes' / f'{name}.mp4'
        w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                                        '-of', 'csv=p=0', str(src)], capture_output=True, text=True).stdout.strip().split(','))
        scale = max(W / w, H / h)
        sw, sh = round(w * scale / 2) * 2, round(h * scale / 2) * 2
        x = int(min(max(cx * sw - W / 2, 0), sw - W))
        y = int((sh - H) / 2)
        n = ends[i] - starts[i] + (round(XF * FPS) if i == len(CLIPS) - 1 else 0)  # last clip covers the dissolve
        run('ffmpeg', '-y', '-loglevel', 'error', '-ss', str(start), '-i', str(src),
            '-vf', f'fps={FPS},scale={sw}:{sh}:flags=lanczos,crop={W}:{H}:{x}:{y},setsar=1,'
                   'eq=saturation=1.12:contrast=1.05,colorbalance=rm=0.04:bm=-0.04',
            '-frames:v', str(n), '-an', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-pix_fmt', 'yuv420p',
            str(out / f'seg{i:02d}.mp4'))


def text_image(lines, W, max_width):
    """Transparent PNG: white lines, highlighted words in gold, soft shadow. Shrinks to fit max_width."""
    parse = [[(part, k % 2 == 1) for k, part in enumerate(line.split('*')) if part] for line in lines]
    size = 112
    while True:
        f = font('InterDisplay-Bold', size)
        probe = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        if max(sum(probe.textlength(p, font=f) for p, _ in line) for line in parse) <= max_width or size <= 60:
            break
        size -= 4
    lh = int(size * 1.16)
    img = Image.new('RGBA', (W, 60 + lh * len(lines) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = 40
    for line in parse:
        x = (W - sum(d.textlength(p, font=f) for p, _ in line)) / 2
        for part, hi in line:
            d.text((x, y), part, font=f, fill=GOLD + (255,) if hi else (255, 255, 255, 255))
            x += d.textlength(part, font=f)
        y += lh
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow.putalpha(img.getchannel('A').point(lambda a: int(a * 0.6)).filter(ImageFilter.GaussianBlur(12)))
    return Image.alpha_composite(shadow, img)


def spaced(d, text, fnt, spacing):
    """Width of letter-spaced text, and a function that draws it centred."""
    widths = [d.textlength(c, font=fnt) for c in text]
    total = sum(widths) + spacing * (len(text) - 1)

    def draw(x, y, fill):
        for c, cw in zip(text, widths):
            d.text((x, y), c, font=fnt, fill=fill)
            x += cw + spacing
    return total, draw


def label_image(W, H):
    """Brand pill shown at the top while the clips play (below the Reels header in 9:16)."""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font('Inter-SemiBold', 30)
    tw, draw = spaced(d, LABEL, f, 6)
    top = 290 if H > W * 1.6 else 60
    d.rounded_rectangle(((W - tw) / 2 - 34, top, (W + tw) / 2 + 34, top + 66), radius=33, fill=(30, 18, 10, 150))
    draw((W - tw) / 2, top + 14, (255, 255, 255, 240))
    return img


def end_card(out, W, H):
    img = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(img)
    c = H / 2 - 120 if H > W * 1.6 else H / 2 - 150

    def center(text, y, fnt, fill):
        d.text(((W - d.textlength(text, font=fnt)) / 2, y), text, font=fnt, fill=fill)

    tw, draw = spaced(d, LABEL, font('InterDisplay-SemiBold', 70), 9)
    draw((W - tw) / 2, c - 130, INK)
    tw, draw = spaced(d, 'PADARIA & DELICATESSEN', font('Inter-Medium', 28), 9)
    draw((W - tw) / 2, c, INK)
    center('Pães · doces · café da manhã', c + 70, font('Inter-Regular', 38), SOFT)
    f = font('Inter-SemiBold', 54)
    tw = d.textlength(CTA, font=f)
    d.rounded_rectangle(((W - tw) / 2 - 70, c + 190, (W + tw) / 2 + 70, c + 312), radius=61, fill=ACCENT)
    center(CTA, c + 216, f, (255, 255, 255))
    f = font('Inter-Medium', 38)
    tw = d.textlength(ADDRESS, font=f)
    x, y = (W - tw - 44) / 2, c + 372
    d.ellipse((x + 6, y + 4, x + 30, y + 28), fill=ACCENT)  # map pin
    d.polygon([(x + 8, y + 20), (x + 28, y + 20), (x + 18, y + 42)], fill=ACCENT)
    d.ellipse((x + 13, y + 11, x + 23, y + 21), fill=CREAM)
    d.text((x + 44, y), ADDRESS, font=f, fill=INK)
    center(FOOTER, H - (200 if H > W * 1.6 else 70), font('Inter-Regular', 22), SOFT)
    img.save(out / 'endcard.png')
    _, clips_end, total = timeline()
    n = total - clips_end + round(XF * FPS)
    run('ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', str(out / 'endcard.png'),
        '-vf', f'fps={FPS},zoompan=z=\'1+0.0005*on\':d=1:s={W}x{H}:fps={FPS},setsar=1', '-frames:v', str(n),
        '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', str(out / 'segend.mp4'))


def gradient(out, W, H):
    """Darkens the lower part so white text stays readable on any clip."""
    ramp = np.clip((np.arange(H) - H * 0.42) / (H * 0.4), 0, 1) * 165
    img = Image.new('RGBA', (W, H), (20, 12, 6, 0))
    img.putalpha(Image.fromarray(np.repeat(ramp[:, None], W, axis=1).astype(np.uint8)))
    img.save(out / 'gradiente.png')


def assemble(out, W, H):
    starts, clips_end, total_f = timeline()
    total, clips_t = total_f / FPS, clips_end / FPS
    n = len(CLIPS)
    inputs = []
    for i in range(n):
        inputs += ['-i', str(out / f'seg{i:02d}.mp4')]
    inputs += ['-i', str(out / 'segend.mp4')]
    graph = [''.join(f'[{i}:v]' for i in range(n)) + f'concat=n={n}:v=1,settb=1/{FPS}[clips]',
             f'[{n}:v]settb=1/{FPS}[end]',
             f'[clips][end]xfade=transition=fade:duration={XF}:offset={clips_t:.3f}[base]']
    k0 = n + 1
    inputs += ['-loop', '1', '-t', f'{total:.3f}', '-i', str(out / 'gradiente.png')]
    inputs += ['-loop', '1', '-t', f'{total:.3f}', '-i', str(out / 'rotulo.png')]
    graph.append(f'[{k0}:v]format=rgba,fade=out:st={clips_t:.3f}:d={XF}:alpha=1[grad]')
    graph.append(f'[{k0 + 1}:v]format=rgba,fade=out:st={clips_t:.3f}:d={XF}:alpha=1[lab]')
    graph.append('[base][grad]overlay=0:0[g0]')
    graph.append('[g0][lab]overlay=0:0[g1]')
    prev = '[g1]'
    ends = starts[1:] + [clips_end]
    text_y = int(H * 0.47) if H > W * 1.6 else int(H * 0.60)  # 9:16: clear of the Reels ad CTA and caption
    for k, (a, b, lines) in enumerate(TEXTS):
        png = out / f'texto{k}.png'
        text_image(lines, W, W - 180).save(png)
        t0, t1 = starts[a] / FPS, ends[b] / FPS
        idx = k0 + 2 + k
        inputs += ['-loop', '1', '-t', f'{total:.3f}', '-i', str(png)]
        if k == 0:  # the hook is on screen from the very first frame
            graph.append(f'[{idx}:v]format=rgba[t{k}]')
            y = str(text_y)
        else:
            graph.append(f'[{idx}:v]format=rgba,fade=in:st={t0:.3f}:d=0.18:alpha=1[t{k}]')
            y = f"{text_y}+18*(1-min(1,max(0,(t-{t0:.3f})/0.3)))"
        graph.append(f"{prev}[t{k}]overlay=x=0:y='{y}':enable='between(t,{t0:.3f},{t1 - 0.001:.3f})'[o{k}]")
        prev = f'[o{k}]'
    graph.append(f'{prev}trim=duration={total:.3f},format=yuv420p[v]')
    run('ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(graph), '-map', '[v]',
        '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-r', str(FPS), str(out / 'video-sem-som.mp4'))
    return total


def main():
    for name, (W, H) in FORMATS.items():
        out = DIR / 'out' / f'v2-{name}'
        out.mkdir(parents=True, exist_ok=True)
        prepare_clips(out, W, H)
        end_card(out, W, H)
        gradient(out, W, H)
        label_image(W, H).save(out / 'rotulo.png')
        total = assemble(out, W, H)
        montar.OUT = out
        montar.music(total)
        final = DIR / f'galeria-dos-paes-v2-{name}.mp4'
        run('ffmpeg', '-y', '-loglevel', 'error', '-i', str(out / 'video-sem-som.mp4'), '-i', str(out / 'trilha.wav'), '-c:v', 'copy',
            '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-shortest',
            '-movflags', '+faststart', str(final))
        run('ffmpeg', '-y', '-loglevel', 'error', '-ss', '1.0', '-i', str(final), '-frames:v', '1', '-q:v', '2',
            str(DIR / f'capa-v2-{name}.jpg'))
        print(f'pronto: {final} ({total:.1f}s)')


if __name__ == '__main__':
    main()
