# Galeria dos Pães — análise do vídeo e guia da proposta

Documento **interno** (para você, não para a padaria). A versão para mostrar ao cliente é a página de proposta.

- Vídeo analisado: `galeria-dos-paes-video.mp4` (v1, 22 s, 1080×1920, 30 fps, trilha de piano elétrico sintetizada, sem narração).
- Versão melhorada: `galeria-dos-paes-v2-reels.mp4` (9:16) e `galeria-dos-paes-v2-feed.mp4` (4:5), 15,8 s cada. Gerados por `montar_v2.py`.
- Grau de confiança: o que está marcado como **[verificado]** eu medi no arquivo; **[opinião de especialista]** é julgamento profissional; **[confira]** é informação de plataforma que muda com frequência e deve ser checada antes de prometer ao cliente.

---

## 1. Resumo em uma frase

O v1 tem uma boa ideia (gancho sensorial + narrativa "pão → forno → café → café da manhã → marca"), mas é lento, mostra a marca tarde demais e, principalmente, **usa imagens de banco que não são da padaria** — inclusive uma plaquinha em dinamarquês com preço em coroas. Ele serve como **demonstração** para vender o serviço, não como vídeo para publicar.

---

## 2. Linha do tempo do v1 (o que aparece em cada segundo) [verificado]

| Tempo | Imagem | Texto na tela |
|---|---|---|
| 0,0–2,7 s | Doces assados em tábuas (clipe de 720p ampliado, um pouco "mole") | "Sentiu o cheirinho de pão quente?" (entra com fade após ~0,25 s) |
| 2,7–4,5 s | Mão tatuada sovando massa, plano escuro e desfocado | mesmo texto |
| 4,5–6,0 s | Mulher abrindo forno | "Fresquinho, saindo do forno." |
| 6,0–7,8 s | Mãos (manga rosa) sobre pão trançado | mesmo texto |
| 7,8–9,3 s | Mãos partindo croissant | mesmo texto |
| 9,5–11,0 s | Compactando café | "E um cafezinho pra acompanhar." |
| 11,0–12,5 s | Café saindo da máquina | mesmo texto |
| 12,7–14,5 s | Latte art | mesmo texto |
| 14,7–16,3 s | Mesa de café da manhã vista de cima | "Seu café da manhã começa aqui." |
| 16,5–18,2 s | Vitrine desfocada, com placa **"LILLE CREME SNEGL 15 KR."** | "Galeria dos Pães" |
| 18,2–22,0 s | Cartão final creme: nome, "Padaria & Delicatessen", botão "Venha nos visitar", endereço, "Imagens ilustrativas · Mixkit" | — |

Áudio: trilha contínua, mono (os dois canais são idênticos), volume médio -16 dB, sem voz. [verificado]

---

## 3. O que está bom no v1 (manter)

1. **Formato certo**: vertical 1080×1920, 30 fps — é o padrão de Reels/Stories. [verificado]
2. **Gancho sensorial**: "Sentiu o cheirinho de pão quente?" faz a pessoa *imaginar o cheiro*. É um bom gancho para comida. [opinião de especialista]
3. **Narrativa simples e correta**: produto → frescor → acompanhamento → momento de consumo → marca → ação. Uma ideia por vídeo, como recomenda a boa prática de vídeo curto.
4. **Texto legível**: fonte limpa, branca, com degradê escuro atrás. Funciona sem som.
5. **Identidade visual coerente**: paleta creme/marrom/caramelo combina com padaria.
6. **Honestidade e licença**: crédito "Imagens ilustrativas · Mixkit". Segundo o `FONTES.md`, a licença do Mixkit permite uso comercial e em anúncios sem crédito obrigatório [confira em mixkit.co/license antes de usar comercialmente].
7. **Trilha própria**: a música é gerada pelo script, então não há risco de direitos autorais nem de o Instagram silenciar o áudio. [verificado no código]

---

## 4. Problemas encontrados (em ordem de gravidade)

### Graves

1. **Não é a padaria.** Todos os planos são de banco de imagens. Para um negócio de bairro, o cliente vai até a loja esperando ver aquele croissant, aquele forno, aquela mesa. Se não encontrar, o vídeo gera frustração em vez de confiança. → Por isso a proposta é **gravar na padaria**; o vídeo atual é o "modelo".
2. **Placa em dinamarquês com preço em coroas** ("LILLE CREME SNEGL 15 KR.") aos ~16 s. Qualquer pessoa que pause o vídeo percebe que não é Vilas do Atlântico. Se a padaria vir isso na apresentação, a credibilidade do seu trabalho cai. [verificado no quadro de 16,5 s]
3. **A marca só aparece aos 16,5 s** (75% do vídeo). Em anúncio, quem desliza antes disso viu um vídeo bonito de pão — mas não sabe de quem. [verificado]

