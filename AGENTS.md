# AGENTS

Vault Obsidian + git (`n-huche/docs`). Fonte de anotações e planos.

Qualquer agente segue este arquivo, `agents/procedures/` e `agents/templates/`. Sem pasta de memória por ferramenta.

## Convenções

- Idioma dos **textos** do usuário: **português**.
- Nomes de **pastas e arquivos**: **inglês**, kebab-case, ASCII, sem espaços.
- Completo, mas enxuto; uma fonte da verdade por tema (não duplicar tabelas/rosters).
- Nunca usar `.gitkeep` nem placeholder para pasta vazia. No git, pasta só entra com nota. `projects/{status}/` (`pending`, `in-progress`, `paused`, `completed`), `tasks/{status}/` (`pending`, `completed`, `recurring`), `pending/{prazo}/`, `independent-tasks/`, `project-tasks/` e pastas de projeto/fase em `tasks/` só existem se tiverem nota.
- Links: `[nome](caminho relativo)` — não `[[wiki]]`.
- Ambiguidade factual ou de decisão → perguntar; não inventar dados pessoais.
- Nota de tipo conhecido: copiar o template em `agents/templates/`; não inventar outro esqueleto.

## Glossário

### Projeto

Resultado maior, partido em fases, objetivo em uma frase. **Não se executa** — o que se faz são tarefas. Sem tarefas relacionadas, é só plano.

Não é 1:1 com tarefa nem com fase: uma fase pode caber numa única tarefa ou pedir dezenas. O projeto acaba quando o objetivo é verdadeiro.

Pasta: `projects/{status}/{slug}/` (`pending` | `in-progress` | `paused` | `completed`; `{slug}.md`, `analysis/`, `phases/{prefixo}-{nn}-{slug-fase}.md`). Hub `{slug}.md` a partir de [project-template](agents/templates/project-template.md). Criar projeto: [new-project](agents/procedures/new-project.md). Fase nova em projeto existente: [new-phase](agents/procedures/new-phase.md). **Status** do projeto **herda** a primeira fase não-`concluído` no hub (por `nn`) e escolhe a pasta ([status-change](agents/procedures/status-change.md)). Ao herdar de novo, mover a árvore e atualizar links que saem dela; links *dentro* do projeto não mudam. **Prazo** só no markdown.

### Fase

Recorte com **uma entrega**. Status e prazo próprios no markdown; nenhum dos dois muda o caminho *dentro* do projeto. A pasta `projects/{status}/{slug}/` só muda quando a herança do projeto muda.

Criar em projeto existente: [new-phase](agents/procedures/new-phase.md). Planejada (`pendente` ou além): nota em `phases/{prefixo}-{nn}-{slug-fase}.md` ([phase-template](agents/templates/phase-template.md)), entrada no hub e **≥1 tarefa**. A nota traz **Entrega** (o quê) e **Como** (método, fontes, restrições) — escrita de forma que as tarefas derivadas já estejam definidas. Se o Como não der para derivar tarefas sem inventar, não criar as tarefas: analisar (se a complexidade justificar) ou perguntar. `não planejado`: só heading + status + prazo no hub — sem arquivo nem tarefas. Heading do hub em **português**; arquivo kebab em inglês. Recorrente sem fim **não** entra em fase.

Relação com tarefas não é 1:1: a fase decide o que fica pronto e como; as tarefas só compactam isso em ações de algumas horas. Uma fase planejada pode ter uma ou dezenas de tarefas. Fases são **sequenciais**. `em andamento`, `pausado` e `concluído` só se todas as `nn` menores estiverem `concluído`.

### Análise

Nota de **decisão**: responde qualquer pergunta. Fonte das seções: [analysis-template](agents/templates/analysis-template.md) (as mesmas para qualquer objeto; nem toda análise preenche todas). **Só quando a complexidade da fase justifica.** Uma ou mais, **normalmente antes** da fase a que servem: dados e pesquisa → o quê e o como que a fase descreve. Opcional. Pasta `analysis/` só nasce com arquivo. Slug **sem** id de fase (`fj-stack.md`, não `fj-01-stack.md`).

### Tarefa

Unidade de execução: **ação concreta, específica, no máximo algumas horas**. **Não traz nada de novo** — compacta e estrutura o que a fase (ou, se independente, a própria nota) já decidiu, visando fazer: o mínimo de pensar.

