# Kit de anúncio em vídeo

Gera um anúncio vertical de 18 s (1080×1920) para um cliente, em duas versões de gancho (A e B) para teste, com narração feminina em português e trilha de violão. O vídeo, a narração e a trilha saem de um único arquivo de configuração.

## Novo cliente

1. Crie uma pasta em `videos/<cliente>/` com uma subpasta `fotos/`.
2. Coloque de 5 a 8 fotos do cliente em `fotos/` (e o logo, se houver). Fotos horizontais ou pequenas funcionam: o modelo usa fundo desfocado quando a foto não preenche a tela.
3. Copie `videos/galeria-dos-paes/config.js` para a pasta nova e troque nome, cores, textos, narração, fotos e contato.
4. Rode:

   ```
   TTS_PY=<python com kokoro-onnx> KOKORO_DIR=<modelos do Kokoro> videos/_kit/fazer.sh videos/<cliente>
   ```

   Saem `<cliente>-A.mp4`, `<cliente>-B.mp4`, `capa-A.jpg` e `capa-B.jpg` na pasta do cliente.

## Limites de tempo da narração

Cada fala precisa caber na cena. O `narracao.py` acelera um pouco a voz quando a fala passa do limite e avisa se mesmo assim não couber:

| Fala | Cena | Máximo |
|---|---|---|
| gancho (A e B) | 0–2,9 s | 2,6 s |
| cena2 | 2,9–5,8 s | 2,7 s |
| cena3 | 5,8–8,7 s | 2,7 s |
| grade | 8,7–12,2 s | 3,2 s |
| destaque | 12,2–15 s | 3,1 s |
| cta | 15–18 s | 2,0 s |

## Arquivos

- `modelo.html` — a animação; lê `config.js` da pasta do cliente.
- `render.js` — renderiza o vídeo quadro a quadro (Playwright + ffmpeg).
- `narracao.py` — gera as falas (Kokoro, voz `pf_dora`, licença Apache-2.0).
- `audio.py` — gera a trilha, abaixa a música sob a voz e mixa.
- `fazer.sh` — roda tudo na ordem.
