#!/usr/bin/env bash
# Gera o anúncio completo de um cliente: narração, vídeos A e B com trilha mixada, e capas.
# Uso: TTS_PY=<python com kokoro-onnx> KOKORO_DIR=<pasta dos modelos> ./fazer.sh <pasta do cliente>
set -euo pipefail

KIT="$(cd "$(dirname "$0")" && pwd)"
CLIENT="$(cd "$1" && pwd)"
NAME="$(basename "$CLIENT")"
: "${TTS_PY:?defina TTS_PY (python com kokoro-onnx)}"
: "${KOKORO_DIR:?defina KOKORO_DIR (kokoro-v1.0.onnx e voices-v1.0.bin)}"

"$TTS_PY" "$KIT/narracao.py" "$KOKORO_DIR" "$CLIENT"
for v in A B; do
  NODE_PATH="$(npm root -g)" node "$KIT/render.js" "$CLIENT" video "$v"
  python3 -I "$KIT/audio.py" "$v" "$CLIENT/narracao"
  ffmpeg -y -loglevel error -i "$CLIENT/out/video-$v-sem-som.mp4" -i "$CLIENT/out/trilha-$v.wav" -c:v copy \
    -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart "$CLIENT/$NAME-$v.mp4"
  ffmpeg -y -loglevel error -ss 1.8 -i "$CLIENT/$NAME-$v.mp4" -frames:v 1 -q:v 2 "$CLIENT/capa-$v.jpg"
  echo "pronto: $CLIENT/$NAME-$v.mp4"
done
