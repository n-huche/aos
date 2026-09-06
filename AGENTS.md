# AGENTS

Vault Obsidian + git (`n-huche/docs`). Fonte de anotações e planos.

## Mapa

| Pasta | Uso |
|---|---|
| `projects/` | Índice e premissa dos eixos: [projects](projects/projects.md). Hub: `projects/{domínio}/{domínio}.md` — [Dinheiro](projects/money/money.md), [Relacionamentos](projects/relationships/relationships.md), [Corpo](projects/body/body.md). Projeto: `projects/{domínio}/{status}/{slug}/` — status: `pending` \| `in-progress` \| `completed`. Canônico (template [domain-projects](templates/domain-projects.md)): `{slug}.md`, `analysis/`, `phases/{id}-{slug-fase}.md`. Mudança de status: [status-change](agents/status-change.md) |
| `tasks/` | Índice em `tasks.md`; itens em `pending/`, `completed/` ou `recurring/` |
| `daily/` | Notas diárias (em construção) |
| `agents/` | Procedimentos compartilhados (ex.: [status-change](agents/status-change.md)). Memória do Grok Bot só em `agents/grok-bot/` — Cursor e demais **não editam** essa subpasta |
| `templates/` | Formatos canônicos — copiar ao criar nota do mesmo tipo |

## Quem faz o quê

### Grok Bot — `agents/grok-bot/`

Usar para **pesquisas específicas** e **automações web**. Memória: [grok-bot](agents/grok-bot/grok-bot.md). Roster: [team](agents/grok-bot/team.md). Só o Grok Bot (e o Nicolas) altera essa pasta.

### Outros agentes (Cursor etc.)

Preferidos para **desenvolvimento**, **edições de texto** e **metanálises** do vault. Seguir este arquivo e `templates/`. Sem pasta de memória própria. **Não tocar** em `agents/grok-bot/`.

## Convenções

- Idioma dos **textos** do usuário: **português**.
- Nomes de **pastas e arquivos**: **inglês**, kebab-case, ASCII, sem espaços. O hub de uma pasta usa o mesmo slug.
- Completo, mas enxuto; uma fonte da verdade por tema (não duplicar tabelas/rosters).
- Nunca usar `.gitkeep` nem placeholder para pasta vazia. Pasta só entra no git quando tiver nota.
- Status padronizado: `não iniciado` | `em andamento` | `concluído` | `não planejado` | `pausado`.
- Ao criar nota de natureza conhecida → partir do template em `templates/`.
- Analyses em pastas `analysis/`: slug **sem** enumeração de fase (ex.: `fj-learning.md`, `fj-stack.md` — não `fj-01-learning.md`). Fases em `phases/` podem manter id (`fj-01-study.md`).
- Links: `[nome](caminho relativo)` — não `[[wiki]]`.
- Ambiguidade factual ou de decisão → perguntar; não inventar dados pessoais.
- Cursor e demais agentes **não editam** `agents/grok-bot/`.
- Objetivo de um domínio = concluir os projetos daquele domínio em `projects/`.
- Ao mudar status de **projeto** ou **tarefa**, seguir [status-change](agents/status-change.md).
