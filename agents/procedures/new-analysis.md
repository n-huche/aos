# Nova análise

Pesquisa quando o objetivo de um projeto ou de uma fase **não tem caminho claro** para ação. Ajuda a descobrir o "o quê" e o "como". Não inventar pessoas, datas, opções nem achados.

Pasta `analysis/` só com nota. Slug **sem** id de fase (`PREFIXO-nn`).

## Relógio

`{hoje}` = data do relógio. **Atualizado:** `{hoje}`.

## 1. Objeto

`{projeto}` = slug do hub. Achar `projects/{pending|in-progress|paused|completed}/{slug}/{slug}.md`.
Não achar → [new-project](new-project.md); parar.

`{alvo}` = `projeto` | `fase`.
Se `{alvo}` = `fase`: `{fase}` = stem da nota em `phases/` (sem `.md`). Fase `não planejado` ou nota inexistente → perguntar; não gravar.

Pedido diz que o caminho (o quê / como) **já está claro** → não gravar.

## 2. Identidade

Faltar `{titulo}` ou `{pergunta}` (uma frase) ou `{objeto}` → perguntar tudo de uma vez; não gravar.

`{slug}` = kebab ASCII do título. Não pode começar com `{PREFIXO}-{nn}-`.
Já existe `analysis/{slug}.md` → atualizar o arquivo; não duplicar.

## 3. Campos

Fonte: o pedido. Não inventar.

| Campo | Obrigatório | Se faltar |
|---|---|---|
| Título, Pergunta, Objeto | sim | perguntar; não gravar |
| Fontes | não | `_(ainda não)_` |
| Contexto, Opções, Achados, Decisão, Implicações, Riscos, Critério de sucesso | não | omitir o heading |

## 4. Arquivo

`projects/{pasta}/{projeto}/analysis/{slug}.md` a partir de [analysis-template](../templates/analysis-template.md).
Pasta `analysis/` nasce com o primeiro arquivo.

Links `[nome](caminho relativo)` — não `[[wiki]]`.

## 5. Hub

Campo **Análise:** no hub:
- se era `_(ainda não)_` → `[título](analysis/{slug}.md)`
- senão acrescentar ` · [título](analysis/{slug}.md)`

Não chama [new-task](new-task.md) nem [new-phase](new-phase.md). Não muda status nem prazo.

Análise **antes** da fase cuja complexidade a justifica — ver [new-project](new-project.md).
