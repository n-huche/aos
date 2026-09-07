# AGENTS

Vault Obsidian + git (`n-huche/docs`). Fonte de anotações e planos.

Qualquer agente segue este arquivo, `agents/procedures/` e `agents/templates/`. Sem pasta de memória por ferramenta.

## Convenções

- Idioma dos **textos** do usuário: **português**.
- Nomes de **pastas e arquivos**: **inglês**, kebab-case, ASCII, sem espaços.
- Completo, mas enxuto; uma fonte da verdade por tema (não duplicar tabelas/rosters).
- Nunca usar `.gitkeep` nem placeholder para pasta vazia. Pasta só entra no git quando tiver nota.
- Links: `[nome](caminho relativo)` — não `[[wiki]]`.
- Ambiguidade factual ou de decisão → perguntar; não inventar dados pessoais.
- Nota de tipo conhecido: copiar o template em `agents/templates/`; não inventar outro esqueleto.

## Glossário

### Domínio

Eixo por **finalidade**, não por tema. Três: Dinheiro (`money`), Relacionamentos (`relationships`), Corpo (`body`).

O lugar de um projeto ou tarefa é **a que fim a ação serve**. A mesma competência pode aparecer em mais de um eixo; a fonte fica no da finalidade principal, o outro só aponta.

Objetivo de um domínio = concluir os seus projetos. Sem `{domínio}.md`; projetos em `projects/{status}/{domínio}/{slug}/`. Índice só em [projects](projects/projects.md).

#### Dinheiro

Ganho financeiro, patrimônio ou ativos — o que entra no bolso, gera renda ou reduz custo de forma duradoura.

Cabe: emprego e carreira, skills com valor de mercado, produtos, investimentos, modelos mentais **quando o uso declarado for dinheiro**. Não cabe: o vínculo em si; treino ou aparência pelo fim estético ou de saúde.

#### Relacionamentos

O vínculo entre pessoas — como começa, se mantém, se repara ou se encerra.

Cabe: namoro e amizade, família, comportamento em relação (presentes, cuidados pontuais, conversas difíceis). Não cabe: charme ou rede só para fechar vaga ou venda; disciplina de treino ou higiene pelo próprio corpo.

#### Corpo

O organismo e como ele aparece — saúde, força, higiene, estilo, expressão física.

Cabe: treino, alimentação, sono, aparência, roupa e postura **quando o fim é o corpo**. Não cabe: academia como networking para emprego; gesto cujo fim é o vínculo.

### Projeto

Resultado maior, partido em fases, objetivo em uma frase. **Não se executa** — o que se faz são tarefas. Sem tarefas relacionadas, é só plano.

Não é 1:1 com tarefa nem com fase: uma fase pode caber numa única tarefa ou pedir dezenas. O projeto acaba quando o objetivo é verdadeiro.

Pasta: `projects/{status}/{domínio}/{slug}/` (`{slug}.md`, `analysis/`, `phases/{prefixo}-{nn}-{slug-fase}.md`). Hub `{slug}.md` a partir de [project-template](agents/templates/project-template.md). Criar: [new-project](agents/procedures/new-project.md). **Status geral** e pasta coincidem ([status-change](agents/procedures/status-change.md)).

### Fase

Recorte com **uma entrega**. Status próprio; mudar o status da fase **não** move a pasta do projeto.

Planejada (`não iniciado` ou além): nota em `phases/{prefixo}-{nn}-{slug-fase}.md` ([phases-template](agents/templates/phases-template.md)) e entrada no hub. `não planejado`: só heading + status no hub — sem arquivo nem tarefas. Heading e arquivo usam o mesmo slug em inglês.

Relação com tarefas não é 1:1: a fase diz o que tem de ficar pronto; as tarefas dizem o que fazer nas próximas horas.

### Análise

Nota de **decisão**: responde qualquer pergunta. Template [analysis-template](agents/templates/analysis-template.md) (pergunta, opções, achados, decisão — as mesmas seções para qualquer objeto). Opcional. Pasta `analysis/` só nasce com arquivo. Slug **sem** id de fase (`fj-stack.md`, não `fj-01-stack.md`).

### Tarefa

Unidade de execução: **ação concreta, específica, no máximo algumas horas**.

Pode ser **independente** (não depende de projeto) ou **relacionada a uma fase** — não 1:1. Campo **Domínio** = finalidade da ação (não há `tasks/money/`). Itens em `tasks/pending/`, `tasks/completed/` ou `tasks/recurring/`. Template [tasks-template](agents/templates/tasks-template.md) — o mesmo para pontual e recorrente. Criar: [new-task](agents/procedures/new-task.md).

### Tarefa recorrente

Todos, ou quase todos, os dias, até uma data, um acontecimento, ou indefinidamente. Status `recorrente`; pasta `tasks/recurring/`. Deixar de ser recorrente = sai de `recurring/` e segue [status-change](agents/procedures/status-change.md).

### Daily

Notas diárias (em construção). Pasta `daily/`. Template: [day-template](agents/templates/day-template.md).

### Status

Campo no markdown **e** pasta. Mudar projeto ou tarefa: [status-change](agents/procedures/status-change.md).

Projeto: `não iniciado` | `em andamento` | `concluído` | `pausado`. Fase: os mesmos **e** `não planejado`. Tarefa: `não iniciado` | `em andamento` | `concluído` | `recorrente`.

Projeto `projects/{status}/{domínio}/{slug}/`: `pending/` (`não iniciado`, `pausado`) · `in-progress/` (`em andamento`) · `completed/` (`concluído`). Tarefa: `tasks/pending/` (`não iniciado` | `em andamento`) · `tasks/completed/` (`concluído`) · `tasks/recurring/` (`recorrente`).

`não planejado` = só **fase**: ainda não vale arquivo nem tarefas (heading no hub, sem nota em `phases/`). `pausado` = já vale, mas parou.

### Índice e hub

Índice: lista curta (link + blurb). Dois: [projects](projects/projects.md), [tasks](tasks/tasks.md) (pendentes e recorrentes; concluídas saem). Hub: nota-índice com o mesmo slug da pasta.
