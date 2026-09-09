# Novo projeto

Não inventar datas, pessoas nem fases. Pasta só com nota.

1. Identidade

   Já existe (slug, nome ou pasta) → não duplicar; atualizar o que já está; parar.
   Faltar objetivo em uma frase, `{slug}` ou fases → perguntar; não gravar.

2. `{slug}` · `{prazo}` · `{PREFIXO}`

   `{slug}` = pasta = arquivo do hub = kebab inglês ASCII.
   Título do hub = nome falado.
   `{prazo}` = `não definido` — não inventar. Filho copia, salvo o pedido ter data.
   `{PREFIXO}`: sigla curta em maiúsculas a partir do nome. Faltar → perguntar. Gravar **Prefixo:** no hub (as fases leem daí se `## Fases` ainda está vazio).
   Projeto nunca usa `não planejado`.

3. Hub

   Pasta `projects/pending/{slug}/`.
   Hub `{slug}.md` a partir de [project-template](../templates/project-template.md). **Objetivo**, **Status:** `pendente`, **Prazo:** `{prazo}`, **Prefixo:** `{PREFIXO}`, **Análise:** `_(ainda não)_`. `## Fases` sem placeholders — entram no passo 4.
   Análise só se a complexidade de uma fase justificar — **antes** dessa fase; [new-analysis](new-analysis.md). Senão não criar `analysis/`.

4. Fases

   Cada fase do pedido → [new-phase](new-phase.md). Não chamar [new-task](new-task.md).
   Conteúdo longo na fase, não no hub.

5. **Herança**

   [new-phase](new-phase.md) **Herança**. Default da pasta = `pending` até a herança mudar.

Pedido posterior de status: [new-phase](new-phase.md) **Herança**. Fase nova depois de o projeto existir: [new-phase](new-phase.md).
