"""Generates the narration lines with Kokoro (Apache-2.0), voice pf_dora (female, pt-BR).

Needs: pip install kokoro-onnx soundfile, plus espeak-ng, and the model files
kokoro-v1.0.onnx / voices-v1.0.bin from github.com/thewh1teagle/kokoro-onnx releases.
Usage: python narracao.py <model_dir> <out_dir>
"""
import pathlib
import sys

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

LINES = {
    'A0': 'Seu dia pede pausa.',
    'B0': 'Roupa que parece férias.',
    '1': 'Leve no corpo.',
    '2': 'Leve na alma.',
    '3': 'Peças fluidas e confortáveis, com alma baiana.',
    '4': 'Soul Dila. Alma e leveza.',
    '5': 'Compre agora no nosso site.',
}
SPEED = 0.88  # a little slower than default: calmer, softer delivery


def trim_breath(audio, sr):
    """The voice sometimes ends a phrase with a breathy hiss that sounds like a final "s"
    ("alma" -> "almas"). Cut the tail where >50% of the energy is above 4 kHz."""
    hop = int(0.01 * sr)
    for i in range(int(0.6 * sr), len(audio) - 2 * hop, hop):
        seg = audio[i:i + 2 * hop] * np.hanning(2 * hop)
        spec = np.abs(np.fft.rfft(seg))
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        if spec[freqs > 4000].sum() / (spec.sum() + 1e-9) > 0.5:
            out = audio[:i].copy()
            fade = int(0.04 * sr)
            out[-fade:] *= np.linspace(1, 0, fade)
            return out
    return audio


def main():
    model_dir, out_dir = map(pathlib.Path, sys.argv[1:3])
    out_dir.mkdir(parents=True, exist_ok=True)
    k = Kokoro(str(model_dir / 'kokoro-v1.0.onnx'), str(model_dir / 'voices-v1.0.bin'))
    for key, text in LINES.items():
        audio, sr = k.create(text, voice='pf_dora', speed=SPEED, lang='pt-br')
        if key == '2':
            audio = trim_breath(audio, sr)
        sf.write(out_dir / f'{key}.wav', audio, sr)


if __name__ == '__main__':
    main()
