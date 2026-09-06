# Novo projeto

Não inventar domínio, datas, pessoas nem fases. Sem `.gitkeep`. Não editar `agents/grok-bot/` (memória do Grok Bot). `agents/procedures/` e `agents/templates/` são compartilhados. Hub a partir de [project-template](../templates/project-template.md). Análise, se houver, a partir de [analysis-template](../templates/analysis-template.md). Fase a partir de [phases-template](../templates/phases-template.md). Pasta só com nota dentro.

| Campo | Pasta |
|---|---|
| `não iniciado` \| `não planejado` \| `pausado` | `projects/pending/{domínio}/` |
| `em andamento` | `projects/in-progress/{domínio}/` |
| `concluído` | `projects/completed/{domínio}/` |

Domínio = **finalidade** ([glossário](../../AGENTS.md)): `money` · `relationships` · `body`. Não o tema aparente.

## Antes de criar

1. Confirmar que não existe projeto no mesmo fim (buscar slug, nome, pasta). Se existir, atualizar o que já está — não duplicar.
2. Se faltar **domínio**, **objetivo em uma frase**, **slug** ou **fases**, perguntar. Default de status: `não iniciado` → `pending/`, salvo o usuário dizer outro.
3. Slug da pasta = slug do hub = inglês, kebab-case, ASCII. Título do hub pode ser o nome falado (ex.: First Job, Ana Year One). Textos em português.
4. Prefixo de fase: sigla curta em maiúsculas (ex.: `FJ`, `AY1`). Arquivo da fase: `{prefixo-minúsculo}-{nn}-{slug-fase}.md` — slug da fase em inglês. Heading no hub: `{PREFIXO}-{nn}-{slug-fase}`.

## Criar

1. Pasta `projects/{status}/{domínio}/{slug}/`. Não criar `projects/{status}/{domínio}/` se for ficar vazia além deste projeto — a pasta do domínio nasce com o slug.
2. Hub `{slug}.md` pelo template. Preencher objetivo e **Status geral**. **Análise:** links reais, ou `_(ainda não)_` — não criar `analysis/` vazia nem nota placeholder.
3. Cada fase **planejada** (`não iniciado` ou além): nota em `phases/{id}-{slug-fase}.md` e entrada no hub (link + status + uma frase de entrega). Fase `não planejado`: só heading + status no hub — **sem arquivo**.
4. Nota de fase: copiar [phases-template](../templates/phases-template.md):

```
# {{PREFIXO}}-{{nn}} — {{nome em português}}

**Objetivo:** _uma frase_  
**Status:** não iniciado | em andamento | concluído | não planejado | pausado  
**Projeto:** [{{Nome}}](../{{slug}}.md)

## Entrega

- _o que esta fase deixa pronto_

---

Obs: Campos extras (`**Rotina:**`, `**Stack:**`, `**Regra:**`, etc.) e seções depois da Entrega (spec, mapa, inventário, apoio) só se o usuário trouxe conteúdo. Não criar seções vazias. Itens de portfólio, se houver, ficam neste arquivo — não em nota à parte.
```

Conteúdo longo fica na fase, não no hub.
5. Análise só se o usuário pediu ou já trouxe a decisão. Slug **sem** id de fase (`{slug}-stack.md`, não `{prefixo}-01-stack.md`). Pasta `analysis/` nasce com o primeiro arquivo.
6. Não criar `learning-method.md`, spec extra, nem outras notas “por se acaso”. Itens de portfólio (se houver) ficam no **corpo da fase**, não em nota à parte.
7. Em [projects](../../projects/projects.md): na seção de status + domínio, item `- [{Nome}]({status}/{domínio}/{slug}/{slug}.md) — {blurb}`. Trocar `--` se a seção estava vazia.
8. Links `[nome](caminho relativo)` — não `[[wiki]]`. Buscar no vault (exceto `agents/grok-bot/`) menções ao tema e apontar para o hub quando fizer sentido.

Mudança de status **depois** de criado: [status-change](status-change.md).
