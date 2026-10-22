# Marketing Skills

Este repositório é a oficina de **marketing**. As skills ficam em `.claude/skills/`.

## Como responder

- O usuário escreve em **português do Brasil**: responda sempre em português, mesmo que a skill esteja escrita em inglês. Termos técnicos podem ficar em inglês quando não houver tradução comum, com uma explicação curta na primeira vez.
- O usuário tem conhecimento **intermediário**: comece com uma explicação curta do que vai ser feito e por quê, depois entregue o trabalho principal. Textos claros, completos e didáticos.
- Em estratégias e planos, seja o mais avançado e completo possível.
- **Não invente informações.** Se um dado não puder ser verificado (preço, número, fato, fonte), diga que não sabe ou que está no limite do seu conhecimento.

## Como escolher a skill

- Os pedidos chegam em português; as descrições das skills estão em inglês. Use o mapa abaixo para traduzir o pedido na skill certa.
- Se o pedido não bater claramente com uma skill, comece pelo **roteador** indicado no mapa: ele escolhe a especialista.
- Diga ao usuário, em uma linha, qual skill está usando e por quê.

## Arquivos gerados

Sessões na nuvem são apagadas ao terminar. Quando uma skill gerar um arquivo que valha guardar (relatório, plano, contexto), salve-o dentro deste repositório e ofereça fazer commit.

## Mapa de pedidos

Antes de qualquer trabalho de marketing num projeto novo, rode `marketing-context` (cria o perfil da marca que as outras skills leem). Roteadores: `marketing-ops` (coordena campanhas e escolhe a skill), `marketing-skills` (índice), `linkedin-skills` (tudo de LinkedIn).

| Pedido em português | Skill |
|---|---|
| "escreve um post/artigo/blog" | `content-production` |
| "plano de conteúdo", "sobre o que escrever", "calendário editorial" | `content-strategy` |
| "texto para a página", "headline", "chamada para ação" | `copywriting` |
| "revisa meu texto", "melhora esse texto" | `copy-editing` |
| "está com cara de IA", "deixa mais humano" | `content-humanizer` |
| "post para Instagram/TikTok/redes" | `social-content` |
| "estratégia de redes sociais" | `social-media-manager` |
| "como foram meus posts/engajamento" | `social-media-analyzer` |
| "crescer no X/Twitter", "thread" | `x-twitter-growth` |
| "LinkedIn" (perfil, post, estratégia, conexões, métricas) | `linkedin-skills` |
| "YouTube", "roteiro de vídeo", "Reels/Shorts" | `video-content-strategist`; transcrição/busca no YouTube: `youtube-full` |
| "monta um vídeo com essas fotos/vídeos", "edita um anúncio/reel a partir desse material" (arquivo real de saída) | `ad-video-assembly` |
| "sequência de e-mails", "e-mail de boas-vindas", "nutrição" | `email-sequence` |
| "e-mail frio", "prospecção" | `cold-email` |
| "anúncios", "Google Ads/Meta Ads", "tráfego pago" | `paid-ads`; só os textos/criativos: `ad-creative` |
| "auditoria de SEO", "por que não ranqueio" | `seo-audit` |
| "aparecer no ChatGPT/Perplexity", "AEO" | `aeo` |
| "SEO local", "Google Meu Negócio" | `local-seo-manager` |
| "página não converte", "CRO" | `page-cro` (formulário: `form-cro`; pop-up: `popup-cro`; cadastro: `signup-flow-cro`) |
| "teste A/B" | `ab-test-setup` |
| "precificação", "planos e preços" | `pricing-strategy` |
| "lançamento", "go-to-market" | `launch-strategy` |
| "posicionamento", "público-alvo/ICP" | `marketing-strategy-pmm` |
| "concorrentes", "página X vs Y" | `competitor-alternatives` |
| "ideias de marketing" | `marketing-ideas` |
| "landing page" | `landing` |
| "nome para a empresa/produto" | `business-name-fit` |
| "manual da marca", "tom de voz" | `brand-guidelines` |
| "ROI da campanha", "atribuição" | `campaign-analytics` |
| "GA4", "Tag Manager", "rastreamento" | `analytics-tracking` |
