# Nova tarefa

Não inventar datas nem pessoas. Sem `.gitkeep`. Nota a partir de [task-template](../templates/task-template.md). `pending/{prazo}/`, `independent-tasks/`, `project-tasks/`, `{projeto}/` e `{fase}/` só com nota. `completed/` e `recurring/` só com nota.

| Status | Pasta |
|---|---|
| `não iniciado` \| `em andamento` | `tasks/pending/{prazo}/` |
| `concluído` | `tasks/completed/` |
| `recorrente` | `tasks/recurring/` |

`{prazo}` só em `pending/`. Sem data → `undefined/`. Com data, dias até ela (hoje = 0; atrasada negativa): `< 0` `late/` · `0` `today/` · `1–3` `three-days/` · `4–7` `one-week/` · `8–30` `one-month/` · `> 30` `long-time/`.

**Domínio** no template: Dinheiro · Relacionamentos · Corpo. Um só, sem link.

## Antes de criar

1. Confirmar que não existe a mesma nota (buscar título, slug, pasta). Se existir, atualizar — não duplicar.
2. Se faltar **título**, **domínio**, **o quê** ou **status**, perguntar. Default de status: `não iniciado`. Tarefa de fase: **Prazo** = copiar o da fase (não perguntar). Independente: se o usuário não der data → `não definido`. Não inventar data. `não definido` → `pending/undefined/` se pendente. `recorrente` → `recurring/`. Tarefa de fase: se faltar a fase, ou se a fase não tiver Entrega + Como suficientes, perguntar — não inventar o como.
3. Arquivo: inglês, kebab-case, ASCII. Título e corpo em português.

## Criar

1. Independente pendente: `pending/{prazo}/independent-tasks/{slug}.md`. De fase pendente: `pending/{prazo}/project-tasks/{projeto}/{fase}/{slug}.md` (slugs do hub e da nota da fase). Recorrente ou concluída: o mesmo sem `{prazo}/`. Preencher **Domínio**, **Prazo** (cópia da fase se for de fase), **Status**, **O quê**, **Por quê**. **O quê** de tarefa de fase = passos compactos extraídos da Entrega + Como da fase (nada de novo). Independente: o como fica nesta nota. **Quando** e **Onde** só com dado real. **Quando** não vira Prazo. **Notas** só se houver detalhe necessário. Independente: omitir **Fase:**.
2. Se for de fase: **Fase:** com link relativo para a nota da fase; em `{fase}.md`, em `## Tarefas`, item `- [{Título}]({caminho relativo})` (criar o heading se ainda não existir). Não copiar o plano da fase. Fase `não planejado` não recebe tarefas.
3. Em [tasks](../../tasks/tasks.md): na seção do balde (ou **Recorrentes**), item `- [ ] [{Título}]({caminho a partir de tasks/})`. Trocar `--` se a seção estava vazia. `concluído` não entra no índice. Checkbox só aqui.
4. Links `[nome](caminho relativo)` — não `[[wiki]]`. Buscar no vault o caminho antigo só se estiver substituindo nota existente.

Mudança de status ou prazo **depois** de criado: [status-change](status-change.md).
