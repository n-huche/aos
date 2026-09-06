# Mudança de status

Pasta e campo no markdown têm de coincidir. Sem `.gitkeep`. Não editar `agents/grok-bot/` — o gabinete atualiza os próprios links.

| Projeto (`Status geral`) | Pasta |
|---|---|
| `não iniciado` \| `não planejado` \| `pausado` | `projects/{domínio}/pending/` |
| `em andamento` | `projects/{domínio}/in-progress/` |
| `concluído` | `projects/{domínio}/completed/` |

| Tarefa (`Status`) | Pasta |
|---|---|
| `não iniciado` \| `em andamento` | `tasks/pending/` |
| `concluído` | `tasks/completed/` |
| `recorrente` | `tasks/recurring/` |

## Projeto

1. Atualizar **Status geral** no `{slug}.md`.
2. Mover a pasta inteira: `projects/{domínio}/{status-antigo}/{slug}/` → `projects/{domínio}/{status-novo}/{slug}/`.
3. Em [projects](../projects/projects.md): tirar o item da seção antiga; pôr na nova (mesmo domínio); corrigir o caminho do link.
4. No hub do domínio (`projects/{domínio}/{domínio}.md`): o mesmo — seção + caminho relativo (`pending/{slug}/…` → `in-progress/{slug}/…`, etc.).
5. Buscar no vault (exceto `agents/grok-bot/`) o caminho antigo e atualizar links externos. Links *dentro* da pasta do projeto (analysis, phases) não mudam.

Fase (`Status` em `phases/` ou no hub do projeto): só o campo. A pasta do projeto **não** se move.

## Tarefa

1. Atualizar **Status** na nota.
2. Mover o arquivo `.md` para a pasta nova.
3. Em [tasks](../tasks/tasks.md): remover da seção antiga; se for pendente ou recorrente, listar na seção nova com caminho certo. Concluída: some do índice (não há seção de concluídos).
4. Buscar no vault (exceto `agents/grok-bot/`) o caminho antigo e atualizar links.

Uma tarefa recorrente que deixa de ser recorrente sai de `recurring/` e segue a tabela acima.
