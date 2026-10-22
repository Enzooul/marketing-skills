"""Builds the Galeria dos Pães ad from licensed stock clips (Mixkit Stock Video Free License):
vertical crops, dissolves, text overlays, an end card and a calm electric-piano soundtrack.

Usage: python montar.py   (writes galeria-dos-paes-video.mp4 and capa.jpg next to this file)
"""
import pathlib
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

DIR = pathlib.Path(__file__).parent
OUT = DIR / 'out'
W, H, FPS = 1080, 1920, 30
XF = 0.35  # dissolve length between clips
FONTS = pathlib.Path('/usr/share/fonts/opentype/inter')
CREAM, INK, ACCENT, SOFT = (246, 239, 228), (42, 29, 20), (168, 90, 31), (140, 122, 104)

# (file, start in the source clip, length, horizontal centre of the crop 0..1)
CLIPS = [
    ('doces-assados', 4.0, 2.6, 0.48),
    ('sovando-massa', 7.0, 2.2, 0.5),
    ('forno', 4.5, 2.0, 0.42),
    ('pao-fatiado', 9.0, 2.2, 0.56),
    ('croissant-partido', 4.0, 2.0, 0.35),
    ('compactando-cafe', 3.0, 1.8, 0.22),
    ('cafe-maquina', 4.0, 2.0, 0.5),
    ('latte-art', 18.5, 2.4, 0.5),
    ('cafe-da-manha', 5.0, 2.2, 0.38),
    ('vitrine', 1.5, 2.2, 0.5),
]
END_CARD = 4.0
# text blocks: (first clip, last clip, lines)
TEXTS = [
    (0, 1, ['Sentiu o cheirinho', 'de pão quente?']),
    (2, 4, ['Fresquinho,', 'saindo do forno.']),
    (5, 7, ['E um cafezinho', 'pra acompanhar.']),
    (8, 8, ['Seu café da manhã', 'começa aqui.']),
    (9, 9, ['Galeria dos Pães']),
]


def run(*cmd):
    subprocess.run(cmd, check=True)


def font(name, size):
    return ImageFont.truetype(str(FONTS / f'{name}.otf'), size)


def clip_starts():
    """Start time of each clip in the final timeline (dissolves overlap neighbours by XF)."""
    starts, t = [], 0.0
    for _, _, dur, _ in CLIPS:
        starts.append(t)
        t += dur - XF
    return starts, t + XF  # second value: where the last clip ends


def prepare_clips():
    for i, (name, start, dur, cx) in enumerate(CLIPS):
        src = DIR / 'clipes' / f'{name}.mp4'
        w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                                        '-of', 'csv=p=0', str(src)], capture_output=True, text=True).stdout.strip().split(','))
        scale = max(W / w, H / h)
        sw, sh = round(w * scale / 2) * 2, round(h * scale / 2) * 2
        x = int(min(max(cx * sw - W / 2, 0), sw - W))
        y = int((sh - H) / 2)
        run('ffmpeg', '-y', '-loglevel', 'error', '-ss', str(start), '-t', str(dur), '-i', str(src),
            '-vf', f'scale={sw}:{sh}:flags=lanczos,crop={W}:{H}:{x}:{y},fps={FPS},setsar=1,eq=saturation=1.06:contrast=1.03',
            '-an', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(OUT / f'seg{i:02d}.mp4'))


def text_image(lines, big=104):
    """Transparent PNG with white lines and a soft shadow."""
    img = Image.new('RGBA', (W, 420), (0, 0, 0, 0))
    f = font('InterDisplay-Medium', big)
    d = ImageDraw.Draw(img)
    y = 40
    for line in lines:
        tw = d.textlength(line, font=f)
        d.text(((W - tw) / 2, y), line, font=f, fill=(255, 255, 255, 255))
        y += int(big * 1.18)
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    shadow.putalpha(img.getchannel('A').point(lambda a: int(a * 0.55)).filter(ImageFilter.GaussianBlur(14)))
    return Image.alpha_composite(shadow, img)