Pode ser **independente** (não depende de projeto) ou **relacionada a uma fase**. Fase planejada tem ≥1 tarefa; não é 1:1. Default ao criar: `pendente`. Campo **Prazo:** data `YYYY-MM-DD` ou `não definido` se `pendente`; `none` só se `recorrente` sem fim (**Quando** no corpo não vira Prazo). Tarefa de fase: default = copiar o prazo da fase. Independente `pendente`: `não definido` se o usuário não der data. Campo **Fase:** só se for de fase (link relativo). `pendente` → `tasks/pending/{prazo}/independent-tasks/{slug}.md` ou `…/project-tasks/{projeto}/{fase}/{slug}.md`. `concluído` → `tasks/completed/…` (sem `{prazo}/`). `recorrente` → `tasks/recurring/…` (sem `{prazo}/`). `{prazo}` em pending: `late` · `today` · `three-days` · `one-week` · `one-month` · `long-time` · `undefined`. Template [task-template](agents/templates/task-template.md). Criar: [new-task](agents/procedures/new-task.md). Tarefa de fase só pode ir a `concluído` se **todas** as tarefas das fases com `nn` menor no mesmo projeto já estiverem `concluído`.

Tarefa de fase em três lugares: o arquivo, um link em `{fase}.md`, um checkbox em [tasks](tasks/tasks.md). Independente: sem **Fase:**. Checkbox só no índice. **O quê** = passos extraídos da Entrega + Como da fase. Se a fase não disser, não entra na tarefa.

### Prazo

Campo em projeto, fase e tarefa `pendente`: `YYYY-MM-DD` ou `não definido`. Recorrente sem fim: `none`. Pai da fase = projeto. Pai da tarefa de fase = fase. Independente não herda. Criar filho: copiar o prazo do pai. Override: o usuário (ou pedido ao agente) põe outro valor no filho. Mudar o prazo do pai: cascatear só nos filhos cujo prazo é **igual ao valor antigo do pai** ou **`não definido`** (`none` não cascateia). **Prazo específico na fase:** as tarefas dessa fase **sem** prazo próprio (`não definido` ou ainda igual ao prazo antigo da fase) herdam a data; tarefa com data diferente ou `none` não mexe. **Quando** não vira Prazo.

Em **tarefa** `pendente`, o prazo escolhe a pasta **dentro de** `pending/`. `não definido` → `undefined/`. Com data, dias até ela (hoje = 0; atrasada negativa): `< 0` `late/` · `0` `today/` · `1–3` `three-days/` · `4–7` `one-week/` · `8–30` `one-month/` · `> 30` `long-time/`. Recalcular vs hoje ao criar, ao mudar Prazo/Status, ou ao usar a lista. `concluído` e `recorrente` saem de `pending/{prazo}/`. Voltar a `pendente`: recalcular o balde. Projeto e fase **não** têm pasta de prazo.

### Tarefa recorrente

Todos, ou quase todos, os dias. Status `recorrente`; pasta `tasks/recurring/` (sem `{prazo}/`). **Prazo:** `YYYY-MM-DD` = último dia — quando hoje ≥ essa data → `concluído`. Sem fim: **Prazo:** `none` — só independente. Com data: pode ser de fase e conta no auto-`concluído` da fase. Deixar de ser recorrente = sai de `recurring/` e segue [status-change](agents/procedures/status-change.md).

### Daily

Notas diárias (em construção). Pasta `daily/`. Template: [day-template](agents/templates/day-template.md).

### Status

Projeto: campo **e** pasta `projects/{status}/`, 1:1 com a herança. Fase: campo no markdown (e o heading no hub). Tarefa: campo **e** pasta, 1:1. Mudar: [status-change](agents/procedures/status-change.md).

Tarefa: `pendente` | `concluído` | `recorrente` → `pending/` · `completed/` · `recurring/`. Fase: `pendente` | `em andamento` | `pausado` | `concluído` | `não planejado`. Projeto: `pendente` | `em andamento` | `pausado` | `concluído` (herdado; nunca `não planejado`). Pastas do projeto: `pending/` · `in-progress/` · `paused/` · `completed/`.

Herança (hub por `nn`, primeira não-`concluído`): `em andamento` / `pausado` / `pendente` → o projeto copia; `não planejado` → projeto `pendente`; se **todas** as fases do hub estão `concluído` (sem heading `não planejado`) → projeto `concluído`.

Gate da fase: `em andamento`, `pausado` e `concluído` só se todas as `nn` menores estiverem `concluído`; recusar se faltar. Com o gate ok, pela ordem de `## Tarefas`: primeira tarefa `concluído` e ainda há outras → fase `em andamento`; **todas** `concluído` (inclui recorrente com data) → fase `concluído` (uma única tarefa na fase: `pendente` → `concluído`). `pausado` só se o usuário pedir. Depois herdar no projeto (mover pasta se mudou).

`não planejado` = só **fase**: ainda não vale arquivo nem tarefas (heading no hub, sem nota em `phases/`). `pausado` = já vale, mas parou.

### Índice e hub

Índice: lista curta (link + blurb). Só o heading que tiver item; sem `--`. [projects](projects/projects.md): **Pendente · Em andamento · Pausado · Concluído**. [tasks](tasks/tasks.md): **Recorrentes · Atrasadas · Hoje · Três dias · Uma semana · Um mês · Longo prazo · Sem prazo** (pendentes e recorrentes; concluídas saem). Hub: nota-índice com o mesmo slug da pasta.
