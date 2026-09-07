# Mudança de status

Sem `.gitkeep`. Pastas em `tasks/` só com nota — apagar `{prazo}/`, `pending/`, `completed/` ou `recurring/` se ficarem sem arquivo. `project-tasks/`, `independent-tasks/`, `{projeto}/` e `{fase}/` apagam-se se ficarem sem nota. Projeto e fase **não** têm pasta de status: só o campo (e o heading no hub).

| Tarefa (`Status`) | Pasta |
|---|---|
| `pending` | `tasks/pending/{prazo}/` |
| `completed` | `tasks/completed/` |
| `recurring` | `tasks/recurring/` |

`{prazo}` só em `pending/`. `não definido` → `undefined/`. Com data, dias até ela (hoje = 0; atrasada negativa): `< 0` `late/` · `0` `today/` · `1–3` `three-days/` · `4–7` `one-week/` · `8–30` `one-month/` · `> 30` `long-time/`. Recalcular vs hoje ao criar, ao mudar Prazo/Status, ou ao usar a lista.

`recurring` com **Prazo:** `YYYY-MM-DD`: hoje ≥ essa data → `completed`. Sem fim: **Prazo:** `none`. `none` só em recorrente sem fim.

## Projeto

O **Status** do projeto **herda** a fase atual — não se escolhe à mão.

1. Recalcular: se alguma fase planejada está `em andamento` → esse status (menor `nn` se houver mais de uma); senão, se alguma está `concluído` → `concluído`; senão → `pendente`. `não planejado` não conta. Pausar a fase em andamento: some o `em andamento`, então o projeto cai na regra 2 ou 3 (não fica `pausado` sozinho).
2. Atualizar **Status** no `{slug}.md`. A pasta `projects/{slug}/` **não** se move.
3. Em [projects](../../projects/projects.md): tirar o item da seção antiga; pôr na nova (**Pendente / pausado**, **Em andamento**, **Concluído**). O caminho do link não muda (`{slug}/{slug}.md`).
4. Tarefas em `tasks/` **não** se movem (o `{projeto}` é o slug). Links *dentro* da pasta do projeto (analysis, phases) não mudam.

Não auto-`em andamento`. Não “todas as fases concluídas / não planejado bloqueia”.

## Fase

1. Se o alvo for `em andamento`: no hub, todas as fases com `nn` menor têm de estar `concluído`. `não planejado`, `pendente` e `pausado` anteriores bloqueiam. Se faltar alguma, recusar e dizer qual — não aplicar.
2. Atualizar **Status** na nota em `phases/` **e** no heading correspondente do hub.
3. A pasta do projeto **não** se move. Tarefas da fase **não** mudam de pasta por status da fase.
4. Recalcular o **Status** do projeto (herança acima).

Auto-`concluído`: quando **todas** as tarefas da fase que **não** são `recurring` tiverem **Status:** `completed`. Recorrente sem fim não entra em fase. Fase `não planejado` não tem tarefas; não entra aqui.

## Tarefa

1. Atualizar **Status** na nota (`pending` | `completed` | `recurring`).
2. Mover o arquivo `.md` para o mesmo `project-tasks/{projeto}/{fase}/` ou `independent-tasks/` no status novo. `pending` inclui `{prazo}/`; `completed` e `recurring` **não**. Ex.: `pending/undefined/project-tasks/first-job/fj-01-study/study-java-basics.md` → `completed/project-tasks/first-job/fj-01-study/study-java-basics.md`. Independente: `pending/undefined/independent-tasks/{slug}.md` → `completed/independent-tasks/{slug}.md`. Voltar a `pending`: recalcular `{prazo}` vs hoje.
3. Se `{fase}/`, `{projeto}/`, `project-tasks/`, `independent-tasks/` ou `{prazo}/` na pasta antiga ficar sem nota, apagar. Se `pending/` ficar sem balde, apagar `pending/` também.
4. Em [tasks](../../tasks/tasks.md): remover da seção antiga; se for `pending` ou `recurring`, listar na seção nova com caminho certo. `completed`: some do índice (não há seção de concluídos).
5. Se for de fase: atualizar o caminho em `## Tarefas` da nota da fase.
6. Buscar no vault o caminho antigo e atualizar links.
7. Se o novo status for `completed` e a tarefa for de fase: se todas as tarefas **não** `recurring` da fase estiverem `completed`, fase → `concluído` (nota + hub). Depois recalcular o projeto e o índice.

Uma tarefa `recurring` que deixa de ser recorrente sai de `recurring/` e segue a tabela acima (balde em `pending/` pela data vs hoje). Recorrente com data: se hoje ≥ Prazo → `completed`.

## Mudança de prazo

Não inferir de **Quando**.

### Tarefa

1. Atualizar **Prazo** (`YYYY-MM-DD`, `não definido`, ou `none` se `recurring` sem fim). Data em `pending` é override: o filho deixa de seguir o pai. `recurring` com data = último dia; hoje ≥ data → `completed`.
2. Se o status for `pending`, mover só dentro de `pending/` para o balde novo. `recurring` e `completed` não mudam de pasta por prazo, salvo o fim da recorrência.
3. Apagar o `{prazo}/` antigo se ficar sem nota.
4. Em [tasks](../../tasks/tasks.md): seção e caminho. Se for de fase: `## Tarefas` da nota da fase.
5. Buscar no vault o caminho antigo e atualizar links.

### Projeto ou fase (cascata)

Pai da fase = projeto. Pai da tarefa de fase = fase. Prazo específico na fase: tarefas da fase sem prazo próprio herdam essa data.

1. Guardar o prazo antigo do pai. Atualizar **Prazo** no pai (hub e, se fase, a nota em `phases/`).
2. Cascatear só nos filhos cujo prazo é **igual ao valor antigo** ou **`não definido`**. `none` não cascateia. Filho com data diferente não mexe. Recursivo: projeto → fases elegíveis (nota + heading no hub) → tarefas elegíveis dessas fases. Se o pai for uma **fase**, as tarefas sem prazo específico recebem o prazo novo da fase.
3. Cada tarefa `pending` cujo prazo mudou: mover para o balde `pending/{prazo}/`; atualizar [tasks](../../tasks/tasks.md) e o link em `## Tarefas` da fase; buscar o caminho antigo no vault.
