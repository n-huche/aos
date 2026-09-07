# Novo projeto

Não inventar domínio, datas, pessoas nem fases. Sem `.gitkeep`. Hub a partir de [project-template](../templates/project-template.md). Análise, se houver, a partir de [analysis-template](../templates/analysis-template.md). Fase a partir de [phase-template](../templates/phase-template.md). Pasta só com nota dentro.

| Campo | Pasta |
|---|---|
| `não iniciado` \| `pausado` | `projects/pending/{domínio}/` |
| `em andamento` | `projects/in-progress/{domínio}/` |
| `concluído` | `projects/completed/{domínio}/` |

Domínio = **finalidade** ([glossário](../../AGENTS.md)): `money` · `relationships` · `body`. Não o tema aparente.

## Antes de criar

1. Confirmar que não existe projeto no mesmo fim (buscar slug, nome, pasta). Se existir, atualizar o que já está — não duplicar.
2. Se faltar **domínio**, **objetivo em uma frase**, **slug** ou **fases**, perguntar. Default de status: `não iniciado` → `pending/`, salvo o usuário dizer outro. Projeto **não** usa `não planejado` — isso é só fase. Análise: só se a complexidade de uma fase justificar (usuário pediu ou já trouxe a decisão) — **antes** dessa fase.
3. Slug da pasta = slug do hub = inglês, kebab-case, ASCII. Título do hub pode ser o nome falado (ex.: First Job, Ana Year One). Textos em português.
4. Prefixo de fase: sigla curta em maiúsculas (ex.: `FJ`, `AY1`). Heading no hub **e** arquivo: `{PREFIXO}-{nn}-{slug-fase}` / `{prefixo}-{nn}-{slug-fase}.md` — slug da fase em inglês nos dois.

## Criar

1. Pasta `projects/{status}/{domínio}/{slug}/`. Não criar `projects/{status}/{domínio}/` se for ficar vazia além deste projeto — a pasta do domínio nasce com o slug.
2. Hub `{slug}.md` pelo template. Preencher objetivo e **Status geral**. **Análise:** `_(ainda não)_` até existir nota; slug curto **sem** id de fase (`fj-stack.md`). Não criar `analysis/` vazia nem `{{slug}}-analysis.md` placeholder.
3. Análise, se necessária: nota em `analysis/` ([analysis-template](../templates/analysis-template.md)); slug **sem** id de fase. Pasta `analysis/` nasce com o primeiro arquivo. Implicações = o quê/como da fase.
4. Cada fase **planejada** (`não iniciado` ou além): nota em `phases/{prefixo}-{nn}-{slug-fase}.md` (copiar [phase-template](../templates/phase-template.md); **Entrega** + **Como**; campos extras só se o usuário trouxe conteúdo) e entrada no hub. Se o Como não der para derivar tarefas sem inventar, perguntar — não criar as tarefas ainda. Depois **≥1 tarefa** (seguir [new-task](new-task.md); compactar a fase, não inventar). Fase `não planejado`: só heading + status no hub — **sem arquivo nem tarefas**.
5. Conteúdo longo fica na fase, não no hub.
6. Não criar `learning-method.md`, spec extra, nem outras notas “por se acaso”. Itens de portfólio (se houver) ficam no **corpo da fase**, não em nota à parte.
7. Em [projects](../../projects/projects.md): na seção de status + domínio, item `- [{Nome}]({status}/{domínio}/{slug}/{slug}.md) — {blurb}`. Trocar `--` se a seção estava vazia.
8. Links `[nome](caminho relativo)` — não `[[wiki]]`. Buscar no vault menções ao tema e apontar para o hub quando fizer sentido.

Mudança de status **depois** de criado: [status-change](status-change.md).
