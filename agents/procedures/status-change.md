# Mudança de status

Sem `.gitkeep`. Pastas em `tasks/` só com nota — apagar `{prazo}/`, `pending/`, `completed/` ou `recurring/` se ficarem sem arquivo. `project-tasks/`, `independent-tasks/`, `{projeto}/` e `{fase}/` apagam-se se ficarem sem nota. Projeto e fase **não** têm pasta de status: só o campo (e o heading no hub).

| Tarefa (`Status`) | Pasta |
|---|---|
| `não iniciado` \| `em andamento` | `tasks/pending/{prazo}/` |
| `concluído` | `tasks/completed/` |
| `recorrente` | `tasks/recurring/` |

`{prazo}` só em `pending/`. Sem data → `undefined/`. Com data, dias até ela (hoje = 0; atrasada negativa): `< 0` `late/` · `0` `today/` · `1–3` `three-days/` · `4–7` `one-week/` · `8–30` `one-month/` · `> 30` `long-time/`. Recalcular vs hoje ao criar, ao mudar Prazo/Status, ou ao usar a lista.

## Projeto

1. Atualizar **Status** no `{slug}.md`. A pasta `projects/{domínio}/{slug}/` **não** se move.
2. Em [projects](../../projects/projects.md): tirar o item da seção antiga; pôr na nova (mesmo domínio). O caminho do link não muda (`{domínio}/{slug}/{slug}.md`).
3. Tarefas em `tasks/` **não** se movem (o `{projeto}` é o slug). Links *dentro* da pasta do projeto (analysis, phases) não mudam.

Não auto-`em andamento`. Auto-`concluído`: só quando **todas** as fases do hub estiverem `concluído`. Fase `não planejado` **bloqueia** — planejar ou tirar o heading; não concluir o projeto no lugar dela.

## Fase

1. Atualizar **Status** na nota em `phases/` **e** no heading correspondente do hub.
2. A pasta do projeto **não** se move. Tarefas da fase **não** mudam de pasta por status da fase.

Auto-`concluído`: quando **todas** as tarefas da fase tiverem **Status:** `concluído`. Fase `não planejado` não tem tarefas; não entra aqui.

## Tarefa

1. Atualizar **Status** na nota.
2. Mover o arquivo `.md` para o mesmo `project-tasks/{projeto}/{fase}/` ou `independent-tasks/` no status novo. Pendente inclui `{prazo}/`; concluída e recorrente **não**. Ex.: `pending/undefined/project-tasks/first-job/fj-01-study/study-java-basics.md` → `completed/project-tasks/first-job/fj-01-study/study-java-basics.md`. Independente: `pending/undefined/independent-tasks/{slug}.md` → `completed/independent-tasks/{slug}.md`. Voltar a pendente: recalcular `{prazo}` vs hoje.
3. Se `{fase}/`, `{projeto}/`, `project-tasks/`, `independent-tasks/` ou `{prazo}/` na pasta antiga ficar sem nota, apagar. Se `pending/` ficar sem balde, apagar `pending/` também.
4. Em [tasks](../../tasks/tasks.md): remover da seção antiga; se for pendente ou recorrente, listar na seção nova com caminho certo. Concluída: some do índice (não há seção de concluídos).
5. Se for de fase: atualizar o caminho em `## Tarefas` da nota da fase.
6. Buscar no vault o caminho antigo e atualizar links.
7. Se o novo status for `concluído` e a tarefa for de fase: se todas as tarefas da fase estiverem `concluído`, fase → `concluído` (nota + hub). Depois, se todas as fases do hub estiverem `concluído`, projeto → `concluído` e o item sobe para Concluído no índice.

Uma tarefa recorrente que deixa de ser recorrente sai de `recurring/` e segue a tabela acima (balde em `pending/` pela data vs hoje).

## Mudança de prazo

Não inferir de **Quando**.

### Tarefa

1. Atualizar **Prazo** (`YYYY-MM-DD` ou `não definido`). Isso é override: o filho deixa de seguir o pai.
2. Se o status for pendente, mover só dentro de `pending/` para o balde novo. Recorrente e concluída não mudam de pasta por prazo.
3. Apagar o `{prazo}/` antigo se ficar sem nota.
4. Em [tasks](../../tasks/tasks.md): seção e caminho. Se for de fase: `## Tarefas` da nota da fase.
5. Buscar no vault o caminho antigo e atualizar links.

### Projeto ou fase (cascata)

Pai da fase = projeto. Pai da tarefa de fase = fase. Prazo específico na fase: tarefas da fase sem prazo próprio herdam essa data.

1. Guardar o prazo antigo do pai. Atualizar **Prazo** no pai (hub e, se fase, a nota em `phases/`).
2. Cascatear só nos filhos cujo prazo é **igual ao valor antigo** ou **`não definido`**. Filho com data diferente não mexe. Recursivo: projeto → fases elegíveis (nota + heading no hub) → tarefas elegíveis dessas fases. Se o pai for uma **fase**, as tarefas sem prazo específico recebem o prazo novo da fase.
3. Cada tarefa pendente cujo prazo mudou: mover para o balde `pending/{prazo}/`; atualizar [tasks](../../tasks/tasks.md) e o link em `## Tarefas` da fase; buscar o caminho antigo no vault.
