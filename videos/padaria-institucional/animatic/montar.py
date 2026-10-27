"""Animatic de 30 s do vídeo institucional de padaria (modelo genérico), em 16:9 e 9:16.

Segue os tempos, textos e atos de ../animatic-quadro-a-quadro.md. As imagens são clipes de
referência do Mixkit (ver FONTES.md) e servem só para aprovar ritmo, textos e música: o
vídeo final é filmado na padaria. A trilha e os efeitos são provisórios, sintetizados aqui.

Uso: python montar.py <pasta com os clipes>   (grava animatic-16x9.mp4, animatic-9x16.mp4 e capa.jpg aqui)
"""
import pathlib
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

DIR = pathlib.Path(__file__).parent
CLIPS = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DIR / 'clipes'
OUT = DIR / 'out'
FPS = 30
DUR = 30.0
FONTS = pathlib.Path('/usr/share/fonts/opentype/inter')
FORMATS = {'16x9': (1920, 1080), '9x16': (1080, 1920)}

# Cor por ato (luz que conta a hora)
FRIO = 'colorbalance=rs=-0.06:bs=0.12:rm=-0.04:bm=0.08,eq=brightness=-0.04:saturation=0.85'
QUENTE = 'colorbalance=rs=0.03:bs=-0.03,eq=saturation=1.03'
AMBAR = 'colorbalance=rs=0.10:gs=0.02:bs=-0.10:rm=0.06:bm=-0.06,eq=saturation=1.08'
DOURADO = 'colorbalance=rs=0.07:gs=0.03:bs=-0.07,eq=saturation=1.06:brightness=0.02'

# (plano, descrição curta, ato, [(clipe, início no clipe, duração, centro horizontal do quadro vertical, velocidade, extra)])
# velocidade > 1 acelera (time-lapse), < 1 desacelera; extra = filtro adicional
PLANOS = [
    (1, 'Fachada à noite', FRIO, [('rua', 2.0, 2.0, 0.85, 1, 'gblur=sigma=14')]),  # desfocado: o clipe tem letreiros de terceiros
    (2, 'Luzes acendendo', FRIO, [('cozinha', 1.0, 2.0, 0.45, 1, 'fade=in:st=0.45:d=0.9')]),
    (3, 'Farinha em contraluz', QUENTE, [('farinha', 21.5, 2.0, 0.55, 1, '')]),
    (4, 'Mãos sovando', QUENTE, [('sovando', 3.0, 1.8, 0.55, 1, ''), ('farinha-mesa', 4.3, 1.2, 0.45, 1, '')]),
    (5, 'Modelagem', QUENTE, [('formando', 1.5, 2.0, 0.55, 1, '')]),
    (6, 'Massa crescendo (time-lapse)', QUENTE, [('crescendo2', 0.0, 1.5, 0.35, 14, '')]),
    (7, 'Assadeira entra no forno', QUENTE, [('bolo-forno', 4.0, 1.5, 0.5, 1, 'fade=out:st=1.15:d=0.35')]),
    (8, 'Forno abre · pães na pá', AMBAR, [('abre-forno', 5.6, 1.4, 0.6, 1, 'fade=in:st=0:d=0.3'), ('pitas', 7.2, 1.6, 0.45, 0.6, '')]),
    (9, 'Pão partido (estalo)', AMBAR, [('croissant', 0.4, 2.0, 0.22, 0.8, '')]),
    (10, 'Bolo: cobertura e fatia', AMBAR, [('cobertura', 6.0, 1.0, 0.45, 1, ''), ('bolo-corte', 5.2, 1.0, 0.5, 1, '')]),
    (11, 'Vitrine abastecida', DOURADO, [('vitrine', 0.8, 2.0, 0.5, 1, '')]),
    (12, 'Portas abertas, clientes', DOURADO, None),  # sem referência: cartão
    (13, 'Café servido · encontro', DOURADO, [('cafe', 3.0, 1.0, 0.5, 1, ''), ('garcom', 8.0, 1.0, 0.45, 1, '')]),
    (14, 'Tela final', None, None),
]
# início de cada plano no filme (segundos), conforme o roteiro
INICIOS = [0, 2, 4, 6, 9, 11, 12.5, 14, 17, 19, 21, 23, 25, 27, 30]

