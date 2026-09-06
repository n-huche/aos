# AGENTS

Vault Obsidian + git (`n-huche/docs`). Fonte de anotações e planos.

## Mapa

| Pasta | Uso |
|---|---|
| `domains/` | Três domínios por **finalidade**: [Dinheiro](domains/money/money.md), [Relacionamentos](domains/relationships/relationships.md), [Corpo](domains/body/body.md) — ver [domains](domains/domains.md). Em cada um: hub e `projects/` |
| `projects/` | Dentro de cada domínio (`domains/{domínio}/projects/`). Projeto canônico (template [domain-projects](templates/domain-projects.md)): `{slug}/{slug}.md`, `analysis/`, `phases/{id}-{slug-fase}.md` |
| `tasks/` | Índice em `tasks.md`; itens em `pending/`, `completed/` ou `recurring/` |
| `daily/` | Notas diárias (em construção) |
| `agents/` | Memória externa **somente do Grok Bot** (`agents/grok-bot/`). O Grok Bot define a estrutura interna dessa pasta. Cursor e demais agentes **não editam** esta pasta |
| `templates/` | Formatos canônicos — copiar ao criar nota do mesmo tipo |
| `drafts/` | Rascunhos pedidos explicitamente para docs (criar sob demanda) |

## Quem faz o quê

### Grok Bot — `agents/grok-bot/`

Usar para **pesquisas específicas** e **automações web**. Memória: [grok-bot](agents/grok-bot/grok-bot.md). Roster: [team](agents/grok-bot/team.md). Só o Grok Bot (e o Nicolas) altera essa pasta.

### Outros agentes (Cursor etc.)

Preferidos para **desenvolvimento**, **edições de texto** e **metanálises** do vault. Seguir este arquivo e `templates/`. Sem pasta de memória própria. **Não tocar** em `agents/grok-bot/`.

## Convenções

- Idioma dos **textos** do usuário: **português**.
- Nomes de **pastas e arquivos**: **inglês**, kebab-case, ASCII, sem espaços. O hub de uma pasta usa o mesmo slug.
- Completo, mas enxuto; uma fonte da verdade por tema (não duplicar tabelas/rosters).
- Status padronizado: `não iniciado` | `em andamento` | `concluído` | `não planejado` | `pausado`.
- Ao criar nota de natureza conhecida → partir do template em `templates/`.
- Links: `[nome](caminho relativo)` — não `[[wiki]]`.
- Ambiguidade factual ou de decisão → perguntar; não inventar dados pessoais.
- Cursor e demais agentes **não editam** `agents/grok-bot/`.
- Objetivo de um domínio = concluir seus `projects/`.
