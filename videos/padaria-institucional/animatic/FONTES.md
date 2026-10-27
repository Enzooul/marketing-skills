# Fontes do animatic

**Isto é um animatic, não o vídeo final.** As imagens são clipes de referência para aprovar ritmo, textos e música. O vídeo final é filmado na padaria, como manda o briefing (`../briefing-video-institucional-v2.md`). Em alguns clipes de referência aparecem situações que **não podem** existir na filmagem real, como pessoas sem touca na cozinha e letreiros de terceiros (o plano 1 foi desfocado por isso).

Todos os clipes vêm do Mixkit, sob a **Mixkit Stock Video Free License** (https://mixkit.co/license/#videoFree). Os arquivos ficam fora do Git. Para baixar de novo: `https://assets.mixkit.co/videos/<id>/<id>-720.mp4`, salvo como `clipes/<nome>.mp4`. Depois rode `python montar.py clipes`.

| Nome | ID Mixkit | Plano | Página |
|---|---|---|---|
| rua | 41160 | P1 | https://mixkit.co/free-stock-video/streets-of-a-big-city-at-night-41160/ |
| cozinha | 43048 | P2 | https://mixkit.co/free-stock-video/chef-working-in-a-large-kitchen-43048/ |
| farinha | 48053 | P3 | https://mixkit.co/free-stock-video/slow-motion-sifting-flour-through-a-metal-sieve-48053/ |
| sovando | 42467 | P4 | https://mixkit.co/free-stock-video/hands-of-a-baker-kneading-a-dough-42467/ |
| farinha-mesa | 42463 | P4 | https://mixkit.co/free-stock-video/baker-preparing-the-flour-on-a-table-42463/ |
| formando | 42466 | P5 | https://mixkit.co/free-stock-video/experienced-baker-forming-a-dough-42466/ |
| crescendo2 | 6787 | P6 | https://mixkit.co/free-stock-video/bread-growing-inside-the-oven-6787/ |
| bolo-forno | 10336 | P7 | https://mixkit.co/free-stock-video/putting-a-cake-to-bake-seen-from-inside-the-oven-10336/ |
| abre-forno | 50031 | P8 | https://mixkit.co/free-stock-video/pastry-chef-opening-her-professional-preheated-oven-50031/ |
| pitas | 19558 | P8 | https://mixkit.co/free-stock-video/cook-taking-pitas-out-of-the-oven-19558/ |
| croissant | 3082 | P9 | https://mixkit.co/free-stock-video/hands-splitting-a-croissant-in-half-3082/ |
| cobertura | 50017 | P10 | https://mixkit.co/free-stock-video/expert-pastry-chef-covering-a-cake-with-icing-50017/ |
| bolo-corte | 41120 | P10 | https://mixkit.co/free-stock-video/cutting-a-little-chocolate-cake-41120/ |
| vitrine | 21927 | P11 | https://mixkit.co/free-stock-video/baked-goods-in-a-bakery-display-21927/ |
| cafe | 43941 | P13 | https://mixkit.co/free-stock-video/pouring-coffee-in-a-cup-43941/ |
| garcom | 205 | P13 | https://mixkit.co/free-stock-video/a-waiter-serves-coffee-to-a-customer-205/ |

P12 (porta abrindo e clientes) não tinha referência adequada e aparece como um cartão desenhado. P14 é a tela final com os campos a preencher.

A trilha e os efeitos sonoros foram sintetizados no `montar.py` só para marcar a estrutura da música (quase silêncio, crescimento, respiro, volta cheia e final) e os pontos de sincronia, como o estalo da casca em 0:17. **Não é a música do vídeo**: a faixa final sai de um banco licenciado (seção 7.1 do briefing).