# textos: (conteúdo, entra, sai, posição) — TI/TS = terço inferior/superior, E/D = esquerda/direita
TEXTOS = [
    ('[HORA DE INÍCIO].', 0.1, 2.0, 'TI-E'),
    ('Enquanto a cidade dorme…', 2.1, 4.3, 'TI-E'),
    ('…tem mãos trabalhando por você.', 6.4, 9.0, 'TS-E'),
    ('Receita boa não se apressa.', 14.6, 17.0, 'TS-D'),
    ('O cheiro chega antes da gente.', 19.2, 21.0, 'TS-E'),
    ('[HORÁRIO]. Portas abertas.', 23.1, 25.0, 'TI-E'),
    ('Seu dia começa aqui.', 25.1, 27.0, 'TS-D'),
]


def run(*cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def font(name, size):
    return ImageFont.truetype(str(FONTS / f'{name}.otf'), size)


# ---------- imagem ----------

def segmento(fmt, idx, clip, start, dur, cx, speed, extra, grade):
    W, H = FORMATS[fmt]
    src = CLIPS / f'{clip}.mp4'
    w, h = 1280, 720
    scale = max(W / w, H / h)
    sw, sh = round(w * scale / 2) * 2, round(h * scale / 2) * 2
    x = int(min(max(cx * sw - W / 2, 0), sw - W)) if fmt == '9x16' else int((sw - W) / 2)
    y = int((sh - H) / 2)
    vf = [f'setpts=PTS/{speed}', f'scale={sw}:{sh}:flags=lanczos', f'crop={W}:{H}:{x}:{y}', f'fps={FPS}', 'setsar=1']
    if grade:
        vf.append(grade)
    if extra:
        vf.append(extra)
    vf.append(f'trim=duration={dur},setpts=PTS-STARTPTS')
    out = OUT / f'{fmt}-seg{idx:02d}.mp4'
    run('ffmpeg', '-y', '-loglevel', 'error', '-ss', start, '-t', dur * speed + 0.5, '-i', src, '-vf', ','.join(vf),
        '-an', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-r', FPS, out)
    return out


def cartao(fmt, idx, img, dur):
    out = OUT / f'{fmt}-seg{idx:02d}.mp4'
    png = OUT / f'{fmt}-card{idx:02d}.png'
    img.save(png)
    run('ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-t', dur, '-i', png, '-vf', f'fps={FPS},setsar=1',
        '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', out)
    return out


def centro(d, W, text, y, fnt, fill):
    d.text(((W - d.textlength(text, font=fnt)) / 2, y), text, font=fnt, fill=fill)


def cartao_p12(fmt):
    W, H = FORMATS[fmt]
    yy = np.linspace(0, 1, H)[:, None]
    xx = np.linspace(0, 1, W)[None, :]
    luz = np.clip(1 - np.hypot(xx - 0.5, yy - 0.35) * 1.4, 0, 1)
    base = np.stack([60 + 170 * luz, 38 + 120 * luz, 20 + 55 * luz], axis=-1).astype(np.uint8)
    img = Image.fromarray(base)
    d = ImageDraw.Draw(img)
    k = W / 1920 if fmt == '16x9' else 1.0
    # porta esquemática com feixe de sol
    pw, ph = int(360 * (k if fmt == '16x9' else 1)), int(620 * (k if fmt == '16x9' else 1))
    px, py = (W - pw) // 2, int(H * (0.18 if fmt == '16x9' else 0.25))
    d.rectangle((px, py, px + pw, py + ph), outline=(255, 236, 200), width=6)
    d.polygon([(px, py + ph), (px + pw, py + ph), (px + pw + pw * 0.8, H), (px - pw * 0.8, H)], fill=(255, 226, 170))
    f1, f2 = font('Inter-SemiBold', 44 if fmt == '16x9' else 50), font('Inter-Regular', 30 if fmt == '16x9' else 34)
    ty = int(H * (0.12 if fmt == '16x9' else 0.13))  # acima da porta, longe do texto de tela
    if fmt == '16x9':
        centro(d, W, 'P12 · Porta abrindo, sol entrando, primeiros clientes', ty, f1, (255, 240, 215))
    else:
        centro(d, W, 'P12 · Porta abrindo, sol entrando,', ty, f1, (255, 240, 215))
        centro(d, W, 'primeiros clientes', ty + 64, f1, (255, 240, 215))
        ty += 64
    centro(d, W, 'sem imagem de referência: filmar na padaria', ty + 64, f2, (240, 215, 180))
    return img


def cartao_final(fmt):
    W, H = FORMATS[fmt]
    CREME, TINTA, MARCA = (246, 239, 228), (42, 29, 20), (168, 90, 31)
    img = Image.new('RGB', (W, H), CREME)
    d = ImageDraw.Draw(img)
    v = fmt == '9x16'
    cy = H * (0.40 if v else 0.30)
    lw, lh = (520, 220) if v else (460, 190)
    d.rounded_rectangle(((W - lw) / 2, cy, (W + lw) / 2, cy + lh), radius=24, outline=TINTA, width=4)
    centro(d, W, '[LOGO DA PADARIA]', cy + lh / 2 - 26, font('Inter-SemiBold', 44 if v else 40), TINTA)
    y = cy + lh + (70 if v else 50)
    centro(d, W, 'Feito aqui. Feito todo dia.', y, font('InterDisplay-Medium', 76 if v else 68), TINTA)
    y += 120 if v else 105
    cta, f = '[CTA]', font('Inter-Medium', 46 if v else 40)
    tw = d.textlength(cta, font=f)
    d.rounded_rectangle(((W - tw) / 2 - 60, y, (W + tw) / 2 + 60, y + (96 if v else 84)), radius=48, fill=MARCA)
    centro(d, W, cta, y + (20 if v else 17), f, (255, 255, 255))
    y += 140 if v else 120
    centro(d, W, '[ENDEREÇO] · [WHATSAPP]', y, font('Inter-Regular', 36 if v else 32), (140, 122, 104))
    return img


def montar_base(fmt):
    segs = []
    idx = 0
    for i, (num, _, grade, partes) in enumerate(PLANOS):
        dur_plano = INICIOS[i + 1] - INICIOS[i]
        if num == 12:
            segs.append(cartao(fmt, idx, cartao_p12(fmt), dur_plano)); idx += 1
        elif num == 14:
            segs.append(cartao(fmt, idx, cartao_final(fmt), dur_plano)); idx += 1
        else:
            soma = sum(p[2] for p in partes)
            assert abs(soma - dur_plano) < 1e-6, (num, soma, dur_plano)
            for clip, start, dur, cx, speed, extra in partes:
                segs.append(segmento(fmt, idx, clip, start, dur, cx, speed, extra, grade)); idx += 1
    lista = OUT / f'{fmt}-lista.txt'
    lista.write_text(''.join(f"file '{s.name}'\n" for s in segs))
    base = OUT / f'{fmt}-base.mp4'
    run('ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lista, '-c:v', 'libx264', '-crf', '16',
        '-pix_fmt', 'yuv420p', '-r', FPS, base)
    return base


# ---------- camadas por quadro ----------

def texto_png(text, size, W):
    f = font('InterDisplay-Medium', size)
    tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    tw = int(tmp.textlength(text, font=f))
    img = Image.new('RGBA', (tw + 80, int(size * 1.6)), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((40, int(size * 0.2)), text, font=f, fill=(255, 255, 255, 255))
    sombra = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sombra.putalpha(img.getchannel('A').point(lambda a: int(a * 0.6)).filter(ImageFilter.GaussianBlur(12)))
    return Image.alpha_composite(sombra, img)


def posicao(pos, img, W, H):
    v = H > W
    margem = 90 if v else 120
    x = margem - 40 if pos.endswith('E') else W - img.width - margem + 40
    if v:  # vertical: textos centralizados, longe das faixas da interface
        x = (W - img.width) // 2
        y = int(H * (0.62 if pos.startswith('TI') else 0.20))
    else:
        y = int(H * (0.74 if pos.startswith('TI') else 0.10))
    return x, y


def plano_em(t):
    for i in range(len(PLANOS)):
        if INICIOS[i] <= t < INICIOS[i + 1]:
            return PLANOS[i]
    return PLANOS[-1]


def sobrepor(fmt, base, saida):
    W, H = FORMATS[fmt]
    v = H > W
    size = 74 if v else 64
    pngs = [texto_png(t, size if len(t) < 28 else size - 8, W) for t, *_ in TEXTOS]
    f_rot = font('Inter-SemiBold', 26 if v else 24)
    f_nota = font('Inter-Regular', 22 if v else 20)
    rotulos = {}

    def rotulo(num, desc):
        if num not in rotulos:
            txt = f'ANIMATIC · P{num:02d} · {desc}'
            tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
            tw = int(tmp.textlength(txt, font=f_rot))
            img = Image.new('RGBA', (tw + 36, 46), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            d.rounded_rectangle((0, 0, tw + 35, 45), radius=10, fill=(0, 0, 0, 120))
            d.text((18, 9), txt, font=f_rot, fill=(255, 255, 255, 230))
            rotulos[num] = img
        return rotulos[num]

    nota_txt = 'Imagens de referência (Mixkit) e trilha provisória · não é o vídeo final'
    tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    nw = int(tmp.textlength(nota_txt, font=f_nota))
    nota = Image.new('RGBA', (nw + 24, 34), (0, 0, 0, 0))
    ImageDraw.Draw(nota).rounded_rectangle((0, 0, nw + 23, 33), radius=8, fill=(0, 0, 0, 100))
    ImageDraw.Draw(nota).text((12, 6), nota_txt, font=f_nota, fill=(255, 255, 255, 200))

    dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', str(base), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                            str(saida)], stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    for i in range(n):
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3:
            break
        t = i / FPS
        frame = Image.frombytes('RGB', (W, H), raw).convert('RGBA')
        num, desc, *_ = plano_em(t)
        frame.alpha_composite(rotulo(num, desc), (24 if not v else 24, 24 if not v else 150))
        if num != 14:
            frame.alpha_composite(nota, ((W - nota.width) // 2, H - (60 if not v else 420)))
        for (txt, t0, t1, pos), png in zip(TEXTOS, pngs):
            if t0 <= t < t1:
                a = min(1, (t - t0) / 0.2, (t1 - t) / 0.15)  # entrada rápida, saída curta
                sub = int(18 * (1 - min(1, (t - t0) / 0.3)))
                layer = png.copy()
                layer.putalpha(layer.getchannel('A').point(lambda p: int(p * a)))
                x, y = posicao(pos, png, W, H)
                frame.alpha_composite(layer, (x, y + sub))
        enc.stdin.write(frame.convert('RGB').tobytes())
    enc.stdin.close()
    enc.wait()
    dec.wait()


# ---------- som provisório ----------

SR = 44100


def trilha():
    """Violão/piano sintético a 90 BPM com a estrutura do briefing: quase silêncio (0–4),
    crescimento (4–14), respiro no grave (14–19), volta cheia (21–27) e final resolvido (27–30).
    Inclui efeitos provisórios nos pontos de sincronia."""
    rng = np.random.default_rng(7)
    n = int(DUR * SR)
    m = np.zeros(n)
    fx = np.zeros(n)
    beat = 60 / 90
    hz = lambda midi: 440.0 * 2 ** ((midi - 69) / 12)

    def add(buf, sig, t, g):
        i = int(t * SR)
        k = max(0, min(len(sig), n - i))
        buf[i:i + k] += g * sig[:k]

    def nota(f, length, bright=0.3, dec=1.8):
        tt = np.arange(int(length * SR)) / SR
        s = np.sin(2 * np.pi * f * tt) + bright * np.sin(4 * np.pi * f * tt) * np.exp(-tt / 0.3) \
            + 0.5 * bright * np.sin(6 * np.pi * f * tt) * np.exp(-tt / 0.12)
        return s * np.minimum(1, tt / 0.006) * np.exp(-tt / dec)

    def ruido(length, decay, hp=True):
        x = rng.standard_normal(int(length * SR))
        if hp:
            x = np.diff(np.concatenate([[0], x]))
        return x * np.exp(-np.arange(len(x)) / (decay * SR))

    # intensidade da música ao longo do tempo (curva do briefing)
    def nivel(t):
        pts = [(0, 0.25), (4, 0.35), (14, 1.0), (14.6, 0.35), (17, 0.18), (19, 0.25), (21, 1.0), (27, 1.0), (30, 0.8)]
        for (a, va), (b, vb) in zip(pts, pts[1:]):
            if a <= t <= b:
                return va + (vb - va) * (t - a) / (b - a)
        return 0.8

    chords = [[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66], [57, 61, 64, 67]]  # Dmaj7 Bm7 Gmaj7 A7
    bass = [38, 35, 31, 33]
    bar = 4 * beat
    for b in range(int(np.ceil(DUR / bar))):
        t0 = b * bar
        if t0 >= 27:
            break
        c = chords[b % 4]
        L = nivel(t0)
        # dedilhado
        for k in range(8):
            t = t0 + k * beat / 2
            if 14.6 <= t < 19.5 or t >= 27:
                continue
            if t < 4 and k % 2:
                continue
            add(m, nota(hz(c[k % 4] + (12 if k % 4 == 3 else 0)), 1.6, 0.4, 0.9), t, 0.09 * nivel(t))
        # baixo (presente no respiro: "quase só no grave")
        add(m, nota(hz(bass[b % 4]), bar, 0.1, 1.6), t0, 0.16 * max(L, 0.5))
        # percussão leve só no crescimento e na volta
        for e in range(8):
            t = t0 + e * beat / 2
            if (4 <= t < 14.6) or (21 <= t < 27):
                add(m, ruido(0.06, 0.012), t, (0.02 if e % 2 else 0.035) * nivel(t))
                if e % 4 == 0:
                    tt = np.arange(int(0.25 * SR)) / SR
                    add(m, np.sin(2 * np.pi * (55 + 60 * np.exp(-tt / 0.03)) * tt) * np.exp(-tt / 0.12), t, 0.10 * nivel(t))
    # melodia na volta cheia
    t = 21.0
    for mi, bt in [(78, 2), (76, 1), (74, 1), (76, 2), (73, 2), (74, 2), (71, 2)]:
        if t >= 27:
            break
        add(m, nota(hz(mi), bt * beat * 1.4, 0.15, 1.0), t, 0.07)
        t += bt * beat
    # acorde final resolvido
    for k, mi in enumerate([50, 57, 62, 66, 69, 74]):
        add(m, nota(hz(mi), 3.2, 0.3, 1.6), 27.0 + k * 0.02, 0.07)

    # efeitos provisórios (pontos de sincronia do roteiro)
    tt = np.arange(int(0.03 * SR)) / SR
    add(fx, np.sin(2 * np.pi * 2500 * tt) * np.exp(-tt / 0.004), 2.55, 0.5)                       # interruptor
    hum = np.sin(2 * np.pi * 120 * np.arange(int(1.4 * SR)) / SR) * np.minimum(1, np.arange(int(1.4 * SR)) / (0.3 * SR))
    add(fx, hum * np.exp(-np.arange(len(hum)) / (0.9 * SR)), 2.6, 0.04)                           # zumbido
    add(fx, ruido(0.5, 0.12, hp=False) * 0.4, 4.25, 0.25)                                         # puff da farinha
    for t in (6.0, 6.0 + 2 * beat, 7.8):                                                          # tapa da massa
        add(fx, ruido(0.12, 0.02, hp=False), t, 0.35)
    add(fx, ruido(0.35, 0.05), 9.9, 0.08)                                                         # lâmina
    w = rng.standard_normal(int(1.2 * SR)); env = np.sin(np.linspace(0, np.pi, len(w))) ** 2
    add(fx, np.convolve(w, np.ones(40) / 40, 'same') * env, 11.0, 0.25)                           # whoosh
    tt = np.arange(int(0.35 * SR)) / SR
    add(fx, (np.sin(2 * np.pi * 70 * tt) + 0.5 * rng.standard_normal(len(tt)) * np.exp(-tt / 0.02)) * np.exp(-tt / 0.08), 13.85, 0.5)  # porta do forno
    w = rng.standard_normal(int(1.5 * SR)); env = np.exp(-np.linspace(0, 4, len(w))) * np.minimum(1, np.linspace(0, 8, len(w)))
    add(fx, np.convolve(w, np.ones(120) / 120, 'same') * env, 14.05, 0.9)                         # sopro de calor
    for k in range(14):                                                                           # ESTALO da casca
        add(fx, ruido(0.03, 0.004), 17.25 + k * 0.018 + rng.uniform(0, 0.012), 0.55 * (1 - k / 16))
    add(fx, ruido(0.4, 0.06), 20.0, 0.06)                                                         # faca
    for k, f in enumerate((2093, 2637)):                                                          # sininho da porta
        tt = np.arange(int(1.2 * SR)) / SR
        add(fx, np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.35), 23.15 + k * 0.08, 0.08)
    w = rng.standard_normal(int(1.0 * SR))
    add(fx, np.convolve(w, np.ones(6) / 6, 'same') * np.sin(np.linspace(0, np.pi, len(w))), 25.0, 0.05)  # café caindo
    # ambiente leve
    amb = np.convolve(rng.standard_normal(n), np.ones(200) / 200, 'same') * 0.6

    mix = m / (np.max(np.abs(m)) + 1e-9) * 0.6 + fx + amb * 0.02
    fi, fo = int(0.3 * SR), int(0.8 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    mix[-fo:] *= np.linspace(1, 0, fo)
    mix = np.tanh(mix * 1.2) * 0.9
    pcm = (np.stack([mix, mix], axis=1) * 32767).astype('<i2')
    path = OUT / 'trilha.wav'
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


def loudnorm(audio):
    """Normalização em duas passadas: mede e depois aplica, para cair perto de -14 LUFS / -1,5 dBTP."""
    import json
    alvo = 'I=-14:TP=-1.5:LRA=11'
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(audio), '-af', f'loudnorm={alvo}:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
    return (f"loudnorm={alvo}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
            f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")


def main():
    OUT.mkdir(exist_ok=True)
    audio = trilha()
    for fmt in FORMATS:
        base = montar_base(fmt)
        sem_som = OUT / f'{fmt}-sem-som.mp4'
        sobrepor(fmt, base, sem_som)
        final = DIR / f'animatic-{fmt}.mp4'
        run('ffmpeg', '-y', '-loglevel', 'error', '-i', sem_som, '-i', audio, '-c:v', 'copy',
            '-af', loudnorm(audio) + ',alimiter=limit=0.82:level=false', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-t', DUR,
            '-movflags', '+faststart', final)
        print('pronto:', final)
    run('ffmpeg', '-y', '-loglevel', 'error', '-ss', 15.5, '-i', DIR / 'animatic-9x16.mp4', '-frames:v', 1, '-q:v', 2, DIR / 'capa.jpg')


if __name__ == '__main__':
    main()