### Médios

4. **Ritmo lento**: todos os cortes são dissoluções de 0,35 s, e os cortes não caem no tempo da música. Em vídeo curto, a dissolução repetida dá sensação de "apresentação de slides". [opinião de especialista]
5. **Plano escuro com mão tatuada** (2,7–4,5 s): desfocado, pouco apetitoso, e a tatuagem de rosto puxa o olhar para longe do produto. Fica justamente nos primeiros segundos, onde a pessoa decide se continua.
6. **O primeiro quadro é o clipe mais fraco tecnicamente**: o clipe de doces só existe em 720p no Mixkit e foi ampliado para 1920 px de altura. [verificado: o arquivo 1080p retorna erro 403, só o 720p está disponível]
7. **Cartão final parado por 4 s** (18% do vídeo) com CTA genérico ("Venha nos visitar"). Tela estática no fim convida a deslizar antes do endereço ser lido.
8. **Colagem perceptível**: três "padeiros" diferentes (mão tatuada, mulher de jaleco, manga rosa). Reforça a sensação de vídeo genérico.

### Leves / técnicos

9. **Só existe em 9:16**. Para anúncio no feed, o formato 4:5 ocupa mais tela que o quadrado e é o recomendado pela Meta para feed [confira as especificações atuais no Guia de Anúncios da Meta].
10. **Posição do texto em anúncios de Reels**: o texto ficava entre 63% e 73% da altura. Em anúncios de Reels, a Meta recomenda deixar livre uma faixa inferior (onde ficam legenda, nome do perfil e botão de ação) — a referência que conheço é algo em torno dos 35% de baixo e 14% de cima [confira: esses números são do meu conhecimento e podem ter mudado].
11. **O gancho entra com fade** (~0,25 s). Pequeno, mas o primeiro quadro precisa já ter o texto.

---

## 5. O que mudou no v2 (e por quê)

| # | Mudança | Por quê |
|---|---|---|
| 1 | Abre no **croissant sendo partido**, com o texto já no primeiro quadro | Movimento + textura + gancho imediato = melhor chance de parar a rolagem |
| 2 | **Removidos** o plano tatuado escuro e a vitrine com a placa dinamarquesa | Eram os dois planos mais fracos e o segundo era um risco de credibilidade |
| 3 | **Cortes secos no tempo da música** (76 bpm, um corte a cada 2 batidas ≈ 1,58 s) | Ritmo mais rápido e "musical"; 22 s → 15,8 s |
| 4 | **Selo "GALERIA DOS PÃES" no topo** durante todo o vídeo | A marca está presente desde o segundo zero (essencial em anúncio) |
| 5 | **Palavras-chave em dourado** ("pão quente", "saindo do forno", "delícias", "cafezinho", "começa aqui") e fonte maior em negrito | Leitura mais rápida, hierarquia clara sem som |
| 6 | Novo bloco **"Pães, doces e delícias."** sobre os doces | Mostra variedade (a padaria é também delicatessen) |
| 7 | Cena do forno reenquadrada (a pessoa aparece), latte art reenquadrado (aparece o coração) | No primeiro teste do v2 o enquadramento mostrava só a porta do forno |
| 8 | **Correção de cor mais quente** (saturação +12%, contraste +5%, leve puxada para o âmbar) | Pão e café ficam mais apetitosos |
| 9 | **Cartão final mais curto** (≈3,2 s), CTA **"Passa aqui hoje"**, ícone de localização, linha "Pães · doces · café da manhã" | CTA mais direto e coloquial; endereço com ícone é escaneado mais rápido |
| 10 | Rodapé "Modelo de demonstração · imagens ilustrativas (Mixkit)" | Deixa claro para a padaria que é um modelo — protege você |
| 11 | Texto subido para ~47% da altura no 9:16 | Fica fora da faixa coberta pela interface em anúncios de Reels |
| 12 | **Versão 4:5** para feed e anúncios de feed | Um vídeo, dois posicionamentos |
| 13 | Volume normalizado em -14 LUFS (medido: -13,7) | Volume consistente com outros vídeos da plataforma [verificado] |

### Limites do v2 (seja transparente com a padaria)

- Continua sendo **imagem de banco**. O salto real de qualidade vem de gravar os produtos dela.
- Não tem **narração** nem **som real** (crocância do pão, máquina de café). Com gravação na loja, dá para captar esse som — é um dos recursos mais fortes em vídeo de comida [opinião de especialista].
- A cena do forno mostra um forno industrial de marca específica; na gravação real, use o forno da padaria.