def end_card():
    img = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(img)

    def center(text, y, fnt, fill, spacing=0):
        if spacing:  # letter-spaced capitals, drawn glyph by glyph
            widths = [d.textlength(c, font=fnt) for c in text]
            x = (W - sum(widths) - spacing * (len(text) - 1)) / 2
            for c, cw in zip(text, widths):
                d.text((x, y), c, font=fnt, fill=fill)
                x += cw + spacing
        else:
            d.text(((W - d.textlength(text, font=fnt)) / 2, y), text, font=fnt, fill=fill)

    center('GALERIA DOS PÃES', 700, font('InterDisplay-SemiBold', 78), INK, spacing=12)
    center('PADARIA & DELICATESSEN', 830, font('Inter-Medium', 28), INK, spacing=9)
    cta, f = 'Venha nos visitar', font('Inter-Medium', 48)
    tw = d.textlength(cta, font=f)
    d.rounded_rectangle(((W - tw) / 2 - 60, 1010, (W + tw) / 2 + 60, 1118), radius=54, fill=ACCENT)
    center(cta, 1034, f, (255, 255, 255))
    center('Av. Praia de Itapoan · Vilas do Atlântico', 1180, font('Inter-Regular', 38), SOFT)
    center('Imagens ilustrativas · Mixkit', 1720, font('Inter-Regular', 22), SOFT)
    img.save(OUT / 'endcard.png')
    run('ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-t', str(END_CARD), '-i', str(OUT / 'endcard.png'),
        '-vf', f'fps={FPS},zoompan=z=\'1+0.0004*on\':d=1:s={W}x{H}:fps={FPS},setsar=1', '-c:v', 'libx264', '-crf', '16',
        '-pix_fmt', 'yuv420p', str(OUT / 'segend.mp4'))


def gradient():
    """Darkens the lower half so white text stays readable on any clip."""
    a = np.zeros((H, W), np.uint8)
    ramp = np.clip((np.arange(H) - H * 0.45) / (H * 0.4), 0, 1) * 150
    a[:] = ramp[:, None].astype(np.uint8)
    img = Image.new('RGBA', (W, H), (20, 12, 6, 0))
    img.putalpha(Image.fromarray(a))
    img.save(OUT / 'gradiente.png')


def assemble(total):
    segs = [OUT / f'seg{i:02d}.mp4' for i in range(len(CLIPS))] + [OUT / 'segend.mp4']
    durs = [c[2] for c in CLIPS] + [END_CARD]
    starts, last_end = clip_starts()
    inputs = []
    for s in segs:
        inputs += ['-i', str(s)]
    n = len(segs)
    # dissolve chain
    graph, prev, offset = [], '[0:v]', 0.0
    for i in range(1, n):
        offset += durs[i - 1] - XF
        graph.append(f'{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={offset:.3f}[x{i}]')
        prev = f'[x{i}]'
    # gradient over the clips (not the end card)
    inputs += ['-loop', '1', '-t', str(total), '-i', str(OUT / 'gradiente.png')]
    gi = n
    graph.append(f'[{gi}:v]format=rgba,fade=out:st={last_end - XF:.3f}:d={XF}:alpha=1[grad]')
    graph.append(f'{prev}[grad]overlay=0:0[g0]')
    prev = '[g0]'
    # text overlays: fade in and rise, fade out before the next block
    for k, (a, b, lines) in enumerate(TEXTS):
        png = OUT / f'texto{k}.png'
        text_image(lines).save(png)
        t0 = starts[a] + 0.25
        t1 = starts[b] + CLIPS[b][2] - XF - 0.05
        inputs += ['-loop', '1', '-t', str(total), '-i', str(png)]
        idx = n + 1 + k
        graph.append(f'[{idx}:v]format=rgba,fade=in:st={t0:.3f}:d=0.45:alpha=1,fade=out:st={t1 - 0.35:.3f}:d=0.35:alpha=1[t{k}]')
        y = f"1210+30*(1-min(1,max(0,(t-{t0:.3f})/0.6)))"
        graph.append(f"{prev}[t{k}]overlay=x=0:y='{y}':enable='between(t,{t0:.3f},{t1:.3f})'[o{k}]")
        prev = f'[o{k}]'
    graph.append(f'{prev}trim=duration={total:.3f},format=yuv420p[v]')
    run('ffmpeg', '-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(graph), '-map', '[v]',
        '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-r', str(FPS), str(OUT / 'video-sem-som.mp4'))


