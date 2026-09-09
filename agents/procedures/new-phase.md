# Nova fase

Não inventar datas, pessoas nem o Como. Pasta só com nota.

1. `{projeto}`

   Se o chamador é [new-project](new-project.md): o hub já existe.
   Senão: achar `projects/{pending|in-progress|paused|completed}/{slug}/{slug}.md`.
   Não achar → [new-project](new-project.md); parar.

2. Identidade

   Faltar `{slug-fase}` (arquivo, inglês), `{nome}` (heading, português) ou se é planejada vs `não planejado` → perguntar; não gravar.
   `{PREFIXO}`: o das fases no hub, ou o campo **Prefixo:**. Hub sem prefixo → perguntar.
   `{nn}`: próximo no hub (`01` se vazio). Heading duplicado → parar.
   Pedido = planejar um heading `não planejado` já no hub: esse `{nn}` — não criar outro.

3. `{status}`

   Pedido `não planejado` → `{status}` = `não planejado`.
   Senão `{status}` = `pendente`, salvo o pedido ter dado outro.
   `{status}` ∈ {`em andamento`, `pausado`, `concluído`}: se alguma `{nn}` menor ≠ `concluído` → recusar; dizer qual falta; `{status}` = `pendente`.
   Pode nascer `pendente` com `{nn}` menores ainda não `concluído`.
   Não pôr `em andamento` / `pausado` / `concluído` sem esse gate.

4. `{prazo}`

   Copiar o do projeto, salvo o pedido ter data. Não inventar.

5. Recorrente sem fim

   Cadência (`todo` / `cada`) sem data de fim: não entra na fase — não chamar [new-task](new-task.md) para essa ação. Se o pedido queria essa ação na fase → perguntar a data de fim; não gravar essa ação.

6. Arquivo

   `{pasta}` = pasta atual do projeto (`pending` | `in-progress` | `paused` | `completed`).

   Se `{status}` = `não planejado`:
   Só heading no hub: `### {PREFIXO}-{nn} — {nome}`, **Status:** `não planejado`, **Prazo:** `{prazo}`, uma frase. Sem link, sem `phases/`, sem tarefas.

   Senão:
   a. Sem **Entrega** ou sem **Como** → perguntar; não gravar.
   b. Nota `projects/{pasta}/{slug}/phases/{prefixo}-{nn}-{slug-fase}.md` a partir de [phase-template](../templates/phase-template.md). Pasta `phases/` nasce com o primeiro arquivo. Preencher **Entrega**, **Como**, **Projeto:** `[{Nome}](../{slug}.md)`, **Status**, **Prazo**, **Objetivo** (uma frase da Entrega se o pedido não deu outra). Conteúdo longo aqui, não no hub.
   c. Heading no hub: `### {PREFIXO}-{nn} — {nome}`, link para a nota, mesmo **Status** e **Prazo**, uma frase.
   d. Se **Entrega** + **Como** não derem para derivar ≥1 tarefa sem inventar → perguntar; não chamar [new-task](new-task.md).
   e. Senão: cada ação extraída desta fase → [new-task](new-task.md) (≥1). Compactar; não inventar.

   Extração: se o pedido trouxe `{ações}`, uma nota por ação nessa ordem. Senão, Entrega+Como como um procedimento único → uma nota compactada (Como = passos da fase; O quê ≠ Título; Por quê = objetivo do projeto se o pedido não deu). Cadência (`todo` / `cada`) sem data de fim: não entra; perguntar a data de fim; não chamar new-task para essa ação. Zero ações deriváveis sem inventar → perguntar; não chamar new-task.

7. **Status da fase ← tarefas**

   Só planejada. Gate do passo 3 para o status resultante: falhou → não mudar para `em andamento` / `pausado` / `concluído`.
   Pela ordem de `## Tarefas`:
   - primeira `concluído` e ainda há outra não `concluído` → `{status}` = `em andamento`
   - todas `concluído` (recorrente com data conta) → `{status}` = `concluído` (uma só tarefa: `pendente` → `concluído`)
   - `pausado` só se o pedido pediu (mesmo gate)
   Atualizar a nota em `phases/` e o heading no hub.

8. **Herança**

   No hub, por `{nn}`: primeira fase ≠ `concluído`:
   - `em andamento` | `pausado` | `pendente` → `{status-projeto}` = esse
   - `não planejado` → `{status-projeto}` = `pendente`
   - todas `concluído` e nenhum heading `não planejado` → `{status-projeto}` = `concluído`
   Projeto nunca usa `não planejado`.

   Pasta: `pendente` `pending` · `em andamento` `in-progress` · `pausado` `paused` · `concluído` `completed`.
   Atualizar **Status** no hub.
   Pasta 1:1 — se mudou: mover `projects/{antigo}/{slug}/` → `projects/{novo}/{slug}/`.
   Em [projects](../../projects/projects.md): o item deste projeto só na seção do `{status-projeto}` (`- [{Nome}]({status}/{slug}/{slug}.md) — {blurb}` com `{blurb}` = objetivo). **Pendente · Em andamento · Pausado · Concluído**; criar `##` se faltar; apagar `##` vazio. Sem `--`. `##` só com item.
   Links *dentro* do projeto não mudam. Buscar no vault `projects/{antigo}/{slug}` e atualizar (incl. **Fase:** nas tarefas).

Pedido posterior de status/prazo: passos 3, 7 e 8. De `não planejado` para planejada: este procedimento desde o passo 2.
