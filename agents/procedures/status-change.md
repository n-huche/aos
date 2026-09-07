# Mudança de status

Sem `.gitkeep`. Pastas em `tasks/` e `projects/{status}/` só com nota — apagar `{prazo}/`, `pending/`, `completed/`, `recurring/`, `in-progress/`, `paused/` se ficarem sem arquivo. `project-tasks/`, `independent-tasks/`, `{projeto}/` e `{fase}/` apagam-se se ficarem sem nota.

| Tarefa (`Status`) | Pasta |
|---|---|
| `pendente` | `tasks/pending/{prazo}/` |
| `concluído` | `tasks/completed/` |
| `recorrente` | `tasks/recurring/` |

| Projeto (`Status` herdado) | Pasta |
|---|---|
| `pendente` | `projects/pending/{slug}/` |
| `em andamento` | `projects/in-progress/{slug}/` |
| `pausado` | `projects/paused/{slug}/` |
| `concluído` | `projects/completed/{slug}/` |

`{prazo}` só em `tasks/pending/`. `não definido` → `undefined/`. Com data, dias até ela (hoje = 0; atrasada negativa): `< 0` `late/` · `0` `today/` · `1–3` `three-days/` · `4–7` `one-week/` · `8–30` `one-month/` · `> 30` `long-time/`. Recalcular vs hoje ao criar, ao mudar Prazo/Status, ou ao usar a lista.

`recorrente` com **Prazo:** `YYYY-MM-DD`: hoje ≥ essa data → `concluído`. Sem fim: **Prazo:** `none` — só independente.

Links relativos: contar `../` até a raiz do vault; depois `projects/{status}/{slug}/…` ou `tasks/…`.

## Projeto

O **Status** do projeto **herda** — não se escolhe à mão. Pasta 1:1. Ver [AGENTS](../../AGENTS.md) **Status**.

1. Recalcular no hub por `nn`: primeira fase não-`concluído` — `em andamento` / `pausado` / `pendente` → copiar; `não planejado` → projeto `pendente`. Se **todas** estão `concluído` (sem heading `não planejado`) → `concluído`.
2. Atualizar **Status** no `{slug}.md`.
3. Se a pasta mudou: mover `projects/{antigo}/{slug}/` → `projects/{novo}/{slug}/`. Apagar `{antigo}/` se ficar sem projeto. Em [projects](../../projects/projects.md): tirar da seção antiga (apagar o `##` se vazio); pôr na nova (**Pendente · Em andamento · Pausado · Concluído**) com caminho `{status}/{slug}/{slug}.md` — criar o heading se faltar. Sem `--`.
4. Tarefas em `tasks/` **não** se movem (o `{projeto}` é o slug). Links *dentro* do projeto não mudam. Buscar no vault `projects/{antigo}/{slug}` e atualizar (incl. **Fase:** nas tarefas).

## Fase

1. De `não planejado` para planejada: [new-phase](new-phase.md) (arquivo + tarefas) — não só mudar o campo.
2. Gate: `em andamento`, `pausado` e `concluído` só se todas as `nn` menores no hub estiverem `concluído`. `não planejado`, `pendente` e `pausado` anteriores bloqueiam. Recusar e dizer qual falta.
3. Com o gate ok, pela ordem de `## Tarefas`: primeira tarefa `concluído` e ainda há outras → `em andamento`; **todas** `concluído` (inclui recorrente com data) → `concluído` (uma única tarefa: `pendente` → `concluído`). `pausado` só se o usuário pedir (mesmo gate).
4. Atualizar **Status** na nota em `phases/` **e** no heading do hub.
5. Tarefas da fase **não** mudam de pasta por status da fase.
6. Recalcular o projeto (herança acima; mover a pasta se mudou).

Fase `não planejado` não tem tarefas; não entra no auto.

## Tarefa

1. Recusar `concluído` se a tarefa for de fase e **qualquer** tarefa de fase com `nn` menor no mesmo projeto ainda não estiver `concluído`.
2. Atualizar **Status** na nota (`pendente` | `concluído` | `recorrente`).
3. Mover o arquivo `.md` para o mesmo `project-tasks/{projeto}/{fase}/` ou `independent-tasks/` no status novo. `pendente` inclui `{prazo}/`; `concluído` e `recorrente` **não**. Ex.: `pending/undefined/project-tasks/first-job/fj-01-study/study-java-basics.md` → `completed/project-tasks/first-job/fj-01-study/study-java-basics.md`. Voltar a `pendente`: recalcular `{prazo}` vs hoje.
4. Se `{fase}/`, `{projeto}/`, `project-tasks/`, `independent-tasks/` ou `{prazo}/` na pasta antiga ficar sem nota, apagar. Se `pending/` ficar sem balde, apagar `pending/` também.
5. Em [tasks](../../tasks/tasks.md): remover da seção antiga (apagar o `##` se vazio); se for `pendente` ou `recorrente`, listar na seção nova — criar o heading na ordem de [AGENTS](../../AGENTS.md) **Índice** se faltar. Sem `--`. `concluído`: some do índice.
6. Se for de fase: atualizar o caminho em `## Tarefas` da nota da fase; reescrever **Fase:** (contar `../` até a raiz).
7. Buscar no vault o caminho antigo e atualizar links.
8. Recalcular o status da fase (passo **Fase** acima) e o projeto.

Uma tarefa `recorrente` que deixa de ser recorrente sai de `recurring/` e segue a tabela (balde em `pending/` pela data vs hoje). Recorrente com data: se hoje ≥ Prazo → `concluído`.

## Mudança de prazo

Não inferir de **Quando**.

### Tarefa

1. Atualizar **Prazo** (`YYYY-MM-DD`, `não definido`, ou `none` se `recorrente` sem fim). Data em `pendente` é override. `recorrente` com data = último dia; hoje ≥ data → `concluído`.
2. Se o status for `pendente`, mover só dentro de `pending/` para o balde novo. `recorrente` e `concluído` não mudam de pasta por prazo, salvo o fim da recorrência.
3. Apagar o `{prazo}/` antigo se ficar sem nota.
4. Em [tasks](../../tasks/tasks.md): seção e caminho (criar `##` se faltar; apagar se ficar vazio). Se for de fase: `## Tarefas` da nota da fase.
5. Buscar no vault o caminho antigo e atualizar links.

### Projeto ou fase (cascata)

Pai da fase = projeto. Pai da tarefa de fase = fase. Prazo específico na fase: tarefas da fase sem prazo próprio herdam essa data.

1. Guardar o prazo antigo do pai. Atualizar **Prazo** no pai (hub e, se fase, a nota em `phases/`).
2. Cascatear só nos filhos cujo prazo é **igual ao valor antigo** ou **`não definido`**. `none` não cascateia. Filho com data diferente não mexe. Recursivo: projeto → fases elegíveis (nota + heading no hub) → tarefas elegíveis dessas fases.
3. Cada tarefa `pendente` cujo prazo mudou: mover para o balde `pending/{prazo}/`; atualizar [tasks](../../tasks/tasks.md) (heading só com item) e o link em `## Tarefas` da fase; buscar o caminho antigo no vault. **Fase:** não muda de profundidade (ainda há `{prazo}/`).

## Ao usar a lista

Em [tasks](../../tasks/tasks.md), para cada `pendente`: abrir a nota, ler **Prazo:** (não só a pasta) e recalcular o balde vs hoje. Se pasta ou seção estiver errada, seguir **Mudança de prazo → Tarefa**. Recorrente com data: hoje ≥ Prazo → `concluído` (seguir **Tarefa**).
