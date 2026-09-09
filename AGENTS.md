# AGENTS

## Convenções

- Idioma dos **textos** do usuário: **português**.
- Nomes de **pastas e arquivos**: **inglês**, kebab-case, ASCII, sem espaços.
- Links: `[nome](caminho relativo)` — não `[[wiki]]`.
- Ambiguidade factual ou de decisão → perguntar; não inventar dados pessoais.
- Relógio dos procedimentos: `{hoje}` (e hora na atualização diária). Não inventar datas.
- Pastas operacionais: `tasks/`, `projects/`, `daily/`. Pasta só com nota.

## Glossário

### Tarefa

Pode ser independente ou de projeto, única ou recorrente. É a única forma de execução de todo o sistema. Deve descrever uma ação concreta, específica e realizável em no máximo poucas horas. Sua proposta é tornar a execução limpa e mecânica.

| Tarefa       | Única                                                             | Recorrente                                                                                                  |
| ------------ | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Independente | Ação única que realiza um objetivo simples                        | Ação que deve ser executada recorrentemente para realizar um objetivo simples                               |
| De projeto   | Ação única que contribui com a realização de um objetivo complexo | Ação que para contribuir com um objetivo complexo deve ser realizada recorrentemente até uma data ou evento |

### Projeto

Resultado maior, partido em fases, define o objetivo. Tem prazo, status e pode ter análises. Não se executa — o que se faz são tarefas.

### Fase

Recorte do projeto com uma entrega necessária para a fase seguinte. Define o "o quê" e o "como" de uma etapa do projeto. Tem status e prazo próprios. As tarefas de projeto são unidades de ação definidas nas fases.

### Análise

Pesquisa feita quando o objetivo de um projeto ou de uma fase não tem um caminho claro para ação. Ajudam a descobrir o "o quê" e o "como".

### Diário

Registro que responde se e quando tarefas foram executadas, ajuda na autoanálise a favor da consistência.

## Procedimentos

|Objetivo|Execute...|
|---|---|
|Criar nova tarefa|[new-task.md](agents/procedures/new-task.md)|
|Criar novo projeto|[new-project.md](agents/procedures/new-project.md)|
|Adicionar nova fase|[new-phase.md](agents/procedures/new-phase.md)|
|Fazer nova análise|[new-analysis.md](agents/procedures/new-analysis.md)|
|Atualização diária|[daily-update.md](agents/procedures/daily-update.md)|