# Nova tarefa

Não inventar domínio, datas nem pessoas. Sem `.gitkeep`. Nota a partir de [task-template](../templates/task-template.md). `projects/`, `independent/`, `{projeto}/` e `{fase}/` só com nota. `tasks/{status}/` existe **localmente** mesmo vazio (criar se faltar).

| Campo | Pasta |
|---|---|
| `não iniciado` \| `em andamento` | `tasks/pending/` |
| `concluído` | `tasks/completed/` |
| `recorrente` | `tasks/recurring/` |

**Domínio** no template: Dinheiro · Relacionamentos · Corpo. Um só, sem link.

## Antes de criar

1. Confirmar que não existe a mesma nota (buscar título, slug, pasta). Se existir, atualizar — não duplicar.
2. Se faltar **título**, **domínio**, **o quê** ou **status**, perguntar. Default: `não iniciado` → `pending/`. `recorrente` → `recurring/`. Tarefa de fase: se faltar a fase, ou se a fase não tiver Entrega + Como suficientes, perguntar — não inventar o como.
3. Arquivo: inglês, kebab-case, ASCII. Título e corpo em português.

## Criar

1. Independente: `{status}/independent/{slug}.md`. De fase: `{status}/projects/{projeto}/{fase}/{slug}.md` (slugs do hub e da nota da fase). Preencher **Domínio**, **Status**, **O quê**, **Por quê**. **O quê** de tarefa de fase = passos compactos extraídos da Entrega + Como da fase (nada de novo). Independente: o como fica nesta nota. **Quando** e **Onde** só com dado real. **Notas** só se houver detalhe necessário. Independente: omitir **Fase:**.
2. Se for de fase: **Fase:** com link relativo para a nota da fase; em `{fase}.md`, em `## Tarefas`, item `- [{Título}]({caminho relativo})` (criar o heading se ainda não existir). Não copiar o plano da fase. Fase `não planejado` não recebe tarefas.
3. Em [tasks](../../tasks/tasks.md): na seção **Pendentes** ou **Recorrentes**, item `- [ ] [{Título}]({caminho a partir de tasks/})`. Trocar `--` se a seção estava vazia. `concluído` não entra no índice. Checkbox só aqui.
4. Links `[nome](caminho relativo)` — não `[[wiki]]`. Buscar no vault o caminho antigo só se estiver substituindo nota existente.

Mudança de status **depois** de criado: [status-change](status-change.md).
