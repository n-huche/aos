# Nova tarefa

Não inventar datas nem pessoas. Sem `.gitkeep`. Nota a partir de [task-template](../templates/task-template.md). `pending/{prazo}/`, `independent-tasks/`, `project-tasks/`, `{projeto}/` e `{fase}/` só com nota. `completed/` e `recurring/` só com nota.

| Status | Pasta |
|---|---|
| `pendente` | `tasks/pending/{prazo}/` |
| `concluído` | `tasks/completed/` |
| `recorrente` | `tasks/recurring/` |

`{prazo}` só em `pending/`. `não definido` → `undefined/`. Com data, dias até ela (hoje = 0; atrasada negativa): `< 0` `late/` · `0` `today/` · `1–3` `three-days/` · `4–7` `one-week/` · `8–30` `one-month/` · `> 30` `long-time/`. Recalcular vs hoje ao criar, ao mudar Prazo/Status, ou ao usar a lista.

`recorrente` com data: **Prazo:** `YYYY-MM-DD` = último dia. Hoje ≥ essa data → `concluído` (ao criar: gravar já em `completed/`, não passar por `recurring/`). Sem fim: **Prazo:** `none` — só independente. `none` não vale em tarefa `pendente` (`não definido`).

## Antes de criar

1. Confirmar que não existe a mesma nota (buscar título, slug, pasta). Se existir, atualizar — não duplicar.
2. Se faltar **título**, **o quê** ou **status**, perguntar. Default de status: `pendente`. Tarefa de fase: **Prazo** = copiar o da fase (não perguntar). Independente `pendente`: se o usuário não der data → `não definido`. Recorrente: se faltar prazo → `none` e **não** pôr numa fase; se o usuário der data, essa data é o fim (pode ser de fase). Não inventar data. Tarefa de fase: se faltar a fase, ou se a fase não tiver Entrega + Como suficientes, perguntar — não inventar o como.
3. Arquivo: inglês, kebab-case, ASCII. Título e corpo em português.

## Criar

1. Independente `pendente`: `pending/{prazo}/independent-tasks/{slug}.md`. De fase `pendente`: `pending/{prazo}/project-tasks/{projeto}/{fase}/{slug}.md` (slug do hub e da nota da fase). `recorrente` ou `concluído`: o mesmo sem `{prazo}/`. Preencher **Prazo**, **Status**, **O quê**, **Por quê**. **O quê** de tarefa de fase = passos compactos extraídos da Entrega + Como da fase (nada de novo). Independente: o como fica nesta nota. **Quando** e **Onde** só com dado real. **Quando** não vira Prazo. **Notas** só se houver detalhe necessário. Independente: omitir **Fase:**.
2. Se for de fase: **Fase:** com link relativo para a nota da fase (contar `../` até a raiz do vault, depois `projects/{status}/{slug}/phases/…`); em `{fase}.md`, em `## Tarefas`, item `- [{Título}]({caminho relativo})` (criar o heading se ainda não existir). Não copiar o plano da fase. Fase `não planejado` não recebe tarefas. Recorrente sem fim não entra em fase.
3. Em [tasks](../../tasks/tasks.md): na seção do balde (ou **Recorrentes**), item `- [ ] [{Título}]({caminho a partir de tasks/})`. Se o `##` não existir, inserir na ordem de [AGENTS](../../AGENTS.md) **Índice**. Sem `--`; heading só com item. `concluído` não entra no índice. Checkbox só aqui.
4. Links `[nome](caminho relativo)` — não `[[wiki]]`. Buscar no vault o caminho antigo só se estiver substituindo nota existente.

Não marcar `concluído` ao criar se ainda houver tarefa não-`concluído` em fase com `nn` menor no mesmo projeto — [status-change](status-change.md).

Mudança de status ou prazo **depois** de criado: [status-change](status-change.md).
