# AGENTS

Vault Obsidian + git (`n-huche/docs`). Fonte de anotações e planos.

Qualquer agente segue este arquivo, `agents/procedures/` e `agents/templates/`. Sem pasta de memória por ferramenta.

## Convenções

- Idioma dos **textos** do usuário: **português**.
- Nomes de **pastas e arquivos**: **inglês**, kebab-case, ASCII, sem espaços.
- Completo, mas enxuto; uma fonte da verdade por tema (não duplicar tabelas/rosters).
- Nunca usar `.gitkeep` nem placeholder para pasta vazia. No git, pasta só entra com nota. `tasks/{status}/` (`pending`, `completed`, `recurring`), `pending/{prazo}/`, `independent-tasks/`, `project-tasks/` e pastas de projeto/fase em `tasks/` só existem se tiverem nota.
- Links: `[nome](caminho relativo)` — não `[[wiki]]`.
- Ambiguidade factual ou de decisão → perguntar; não inventar dados pessoais.
- Nota de tipo conhecido: copiar o template em `agents/templates/`; não inventar outro esqueleto.

## Glossário

### Projeto

Resultado maior, partido em fases, objetivo em uma frase. **Não se executa** — o que se faz são tarefas. Sem tarefas relacionadas, é só plano.

Não é 1:1 com tarefa nem com fase: uma fase pode caber numa única tarefa ou pedir dezenas. O projeto acaba quando o objetivo é verdadeiro.

Pasta: `projects/{slug}/` (`{slug}.md`, `analysis/`, `phases/{prefixo}-{nn}-{slug-fase}.md`). Hub `{slug}.md` a partir de [project-template](agents/templates/project-template.md). Criar: [new-project](agents/procedures/new-project.md). **Status** e **Prazo** só no markdown — a pasta não muda ([status-change](agents/procedures/status-change.md)). Todas as tarefas da fase `concluído` → fase `concluído`. Todas as fases do hub `concluído` → projeto `concluído`. Fase `não planejado` **bloqueia** o projeto.

### Fase

Recorte com **uma entrega**. Status e prazo próprios no markdown; nenhum dos dois move a pasta do projeto.

Planejada (`não iniciado` ou além): nota em `phases/{prefixo}-{nn}-{slug-fase}.md` ([phase-template](agents/templates/phase-template.md)), entrada no hub e **≥1 tarefa**. A nota traz **Entrega** (o quê) e **Como** (método, fontes, restrições) — escrita de forma que as tarefas derivadas já estejam definidas. Se o Como não der para derivar tarefas sem inventar, não criar as tarefas: analisar (se a complexidade justificar) ou perguntar. `não planejado`: só heading + status + prazo no hub — sem arquivo nem tarefas. Heading e arquivo usam o mesmo slug em inglês.

Relação com tarefas não é 1:1: a fase decide o que fica pronto e como; as tarefas só compactam isso em ações de algumas horas. Uma fase planejada pode ter uma ou dezenas de tarefas.

### Análise

Nota de **decisão**: responde qualquer pergunta. Fonte das seções: [analysis-template](agents/templates/analysis-template.md) (as mesmas para qualquer objeto; nem toda análise preenche todas). **Só quando a complexidade da fase justifica.** Uma ou mais, **normalmente antes** da fase a que servem: dados e pesquisa → o quê e o como que a fase descreve. Opcional. Pasta `analysis/` só nasce com arquivo. Slug **sem** id de fase (`fj-stack.md`, não `fj-01-stack.md`).

### Tarefa

Unidade de execução: **ação concreta, específica, no máximo algumas horas**. **Não traz nada de novo** — compacta e estrutura o que a fase (ou, se independente, a própria nota) já decidiu, visando fazer: o mínimo de pensar.

