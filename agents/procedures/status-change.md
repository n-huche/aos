# Mudança de status

Sem `.gitkeep`. Pastas em `tasks/` e `projects/{status}/` só com nota — apagar `{prazo}/`, `pending/`, `completed/`, `recurring/`, `in-progress/`, `paused/` se ficarem sem arquivo. `project-tasks/`, `independent-tasks/`, `{projeto}/` e `{fase}/` apagam-se se ficarem sem nota.

| Tarefa (`Status`) | Pasta |
|---|---|
| `pending` | `tasks/pending/{prazo}/` |
| `completed` | `tasks/completed/` |
| `recurring` | `tasks/recurring/` |

| Projeto (`Status` herdado) | Pasta |
|---|---|
| `pendente` | `projects/pending/{slug}/` |
| `em andamento` | `projects/in-progress/{slug}/` |
| `pausado` | `projects/paused/{slug}/` |
| `concluído` | `projects/completed/{slug}/` |

`{prazo}` só em `tasks/pending/`. `não definido` → `undefined/`. Com data, dias até ela (hoje = 0; atrasada negativa): `< 0` `late/` · `0` `today/` · `1–3` `three-days/` · `4–7` `one-week/` · `8–30` `one-month/` · `> 30` `long-time/`. Recalcular vs hoje ao criar, ao mudar Prazo/Status, ou ao usar a lista.

`recurring` com **Prazo:** `YYYY-MM-DD`: hoje ≥ essa data → `completed`. Sem fim: **Prazo:** `none`. `none` só em recorrente sem fim.

## Projeto

O **Status** do projeto **herda** a fase atual — não se escolhe à mão. Pasta 1:1 com a herança.

1. Recalcular: se alguma fase planejada está `em andamento` → `em andamento` (menor `nn` se houver mais de uma); senão, se alguma está `pausado` → `pausado`; senão, se alguma está `concluído` → `concluído`; senão → `pendente`. `não planejado` não conta. Pausar a fase em andamento: some o `em andamento` → projeto `pausado` → `projects/paused/{slug}/`.
2. Atualizar **Status** no `{slug}.md`.
3. Se a pasta mudou: mover `projects/{antigo}/{slug}/` → `projects/{novo}/{slug}/`. Apagar `{antigo}/` se ficar sem projeto. Índice: tirar da seção antiga; pôr na nova (**Pendente**, **Em andamento**, **Pausado**, **Concluído**) com caminho `{status}/{slug}/{slug}.md`.
4. Tarefas em `tasks/` **não** se movem (o `{projeto}` é o slug). Links *dentro* da pasta do projeto (analysis, phases) não mudam. Buscar no vault `projects/{antigo}/{slug}` e atualizar (incl. **Fase:** nas tarefas: `projects/{status}/{slug}/phases/…`). Profundidade de `../` até a raiz **não** muda.

Não auto-`em andamento`. Não “todas as fases concluídas / não planejado bloqueia”.

## Fase

1. De `não planejado` para planejada: [new-phase](new-phase.md) (arquivo + tarefas) — não só mudar o campo.
2. Se o alvo for `em andamento`: no hub, todas as fases com `nn` menor têm de estar `concluído`. `não planejado`, `pendente` e `pausado` anteriores bloqueiam. Se faltar alguma, recusar e dizer qual — não aplicar.
3. Atualizar **Status** na nota em `phases/` **e** no heading correspondente do hub.
4. Tarefas da fase **não** mudam de pasta por status da fase.
5. Recalcular o **Status** do projeto (herança acima; mover a pasta do projeto se mudou).

Auto-`concluído`: quando **todas** as tarefas da fase que **não** são `recurring` tiverem **Status:** `completed`. Recorrente sem fim não entra em fase. Fase `não planejado` não tem tarefas; não entra aqui.

## Tarefa

