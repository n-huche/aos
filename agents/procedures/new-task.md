# Nova tarefa

Não inventar domínio, datas nem pessoas. Sem `.gitkeep`. Não editar `agents/grok-bot/` (memória do Grok Bot). `agents/procedures/` e `agents/templates/` são compartilhados. Nota a partir de [tasks-template](../templates/tasks-template.md). Pasta só com nota dentro.

| Campo | Pasta |
|---|---|
| `não iniciado` \| `em andamento` | `tasks/pending/` |
| `concluído` | `tasks/completed/` |
| `recorrente` | `tasks/recurring/` |

**Domínio** no template: Dinheiro · Relacionamentos · Corpo — [glossário](../../AGENTS.md). Um só.

## Antes de criar

1. Confirmar que não existe a mesma nota (buscar título, slug, pasta). Se existir, atualizar — não duplicar.
2. Se faltar **título**, **domínio**, **o quê** ou **status**, perguntar. Default: `não iniciado` → `pending/`. `recorrente` → `recurring/`.
3. Arquivo: inglês, kebab-case, ASCII (`replace-iphone-12-battery.md`). Título e corpo em português.

## Criar

1. `{pasta}/{slug}.md` pelo template. Preencher **Domínio** (um link), **Status**, **O quê**, **Por quê**. **Quando** e **Onde** só com dado real. **Notas** só se houver detalhe necessário.
2. Se o usuário nomeou projeto e/ou fase, acrescentar na nota um bloco com links relativos — não copiar o plano do projeto. Se não nomeou, não inventar o bloco.
3. Em [tasks](../../tasks/tasks.md): na seção **Pendentes** ou **Recorrentes**, item `- [ ] [{Título}]({pasta}/{slug}.md)`. Trocar `--` se a seção estava vazia. `concluído` não entra no índice.
4. Links `[nome](caminho relativo)` — não `[[wiki]]`. Buscar no vault (exceto `agents/grok-bot/`) o caminho antigo só se estiver substituindo nota existente.

Mudança de status **depois** de criado: [status-change](status-change.md).