---

## 6. Como apresentar para a padaria (roteiro de ~15 minutos)

1. **Abra com o vídeo** (Reels, no celular, com som). Não explique antes — deixe a pessoa sentir.
2. **Pergunte**: "Imagina isso com o *seu* croissant, o *seu* forno, a *sua* equipe?" — e explique que este é um modelo feito com imagens ilustrativas.
3. **Mostre a anatomia** (seção "Por que funciona" da página): gancho, ritmo, marca o tempo todo, CTA.
4. **Mostre os dois formatos** (Reels e feed) e explique que um mesmo material vira post orgânico e anúncio.
5. **Apresente os pacotes** e deixe o intermediário como recomendação.
6. **Feche com um próximo passo pequeno**: uma gravação piloto (1 manhã) com X vídeos entregues. Pequeno compromisso, decisão fácil.

### Objeções prováveis e respostas

| Objeção | Resposta |
|---|---|
| "Eu mesmo gravo com o celular." | Ótimo para o dia a dia (stories). O pacote cuida do que dá mais trabalho: roteiro com gancho, edição no ritmo, legendas, formato de anúncio e constância. |
| "Já tenho Instagram e não vende." | Postar foto do produto não é o mesmo que vídeo com gancho e chamada para ação. A proposta inclui métricas para ver o que funciona. |
| "Anúncio é caro." | O orçamento de mídia é definido por vocês e pago direto à Meta; começa pequeno, com teste, e só aumenta o que der resultado. |
| "E se não der resultado?" | Por isso começar com piloto e medir (visualizações, salvamentos, mensagens, cupom na loja). |

**Não prometa números** (seguidores, vendas). Prometa entregáveis, constância e medição.

---

## 7. Como precificar (método, sem inventar valores)

Eu **não tenho dados confiáveis** de quanto se cobra hoje por vídeo para pequenos negócios em Lauro de Freitas/Salvador — está fora do que consigo verificar. Para chegar no seu preço:

1. **Calcule seu custo-hora**: quanto você quer ganhar por mês ÷ horas que você realmente consegue faturar (normalmente bem menos que 160 h).
2. **Estime horas por pacote**: gravação (deslocamento + 2–3 h na loja) + edição (≈1–2 h por vídeo curto, depois que o modelo está pronto) + legendas/publicação + reunião/relatório mensal.
3. **Preço = horas × custo-hora + margem** (imprevistos, refação).
4. **Pesquise o mercado local**: peça orçamento a 2–3 social medias/videomakers da região e veja perfis de freelancers locais. Posicione-se no meio, com o diferencial do método (gancho + ritmo + anúncio + métrica).
5. **Gestão de anúncios** é cobrada à parte do orçamento de mídia. Deixe claro por escrito que a verba da Meta é paga pela padaria.

Se você me disser seu custo-hora desejado, eu monto a tabela dos três pacotes com os valores.

---

## 8. Legenda sugerida para o post (quando for com imagens reais)

> Sentiu o cheirinho daqui? 🥐☕
> Pão fresquinho saindo do forno e aquele cafezinho pra acompanhar.
> 📍 Av. Praia de Itapoan · Vilas do Atlântico
> Marca aqui quem vai te acompanhar no café da manhã 👇

(Ajuste horário de funcionamento e produtos reais — não coloquei porque não sei quais são.)

### Textos para o anúncio (Meta)

- **Texto principal A (sensorial):** "Sentiu o cheirinho? Pão quentinho e café passado na hora, aqui em Vilas do Atlântico."
- **Texto principal B (momento):** "Seu café da manhã começa aqui. Pães, doces e café na Av. Praia de Itapoan."
- **Título:** "Galeria dos Pães · Vilas do Atlântico"
- **Botão:** "Como chegar" ou "Enviar mensagem" (se usarem WhatsApp) [confira quais botões estão disponíveis para o objetivo escolhido].

Teste A × B com o mesmo vídeo e veja qual texto traz mais cliques/mensagens.

---

## 9. Próximas melhorias possíveis

- **Versão com narração** usando o kit em `videos/_kit` (voz feminina em português).
- **Duas versões de gancho** para teste A/B em anúncio: "Sentiu o cheirinho de pão quente?" × "Seu café da manhã começa aqui."
- **Vídeo de 6–8 s** só com croissant + marca + endereço, para anúncio de alcance.
- Com gravação real: som da crocância, rosto da equipe, fornada da manhã com horário real na tela.

## 10. Como reproduzir

```
cd videos/galeria-dos-paes-video
# baixe os clipes listados em FONTES.md para clipes/ (doces-assados só existe em -720.mp4)
python montar_v2.py
```