def music(total):
    """Calm electric piano (Dmaj7 - Bm7 - Gmaj7 - A6) voiced high enough for phone speakers,
    soft bass, a light shaker and a sparse bell melody. No guitar, no drums."""
    sr, bpm = 44100, 76
    rng = np.random.default_rng(5)
    n = int(total * sr)
    m = np.zeros(n)
    beat, bar = 60 / bpm, 4 * 60 / bpm
    chords = [[66, 69, 73, 74, 78], [62, 66, 69, 71, 74], [62, 66, 67, 71, 74], [64, 66, 69, 71, 73]]
    bass = [50, 47, 43, 45]
    hz = lambda midi: 440.0 * 2 ** ((midi - 69) / 12)

    def add(sig, t, gain):
        i = int(t * sr)
        k = max(0, min(len(sig), n - i))
        m[i:i + k] += gain * sig[:k]

    def epiano(f, length):
        t = np.arange(int(length * sr)) / sr
        tone = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.4) \
            + 0.12 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.2) + 0.05 * np.sin(2 * np.pi * 7 * f * t) * np.exp(-t / 0.05)
        return tone * np.minimum(1, t / 0.01) * np.exp(-t / 2.0) * (1 + 0.1 * np.sin(2 * np.pi * 4.2 * t))

    for b in range(int(np.ceil(total / bar))):
        t0 = b * bar
        for when, g in ((0, 0.12), (1.5 * beat, 0.06), (2.5 * beat, 0.08)):
            for k, note in enumerate(chords[b % 4]):
                add(epiano(hz(note), bar), t0 + when + k * 0.015, g)
        t = np.arange(int(bar * sr)) / sr
        add(np.sin(2 * np.pi * hz(bass[b % 4]) * t) * np.minimum(1, t / 0.03) * np.exp(-t / 1.2), t0, 0.09)
        for e in range(8):  # very soft shaker
            ln = int(0.05 * sr)
            x = rng.standard_normal(ln)
            x = np.diff(np.concatenate([[0], x])) * np.exp(-np.arange(ln) / (0.012 * sr))
            add(x, t0 + e * beat / 2, 0.012 if e % 2 else 0.006)
    melody = [(81, 2), (78, 2), (76, 3), (73, 1), (74, 2), (76, 2), (78, 4)]
    t = bar
    for i in range(30):
        note, beats = melody[i % len(melody)]
        if t > total - 2:
            break
        tt = np.arange(int(beats * beat * 1.4 * sr)) / sr
        add((np.sin(2 * np.pi * hz(note) * tt) + 0.3 * np.sin(2 * np.pi * 2 * hz(note) * tt)) * np.minimum(1, tt / 0.005) * np.exp(-tt / 0.9), t, 0.1)
        t += beats * beat
    fi, fo = int(0.8 * sr), int(1.8 * sr)
    m[:fi] *= np.linspace(0, 1, fi)
    m[-fo:] *= np.linspace(1, 0, fo)
    m = np.tanh(m / np.max(np.abs(m)) * 1.1) * 0.85
    with wave.open(str(OUT / 'trilha.wav'), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.stack([m, m], axis=1) * 32767).astype('<i2').tobytes())


def main():
    OUT.mkdir(exist_ok=True)
    prepare_clips()
    end_card()
    gradient()
    total = sum(c[2] for c in CLIPS) + END_CARD - len(CLIPS) * XF
    assemble(total)
    music(total)
    final = DIR / 'galeria-dos-paes-video.mp4'
    run('ffmpeg', '-y', '-loglevel', 'error', '-i', str(OUT / 'video-sem-som.mp4'), '-i', str(OUT / 'trilha.wav'), '-c:v', 'copy',
        '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-shortest', '-movflags', '+faststart', str(final))
    run('ffmpeg', '-y', '-loglevel', 'error', '-ss', '1.6', '-i', str(final), '-frames:v', '1', '-q:v', '2', str(DIR / 'capa.jpg'))
    print(f'pronto: {final} ({total:.1f}s)')


if __name__ == '__main__':
    main()
