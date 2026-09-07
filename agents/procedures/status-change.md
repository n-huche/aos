# Mudança de status

Pasta e campo no markdown têm de coincidir. Sem `.gitkeep`. `tasks/{status}/` permanece **localmente** mesmo vazio (criar se faltar). `projects/`, `independent/`, `{projeto}/` e `{fase}/` apagam-se se ficarem sem nota.

| Projeto (`Status geral`) | Pasta |
|---|---|
| `não iniciado` \| `pausado` | `projects/pending/{domínio}/` |
| `em andamento` | `projects/in-progress/{domínio}/` |
| `concluído` | `projects/completed/{domínio}/` |

| Tarefa (`Status`) | Pasta |
|---|---|
| `não iniciado` \| `em andamento` | `tasks/pending/` |
| `concluído` | `tasks/completed/` |
| `recorrente` | `tasks/recurring/` |

## Projeto

1. Atualizar **Status geral** no `{slug}.md`.
2. Mover a pasta inteira: `projects/{status-antigo}/{domínio}/{slug}/` → `projects/{status-novo}/{domínio}/{slug}/`. Ex.: `pending/money/first-job/` → `in-progress/money/first-job/`. Não deixar `projects/{status}/{domínio}/` vazio — se o domínio ficar sem projetos naquele status, apagar a pasta do domínio.
3. Em [projects](../../projects/projects.md): tirar o item da seção antiga; pôr na nova (mesmo domínio); corrigir o caminho do link (`pending/money/first-job/…` → `in-progress/money/first-job/…`, etc.).
4. Buscar no vault o caminho antigo e atualizar links externos. Atualizar **Fase:** nas tarefas ligadas (o caminho do projeto muda). Links *dentro* da pasta do projeto (analysis, phases) não mudam. Tarefas em `tasks/` **não** se movem quando o projeto muda de status (o `{projeto}` em `tasks/` é o slug, não o status do projeto).

Fase (`Status` em `phases/` ou no hub do projeto): só o campo. A pasta do projeto **não** se move. Tarefas da fase **não** mudam de pasta.

## Tarefa

1. Atualizar **Status** na nota.
2. Mover o arquivo `.md` para o mesmo `projects/{projeto}/{fase}/` ou `independent/` no status novo. Ex.: `pending/projects/first-job/fj-01-study/study-java-basics.md` → `completed/projects/first-job/fj-01-study/study-java-basics.md`. Independente: `pending/independent/{slug}.md` → `completed/independent/{slug}.md`.
3. Se `{fase}/`, `{projeto}/`, `projects/` ou `independent/` na pasta antiga ficar sem nota, apagar. Não apagar `pending/` / `completed/` / `recurring/`.
4. Em [tasks](../../tasks/tasks.md): remover da seção antiga; se for pendente ou recorrente, listar na seção nova com caminho certo. Concluída: some do índice (não há seção de concluídos).
5. Se for de fase: atualizar o caminho em `## Tarefas` da nota da fase.
6. Buscar no vault o caminho antigo e atualizar links.

Uma tarefa recorrente que deixa de ser recorrente sai de `recurring/` e segue a tabela acima.
