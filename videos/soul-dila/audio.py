"""Builds a calm, warm soundtrack for the Soul Dila ad (electric piano, bass, shaker)."""
import pathlib
import wave

import numpy as np

SR = 44100
DUR = 18.0
BPM = 84
DIR = pathlib.Path(__file__).parent
rng = np.random.default_rng(11)
LOGO_TIME = 15.0  # end card starts; a soft chime marks the logo

# Dmaj7 - Bm7 - Gmaj7 - A6, one chord per bar
CHORDS = [[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66], [57, 61, 64, 66]]
BASS = [38, 35, 31, 33]


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def epiano(freq, length):
    t = np.arange(int(length * SR)) / SR
    attack = np.minimum(1, t / 0.012)
    tone = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t / 0.3) + 0.08 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t / 0.15)
    tremolo = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
    return tone * attack * np.exp(-t / 1.6) * tremolo


def main():
    total = int(DUR * SR)
    music = np.zeros(total)
    beat = 60 / BPM
    bar = 4 * beat
    n_bars = int(np.ceil(DUR / bar))
    for b in range(n_bars):
        t0 = b * bar
        chord = CHORDS[b % 4]
        # chord on beat 1, a softer re-strike on the "and" of beat 3
        for when, gain in ((0.0, 0.16), (2.5 * beat, 0.09)):
            for k, note in enumerate(chord):
                s = epiano(hz(note), bar) * gain
                i = int((t0 + when + k * 0.012) * SR)
                n = max(0, min(len(s), total - i))
                music[i:i + n] += s[:n]
        # bass: root on 1, fifth on 3
        for when, note in ((0, BASS[b % 4]), (2 * beat, BASS[b % 4] + 7)):
            t = np.arange(int(beat * 1.8 * SR)) / SR
            s = 0.22 * np.sin(2 * np.pi * hz(note) * t) * np.minimum(1, t / 0.02) * np.exp(-t / 0.7)
            i = int((t0 + when) * SR)
            n = max(0, min(len(s), total - i))
            music[i:i + n] += s[:n]
        # shaker on 8ths, accent on the off-beats
        for e in range(8):
            ln = int(0.06 * SR)
            x = rng.standard_normal(ln)
            x = (x - lowpass(x, 5000)) * np.exp(-np.arange(ln) / (0.018 * SR))
            i = int((t0 + e * beat / 2) * SR)
            n = max(0, min(ln, total - i))
            music[i:i + n] += (0.05 if e % 2 else 0.025) * x[:n]
    # soft chime on the logo
    t = np.arange(int(2.5 * SR)) / SR
    chime = sum(g * np.sin(2 * np.pi * hz(86) * h * t) for h, g in ((1, 1), (2.01, 0.3), (3.0, 0.1))) * np.exp(-t / 0.8) * 0.12
    i = int((LOGO_TIME + 0.4) * SR)
    music[i:i + len(chime)] += chime[: total - i]
    # fade in / out
    fi, fo = int(0.6 * SR), int(1.2 * SR)
    music[:fi] *= np.linspace(0, 1, fi)
    music[-fo:] *= np.linspace(1, 0, fo)
    music = np.tanh(music / np.max(np.abs(music)) * 1.1) * 0.8
    pcm = (np.stack([music, music], axis=1) * 32767).astype('<i2')
    (DIR / 'out').mkdir(exist_ok=True)
    with wave.open(str(DIR / 'out' / 'trilha.wav'), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    main()
