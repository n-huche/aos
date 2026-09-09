# Nova tarefa

1. `{tipo}`

   Se o chamador é [new-phase](new-phase.md): `{tipo}` = `de-projeto`. Senão: `{tipo}` = `independente` — citar um projeto no pedido não muda `{tipo}`.
   Se a nota já existe (título, slug ou pasta): atualizar — parar aqui.

2. Identidade

   Se `{tipo}` = `de-projeto`:
   - `{projeto}` = slug do hub; `{fase}` = slug da nota em `phases/` (sem `.md`) — os do chamador.
   - Faltar `{projeto}` ou `{fase}` → perguntar.
   - Status da fase = `não planejado` → parar.
   - `{ação}` = a que o chamador passou. Sem `{ação}`: uma nota por ação extraída da Entrega + Como **dessa** `{fase}`. Não varrer outras fases.

   Se `{tipo}` = `independente` e o pedido não tem **O quê** nem título: perguntar; não gravar.

   Passos 3–8 para cada nota a criar.

3. Campos — não gravar até isto fechar

   Fonte: o pedido. `{tipo}` = `de-projeto`: também a Entrega + Como da `{fase}` (nada de novo).
   `{faltas}` = lista. No fim, se `{faltas}` ≠ vazia → perguntar tudo de uma vez; não gravar.

   **Título** — rótulo curto; abstração ok. Pedido deu título curto → usar. Senão: substantivo da ação. `{slug}` = slug do título.

   **Como** — instruções na ordem, cada uma uma ação (abrir, clicar, pagar, levar, dizer). Se não der para executar o passo sem interpretar → `{faltas}`.

   **O quê** — uma frase desta execução, compactada do **Como** (o que fica feito), distinta do **Título**. Não copiar o rótulo. Sem **Como** válido: não preencher.

   **Por quê** — motivo. Faltar → `{faltas}`.

   **Quando** — opcional; não perguntar. Sem dado: omitir.

   **Onde** — se dá no celular ou no computador: omitir.
   Senão: lugar da execução. Estabelecimento sem endereço → `{faltas}`. Endereço no pedido: incluir. Cômodo ou casa já no pedido ou na fase: esse lugar, sem inventar rua. Sem lugar → `{faltas}`.

   **Com quem** — só se o pedido citou pessoa. Senão omitir.

4. `{status}`

   `{status}` = `concluído` se o pedido disse que já está feito.
   Senão `recorrente` se a ação se repete: cadência em **Quando** ou no pedido (`todo` / `cada` + período, `todo dia N`). “No domingo” / uma data / um intervalo = uma vez.
   Senão `pendente`.
   A palavra “recorrente” no pedido não conta se a ação é um único evento.

5. `{prazo}`

   Cadência (`todo` / `cada`) não vira `{prazo}`. Instante desta execução sim.

   Se `{status}` = `recorrente`: data de **fim** se o pedido deu; senão `none`. `{tipo}` ≠ `independente` e seria `none` → perguntar a data de fim; não gravar.
   Se `{status}` = `pendente`: instante desta execução (pedido ou **Quando**) → `YYYY-MM-DD` (weekday = o próximo a partir de hoje; intervalo = último dia). Instante vence “até DATE”. Só “até DATE”, sem outro instante → essa data. Sem instante → `não definido` e omitir **Quando**.
   `{tipo}` = `de-projeto` e ainda sem data: copiar o da fase.

   Se `{status}` = `recorrente` e `{prazo}` é data e hoje ≥ essa data: `{status}` = `concluído`.
   Se `{status}` = `concluído` e `{tipo}` = `de-projeto` e alguma tarefa de projeto com `nn` menor ainda não está `concluído`: recusar o `concluído`; dizer qual `{nn}` falta; `{status}` = `pendente`.

6. `{balde}` — só se `{status}` = `pendente`

   `{prazo}` = `não definido` → `undefined`.
   Senão, dias até `{prazo}` (hoje = 0): `< 0` `late` · `0` `today` · `1–3` `three-days` · `4–7` `one-week` · `8–30` `one-month` · `> 30` `long-time`.

7. Arquivo

   Pasta só com nota.

   | `{status}` | `{status-pasta}` |
   |---|---|
   | `pendente` | `pending` |
   | `concluído` | `completed` |
   | `recorrente` | `recurring` |

   `{pasta-meio}` = `independent-tasks` se `independente`; `project-tasks/{projeto}/{fase}` se `de-projeto`.
   Path: `tasks/{status-pasta}/{balde}/{pasta-meio}/{slug}.md` se `pendente`; senão `tasks/{status-pasta}/{pasta-meio}/{slug}.md`.
   Pedido posterior: o arquivo já existente vai para esse path (apagar pasta que ficar sem nota).

   Preencher [task-template](../templates/task-template.md) com o passo 3. Omitir heading vazio.
   `{tipo}` = `independente`: omitir **Fase:**.
   `{tipo}` = `de-projeto`: **Fase:** = `[PREFIXO-nn](` + `../` até a raiz do vault + `projects/{status-do-projeto}/{projeto}/phases/{fase}.md)`. Em `{fase}.md` → `## Tarefas`: `- [{Título}]({caminho relativo})` (criar o heading se não existir).

8. Índice — só se `{status}` ≠ `concluído`

   Em [tasks](../../tasks/tasks.md): `- [ ] [{Título}]({caminho a partir de tasks/})`. `{status}` = `concluído`: tirar do índice.

   | `{status}` / `{balde}` | `##` |
   |---|---|
   | `recorrente` | Recorrentes |
   | `late` | Atrasadas |
   | `today` | Hoje |
   | `three-days` | Três dias |
   | `one-week` | Uma semana |
   | `one-month` | Um mês |
   | `long-time` | Longo prazo |
   | `undefined` | Sem prazo |

   Se o `##` não existir, inserir nessa ordem. Sem `--`. Heading só com item. Pedido posterior: sair da seção antiga (apagar `##` vazio).

9. `{tipo}` = `de-projeto`: [new-phase](new-phase.md) **Status da fase ← tarefas** e **Herança**.

Pedido posterior de `{status}` / `{prazo}`: os mesmos passos 4–8; `{tipo}` = `de-projeto`: também o 9.

## Relógio, slug, O quê, Onde, links

`{hoje}` = data do relógio. `{slug}` = kebab ASCII do título (acentos removidos).

**O quê:** se o pedido deu frase distinta do Título, usar. Senão compactar o **Como** (o que fica feito). Igual ao Título → `{faltas}`.

**Onde (auto):** no celular/computador/app/site → omitir. Cômodo ou casa já no pedido ou na fase → esse lugar, sem inventar rua. Estabelecimento sem endereço → `{faltas}`. Lugar físico sem lugar → `{faltas}`.

**Fase:** `[PREFIXO-nn](` + `../` × (níveis do arquivo até a raiz do vault) + `projects/{status-do-projeto}/{projeto}/phases/{fase}.md)`.

Pedido posterior (mesmo título/slug): atualizar a nota existente (passos 3–8); mover o arquivo; não duplicar. Regrava o índice (repara índice stale).

