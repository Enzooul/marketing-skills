"""Soundtrack for the Soul Dila ad: bossa-style nylon guitar, soft melody and shaker,
mixed with the narration (music ducks under the voice).

Usage: python audio.py <A|B> <narration_dir>
The narration dir holds one WAV per line, named as in NARRATION below.
"""
import pathlib
import sys
import wave

import numpy as np

SR = 44100
DUR = 18.0
BPM = 84
DIR = pathlib.Path(__file__).parent
rng = np.random.default_rng(11)

# (start time in seconds, file stem) — the hook line depends on the version
NARRATION = [(0.35, '{v}0'), (3.2, '1'), (6.2, '2'), (9.0, '3'), (12.6, '4'), (15.9, '5')]

# Dmaj7 - Bm7 - Gmaj7 - A7, nylon-guitar voicings (MIDI)
CHORDS = [[50, 57, 61, 66, 69], [47, 54, 57, 62, 66], [43, 50, 54, 59, 62], [45, 52, 55, 61, 64]]
BASS = [38, 35, 31, 33]
# one melody note per half bar: (MIDI, length in beats)
MELODY = [(78, 2), (76, 2), (74, 2), (73, 2), (71, 2), (74, 2), (76, 3), (73, 1)]
CHORD_16THS = [0, 3, 6, 10, 13]  # bossa-style comping inside each bar


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


def pluck(freq, length, brightness=0.5, decay=0.996):
    """Karplus-Strong string, computed one period at a time."""
    n = int(length * SR)
    p = max(2, int(round(SR / freq)))
    burst = rng.uniform(-1, 1, p)
    burst = lowpass(burst, 1500 + 6000 * brightness)
    y = np.zeros(n + p + 1)
    y[:p] = burst
    for start in range(p, n + p, p):
        end = min(start + p, n + p)
        seg = np.arange(start, end)
        y[seg] = decay * 0.5 * (y[seg - p] + y[seg - p - 1])
    out = y[p:p + n]
    return out / (np.max(np.abs(out)) + 1e-9)


def add(buf, sig, t, gain):
    i = int(t * SR)
    n = max(0, min(len(sig), len(buf) - i))
    buf[i:i + n] += gain * sig[:n]


def music_track():
    total = int(DUR * SR)
    m = np.zeros(total)
    beat = 60 / BPM
    bar = 4 * beat
    s16 = beat / 4
    for b in range(int(np.ceil(DUR / bar))):
        t0 = b * bar
        chord = CHORDS[b % 4]
        add(m, pluck(hz(BASS[b % 4]), 1.6, 0.25, 0.997), t0, 0.32)                # thumb on 1
        add(m, pluck(hz(BASS[b % 4] + 7), 1.4, 0.25, 0.997), t0 + 2 * beat, 0.26)  # and on 3
        for pos in CHORD_16THS:
            for k, note in enumerate(chord[1:]):
                add(m, pluck(hz(note), 0.9, 0.55, 0.994), t0 + pos * s16 + k * 0.007, 0.07)
        # shaker
        for e in range(16):
            ln = int(0.05 * SR)
            x = rng.standard_normal(ln)
            x = (x - lowpass(x, 5000)) * np.exp(-np.arange(ln) / (0.012 * SR))
            add(m, x, t0 + e * s16, 0.05 if e % 2 else 0.025)
    # soft vibraphone-like melody, starting when the hook line ends
    t = 2.2
    for i in range(40):
        note, beats = MELODY[i % len(MELODY)]
        if t > DUR - 1:
            break
        ln = beats * beat * 1.3
        tt = np.arange(int(ln * SR)) / SR
        tone = (np.sin(2 * np.pi * hz(note) * tt) + 0.2 * np.sin(2 * np.pi * 4 * hz(note) * tt) * np.exp(-tt / 0.2))
        tone *= np.minimum(1, tt / 0.01) * np.exp(-tt / 1.1) * (1 + 0.15 * np.sin(2 * np.pi * 5 * tt))
        add(m, tone, t, 0.09)
        t += beats * beat
    fi, fo = int(0.4 * SR), int(1.2 * SR)
    m[:fi] *= np.linspace(0, 1, fi)
    m[-fo:] *= np.linspace(1, 0, fo)
    return m


def read_wav(path):
    with wave.open(str(path)) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, '<i2' if sw == 2 else '<i4').astype(float)
    x /= 32768 if sw == 2 else 2 ** 31
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    if sr != SR:  # linear resample is enough for speech at this rate ratio
        x = np.interp(np.arange(0, len(x), sr / SR), np.arange(len(x)), x)
    return x


def voice_track(version, narr_dir):
    total = int(DUR * SR)
    v = np.zeros(total)
    for start, stem in NARRATION:
        x = read_wav(pathlib.Path(narr_dir) / f'{stem.format(v=version)}.wav')
        x = x / (np.max(np.abs(x)) + 1e-9)
        add(v, x, start, 1.0)
    # soft "room": a few quiet early reflections make the voice warmer and less dry
    room = v.copy()
    for d, g in ((0.023, 0.18), (0.041, 0.12), (0.067, 0.08), (0.097, 0.05)):
        k = int(d * SR)
        room[k:] += g * v[:-k]
    return room


def main():
    version, narr_dir = sys.argv[1], sys.argv[2]
    music = music_track()
    voice = voice_track(version, narr_dir)
    # duck the music under the voice (smoothed envelope)
    env = np.abs(voice)
    win = int(0.25 * SR)
    env = np.convolve(env, np.ones(win) / win, mode='same')
    duck = 1 - 0.55 * np.clip(env / (np.max(env) * 0.25), 0, 1)
    music = music / np.max(np.abs(music))
    voice = voice / np.max(np.abs(voice))
    mix = 0.55 * music * duck + 0.95 * voice
    mix = np.tanh(mix * 1.1) * 0.9
    pcm = (np.stack([mix, mix], axis=1) * 32767).astype('<i2')
    (DIR / 'out').mkdir(exist_ok=True)
    with wave.open(str(DIR / 'out' / f'trilha-{version}.wav'), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    main()