1. Atualizar **Status** na nota (`pending` | `completed` | `recurring`).
2. Mover o arquivo `.md` para o mesmo `project-tasks/{projeto}/{fase}/` ou `independent-tasks/` no status novo. `pending` inclui `{prazo}/`; `completed` e `recurring` **não**. Ex.: `pending/undefined/project-tasks/first-job/fj-01-study/study-java-basics.md` → `completed/project-tasks/first-job/fj-01-study/study-java-basics.md`. Independente: `pending/undefined/independent-tasks/{slug}.md` → `completed/independent-tasks/{slug}.md`. Voltar a `pending`: recalcular `{prazo}` vs hoje.
3. Se `{fase}/`, `{projeto}/`, `project-tasks/`, `independent-tasks/` ou `{prazo}/` na pasta antiga ficar sem nota, apagar. Se `pending/` ficar sem balde, apagar `pending/` também.
4. Em [tasks](../../tasks/tasks.md): remover da seção antiga (se ficar sem item, apagar o `##`); se for `pending` ou `recurring`, listar na seção nova — criar o heading na ordem do obs de [task-template](../templates/task-template.md) se faltar. Sem `--`. `completed`: some do índice (não há seção de concluídos).
5. Se for de fase: atualizar o caminho em `## Tarefas` da nota da fase (`pending/{prazo}/` vs `completed/` ou `recurring/` sem `{prazo}/`; da fase são 4 `../` até a raiz: `../../../../tasks/…`). Reescrever **Fase:** na nota da tarefa: em `pending/{prazo}/` são 6 `../` até a raiz; em `completed/` e `recurring/`, 5 `../` — o `{status}` do projeto fica *depois* de `projects/` (ver [task-template](../templates/task-template.md)).
6. Buscar no vault o caminho antigo e atualizar links.
7. Se o novo status for `completed` e a tarefa for de fase: se todas as tarefas **não** `recurring` da fase estiverem `completed`, fase → `concluído` (nota + hub). Depois recalcular o projeto (mover pasta se a herança mudou) e o índice.

Uma tarefa `recurring` que deixa de ser recorrente sai de `recurring/` e segue a tabela acima (balde em `pending/` pela data vs hoje). Recorrente com data: se hoje ≥ Prazo → `completed`.

## Mudança de prazo

Não inferir de **Quando**.

### Tarefa

1. Atualizar **Prazo** (`YYYY-MM-DD`, `não definido`, ou `none` se `recurring` sem fim). Data em `pending` é override: o filho deixa de seguir o pai. `recurring` com data = último dia; hoje ≥ data → `completed`.
2. Se o status for `pending`, mover só dentro de `pending/` para o balde novo. `recurring` e `completed` não mudam de pasta por prazo, salvo o fim da recorrência.
3. Apagar o `{prazo}/` antigo se ficar sem nota.
4. Em [tasks](../../tasks/tasks.md): seção e caminho (criar `##` se faltar; apagar se ficar vazio). Se for de fase: `## Tarefas` da nota da fase.
5. Buscar no vault o caminho antigo e atualizar links.

### Projeto ou fase (cascata)

Pai da fase = projeto. Pai da tarefa de fase = fase. Prazo específico na fase: tarefas da fase sem prazo próprio herdam essa data.

1. Guardar o prazo antigo do pai. Atualizar **Prazo** no pai (hub e, se fase, a nota em `phases/`).
2. Cascatear só nos filhos cujo prazo é **igual ao valor antigo** ou **`não definido`**. `none` não cascateia. Filho com data diferente não mexe. Recursivo: projeto → fases elegíveis (nota + heading no hub) → tarefas elegíveis dessas fases. Se o pai for uma **fase**, as tarefas sem prazo específico recebem o prazo novo da fase.
3. Cada tarefa `pending` cujo prazo mudou: mover para o balde `pending/{prazo}/`; atualizar [tasks](../../tasks/tasks.md) (heading só com item) e o link em `## Tarefas` da fase; buscar o caminho antigo no vault. **Fase:** na nota da tarefa não muda de profundidade (ainda há `{prazo}/`).

## Ao usar a lista

Em [tasks](../../tasks/tasks.md), para cada `pending`: abrir a nota, ler **Prazo:** (não só a pasta) e recalcular o balde vs hoje. Se pasta ou seção estiver errada, seguir **Mudança de prazo → Tarefa** (criar/apagar `##` conforme o último item). Recorrente com data: hoje ≥ Prazo → `completed` (seguir **Tarefa**).