Pode ser **independente** (não depende de projeto) ou **relacionada a uma fase**. Fase planejada tem ≥1 tarefa; não é 1:1. Campo **Prazo:** data `YYYY-MM-DD` ou `não definido` (**Quando** no corpo não vira Prazo). Tarefa de fase: default = copiar o prazo da fase. Independente: `não definido` se o usuário não der data. Campo **Fase:** só se for de fase (link relativo). Pendente: `tasks/pending/{prazo}/independent-tasks/{slug}.md` ou `tasks/pending/{prazo}/project-tasks/{projeto}/{fase}/{slug}.md`. Concluída: `tasks/completed/…` (sem `{prazo}/`). Recorrente: `tasks/recurring/…` (sem `{prazo}/`). `{prazo}`: `late` · `today` · `three-days` · `one-week` · `one-month` · `long-time` · `undefined`. Template [task-template](agents/templates/task-template.md) — o mesmo para pontual e recorrente. Criar: [new-task](agents/procedures/new-task.md).

Tarefa de fase em três lugares: o arquivo, um link em `{fase}.md`, um checkbox em [tasks](tasks/tasks.md). Independente: sem **Fase:**. Checkbox só no índice. **O quê** = passos extraídos da Entrega + Como da fase. Se a fase não disser, não entra na tarefa.

### Prazo

Campo em projeto, fase e tarefa: `YYYY-MM-DD` ou `não definido`. Pai da fase = projeto. Pai da tarefa de fase = fase. Independente não herda. Criar filho: copiar o prazo do pai. Override: o usuário (ou pedido ao agente) põe outro valor no filho. Mudar o prazo do pai: cascatear só nos filhos cujo prazo é **igual ao valor antigo do pai** ou **`não definido`**; depois, nas tarefas elegíveis dessas fases. Filho com data diferente não mexe. **Prazo específico na fase:** as tarefas dessa fase **sem** prazo próprio (`não definido` ou ainda igual ao prazo antigo da fase) herdam a data; tarefa com data diferente não mexe. **Quando** não vira Prazo.

Em **tarefa** pendente, o prazo também escolhe a pasta **dentro de** `pending/`. Sem data → `undefined/`. Com data, dias até ela (hoje = 0; atrasada negativa): `< 0` `late/` · `0` `today/` · `1–3` `three-days/` · `4–7` `one-week/` · `8–30` `one-month/` · `> 30` `long-time/`. Recalcular vs hoje ao criar, ao mudar Prazo/Status, ou ao usar a lista. Concluir ou tornar recorrente: sair de `pending/{prazo}/`. Voltar a pendente: recalcular o balde. Projeto e fase **não** têm pasta de prazo.

### Tarefa recorrente

Todos, ou quase todos, os dias, até uma data, um acontecimento, ou indefinidamente. Status `recorrente`; pasta `tasks/recurring/` (sem `{prazo}/`). Deixar de ser recorrente = sai de `recurring/` e segue [status-change](agents/procedures/status-change.md).

### Daily

Notas diárias (em construção). Pasta `daily/`. Template: [day-template](agents/templates/day-template.md).

### Status

Projeto e fase: só o campo no markdown (e o heading no hub). Tarefa: campo **e** pasta. Mudar: [status-change](agents/procedures/status-change.md).

Projeto: `não iniciado` | `em andamento` | `concluído` | `pausado`. Fase: os mesmos **e** `não planejado`. Tarefa: `não iniciado` | `em andamento` | `concluído` | `recorrente`.

Tarefa: `pending/` (`não iniciado` | `em andamento`, com `{prazo}/`) · `completed/` (`concluído`) · `recurring/` (`recorrente`). Status e pasta coincidem **só** na tarefa.

Todas as tarefas de uma fase `concluído` → fase `concluído` (nota + hub). Todas as fases do hub `concluído` → projeto `concluído` (índice). Fase `não planejado` bloqueia o projeto. Não auto-`em andamento`.

`não planejado` = só **fase**: ainda não vale arquivo nem tarefas (heading no hub, sem nota em `phases/`). `pausado` = já vale, mas parou.

### Índice e hub

Índice: lista curta (link + blurb). Dois: [projects](projects/projects.md), [tasks](tasks/tasks.md) (pendentes e recorrentes; concluídas saem). Hub: nota-índice com o mesmo slug da pasta.
