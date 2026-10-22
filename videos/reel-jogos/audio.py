"""Builds the reel soundtrack: a synthesized beat plus sound effects timed from out/events.json."""
import json
import pathlib
import wave

import numpy as np

SR = 44100
DUR = 15.5
MUSIC_START = 2.4  # lights turn on
BPM = 118
DIR = pathlib.Path(__file__).parent
rng = np.random.default_rng(3)


def env(n, decay):
    return np.exp(-np.arange(n) / (decay * SR))


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def tone(freq, length, decay, harmonics=((1, 1.0),)):
    t = np.arange(int(length * SR)) / SR
    s = sum(g * np.sin(2 * np.pi * freq * h * t) for h, g in harmonics)
    return s * env(len(t), decay)


def noise(length):
    return rng.standard_normal(int(length * SR))


def sfx(kind):
    if kind == 'strike':
        return 0.9 * tone(2400, 0.08, 0.012, ((1, 1), (1.7, 0.5))) + 0.5 * noise(0.08) * env(int(0.08 * SR), 0.006)
    if kind == 'click':
        return 0.7 * tone(3300, 0.05, 0.008, ((1, 1), (1.6, 0.4)))
    if kind == 'pocket':
        thud = tone(110, 0.3, 0.07)
        rattle = lowpass(noise(0.3), 900) * env(int(0.3 * SR), 0.05) * 2
        return 0.9 * thud + 0.5 * rattle
    if kind == 'kick':
        return 0.8 * tone(520, 0.12, 0.025, ((1, 1), (2.3, 0.3))) + 0.3 * lowpass(noise(0.12), 2000) * env(int(0.12 * SR), 0.01)
    if kind == 'whoosh':
        n = int(0.4 * SR)
        x = noise(0.4) * np.sin(np.linspace(0, np.pi, n)) ** 2
        return 0.35 * (x - lowpass(x, 600))
    if kind == 'pop':
        n = int(0.1 * SR)
        f = np.linspace(900, 300, n)
        return 0.6 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.03)
    if kind == 'ding':
        return 0.5 * tone(1318.5, 1.4, 0.35, ((1, 1), (2.01, 0.4), (3.0, 0.15)))
    if kind == 'goal':
        n = int(1.6 * SR)
        crowd = lowpass(noise(1.6), 2500) - lowpass(noise(1.6), 300)
        shape = np.minimum(1, np.arange(n) / (0.15 * SR)) * np.exp(-np.arange(n) / (0.9 * SR))
        t = np.arange(int(0.45 * SR)) / SR
        whistle = 0.25 * np.sin(2 * np.pi * (2900 + 60 * np.sin(2 * np.pi * 30 * t)) * t)
        out = 1.1 * crowd * shape
        out[: len(whistle)] += whistle
        return out
    raise ValueError(kind)


def beat(total):
    out = np.zeros(total)
    spb = 60 / BPM
    bass_notes = [55.0, 55.0, 65.41, 73.42, 55.0, 55.0, 82.41, 73.42]  # A1 pattern
    kick = None
    t = MUSIC_START
    step = 0
    while t < DUR - 0.2:
        i = int(t * SR)
        if step % 2 == 0:  # kick on every beat
            n = int(0.25 * SR)
            f = np.linspace(140, 45, n)
            kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.09)
            out[i:i + n] += 0.9 * kick[: max(0, min(n, total - i))]
        if step % 4 == 2:  # clap on 2 and 4
            n = int(0.18 * SR)
            c = noise(0.18)
            c = (c - lowpass(c, 900)) * env(n, 0.04)
            out[i:i + n] += 0.35 * c[: max(0, min(n, total - i))]
        n = int(0.05 * SR)  # hi-hat on every 8th
        h = noise(0.05)
        h = (h - lowpass(h, 6000)) * env(n, 0.01)
        out[i:i + n] += (0.18 if step % 2 else 0.1) * h[: max(0, min(n, total - i))]
        n = int(spb / 2 * SR * 0.9)  # bass on every 8th
        tt = np.arange(n) / SR
        f = bass_notes[(step // 2) % len(bass_notes)] * (2 if step % 2 else 1)
        b = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)) * env(n, 0.12)
        out[i:i + n] += 0.32 * b[: max(0, min(n, total - i))]
        t += spb / 2
        step += 1
    # fade the music out at the end
    fade = int(0.5 * SR)
    out[total - fade:] *= np.linspace(1, 0, fade)
    return out


def main():
    total = int(DUR * SR)
    mix = beat(total) * 0.55
    # quiet room tone during the hook
    hum = lowpass(noise(MUSIC_START), 200) * 0.6
    mix[: len(hum)] += hum * np.linspace(1, 0.2, len(hum))
    for ev in json.loads((DIR / 'out' / 'events.json').read_text()):
        s = sfx(ev['kind']) * ev['gain']
        i = int(ev['time'] * SR)
        n = max(0, min(len(s), total - i))
        mix[i:i + n] += s[:n]
    peak = np.max(np.abs(mix))
    mix = np.tanh(mix / peak * 1.2) * 0.85  # soft limit
    pcm = (np.stack([mix, mix], axis=1) * 32767).astype('<i2')
    with wave.open(str(DIR / 'out' / 'trilha.wav'), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    main()
