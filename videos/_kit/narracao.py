"""Generates a client's narration lines with Kokoro (Apache-2.0), voice pf_dora (female, pt-BR).

Needs: pip install kokoro-onnx soundfile, plus espeak-ng, and the model files
kokoro-v1.0.onnx / voices-v1.0.bin from github.com/thewh1teagle/kokoro-onnx releases.
Usage: python narracao.py <model_dir> <client folder>
Writes <client>/narracao/{A0,B0,1..5}.wav, matching the scenes of modelo.html.
"""
import json
import pathlib
import sys

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

SPEED = 0.88  # a little slower than default: calmer, softer delivery
# line -> (config key, max seconds that fits the scene)
SLOTS = {'1': ('cena2', 2.7), '2': ('cena3', 2.7), '3': ('grade', 3.2), '4': ('destaque', 3.1), '5': ('cta', 2.0)}
HOOK_MAX = 2.6


def load_config(client):
    raw = (client / 'config.js').read_text(encoding='utf-8')
    return json.loads(raw[raw.index('{'):raw.rindex('}') + 1])


def trim_breath(audio, sr):
    """The voice sometimes ends a phrase with a breathy hiss that sounds like a final "s"
    ("alma" -> "almas"). Cut the tail where >50% of the energy is above 4 kHz."""
    hop = int(0.01 * sr)
    frames = []  # (start sample, level dB, share of energy above 4 kHz)
    for i in range(0, len(audio) - 2 * hop, hop):
        seg = audio[i:i + 2 * hop]
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        level = 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9)
        frames.append((i, level, spec[freqs > 4000].sum() / (spec.sum() + 1e-9)))
    # only look at the tail: after the last voiced frame (loud, little hiss)
    voiced = [k for k, (_, level, hf) in enumerate(frames) if level > -40 and hf < 0.3]
    if not voiced:
        return audio
    tail = frames[voiced[-1] + 1:]
    hiss = [f for f in tail if f[1] > -50 and f[2] > 0.5]
    if len(hiss) < 5:  # under ~50 ms of hiss is natural release, keep it
        return audio
    cut = frames[voiced[-1]][0] + 2 * hop
    out = audio[:cut].copy()
    fade = min(int(0.04 * sr), len(out))
    out[-fade:] *= np.linspace(1, 0, fade)
    return out


def speak(k, text, max_seconds):
    speed = SPEED
    while True:
        audio, sr = k.create(text, voice='pf_dora', speed=speed, lang='pt-br')
        # only a phrase that ends in a vowel can have a spurious hissy tail
        if text.rstrip('.!?…').strip()[-1:].lower() in 'aeiouáéíóúâêôãõ':
            audio = trim_breath(audio, sr)
        if len(audio) / sr <= max_seconds or speed >= 1.05:
            return audio, sr
        speed += 0.04


def main():
    model_dir, client = map(pathlib.Path, sys.argv[1:3])
    cfg = load_config(client)
    out = client / 'narracao'
    out.mkdir(exist_ok=True)
    k = Kokoro(str(model_dir / 'kokoro-v1.0.onnx'), str(model_dir / 'voices-v1.0.bin'))
    lines = {f'{v}0': (cfg['versoes'][v]['narracao'], HOOK_MAX) for v in cfg['versoes']}
    lines.update({stem: (cfg['narracao'][key], limit) for stem, (key, limit) in SLOTS.items()})
    for stem, (text, limit) in lines.items():
        audio, sr = speak(k, text, limit)
        sf.write(out / f'{stem}.wav', audio, sr)
        flag = '  <-- longa demais, encurte o texto' if len(audio) / sr > limit else ''
        print(f'{stem}: {len(audio) / sr:.2f}s  {text}{flag}')


if __name__ == '__main__':
    main()
