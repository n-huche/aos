# Novo projeto

Não inventar datas, pessoas nem fases. Sem `.gitkeep`. Hub a partir de [project-template](../templates/project-template.md). Análise, se houver, a partir de [analysis-template](../templates/analysis-template.md). Fase a partir de [phase-template](../templates/phase-template.md). Pasta só com nota dentro. Status de pasta: `projects/{pending|in-progress|paused|completed}/{slug}/`.

## Antes de criar

1. Confirmar que não existe o mesmo projeto (buscar slug, nome, pasta). Se existir, atualizar o que já está — não duplicar.
2. Se faltar **objetivo em uma frase**, **slug** ou **fases**, perguntar. Default de **Status:** `pendente` (herdado: primeira fase não-`concluído` é `pendente` ou `não planejado`, ou ainda não há fases) → `projects/pending/{slug}/`. Default de **Prazo:** `não definido` — não inventar data. Projeto **não** usa `não planejado` — isso é só fase. Análise: só se a complexidade de uma fase justificar (usuário pediu ou já trouxe a decisão) — **antes** dessa fase.
3. Slug da pasta = slug do hub = inglês, kebab-case, ASCII. Título do hub pode ser o nome falado (ex.: First Job, Ana Year One). Textos em português.
4. Prefixo de fase: sigla curta em maiúsculas (ex.: `FJ`, `AY1`). Arquivo: `{prefixo}-{nn}-{slug-fase}.md` (slug em inglês). Heading no hub em **português** (ex.: `### FJ-01 — estudo`).

## Criar

1. Pasta `projects/pending/{slug}/` (default `pendente`).
2. Hub `{slug}.md` pelo template. Preencher objetivo, **Status** (`pendente` até a herança mudar) e **Prazo**. **Análise:** `_(ainda não)_` até existir nota; slug curto **sem** id de fase (`fj-stack.md`). Não criar `analysis/` vazia nem `{{slug}}-analysis.md` placeholder.
3. Análise, se necessária: nota em `analysis/` ([analysis-template](../templates/analysis-template.md)); slug **sem** id de fase. Pasta `analysis/` nasce com o primeiro arquivo. Implicações = o quê/como da fase.
4. Cada fase **planejada** (`pendente` ou além): nota em `phases/{prefixo}-{nn}-{slug-fase}.md` (copiar [phase-template](../templates/phase-template.md); **Entrega** + **Como**; **Prazo** = copiar o do projeto; campos extras só se o usuário trouxe conteúdo) e entrada no hub (heading em português, mesmo **Status** e **Prazo**). Se o Como não der para derivar tarefas sem inventar, perguntar — não criar as tarefas ainda. Depois **≥1 tarefa** (seguir [new-task](new-task.md); compactar a fase, não inventar). Fase `não planejado`: só heading em português + **Status** + **Prazo** no hub — **sem arquivo nem tarefas**. **Prazo** da fase não planejada = copiar o do projeto.
5. Conteúdo longo fica na fase, não no hub.
6. Não criar spec extra nem outras notas “por se acaso”. Itens de portfólio (se houver) ficam no **corpo da fase**, não em nota à parte.
7. Em [projects](../../projects/projects.md): na seção do status herdado (**Pendente · Em andamento · Pausado · Concluído**), item `- [{Nome}]({status}/{slug}/{slug}.md) — {blurb}` (default `pending/{slug}/{slug}.md`). Se o `##` não existir, inserir nessa ordem. Sem `--`; heading só com item.
8. Links `[nome](caminho relativo)` — não `[[wiki]]`. Buscar no vault menções ao tema e apontar para o hub quando fizer sentido.

Fase **depois** de o projeto existir: [new-phase](new-phase.md). Mudança de status ou prazo: [status-change](status-change.md).
