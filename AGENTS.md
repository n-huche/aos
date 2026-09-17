# AGENTS

Contrato da IA para o Agency Operating System (AOS). A lei completa está em [docs/spec.md](docs/spec.md).

Talk to the user in Portuguese. Folder names, file names, and frontmatter keys: English, kebab-case, ASCII. Timezone: `America/Sao_Paulo`. Section headings (`##`) in notes: English.

Markdown is the source of truth. After creating or editing tasks/projects, run `aos reindex`.

## Goal

- Só o usuário cria e muda o goal.
- Não declarar condition verdadeira.

## When to write

- Escrever project/task só se ele pediu.
- Só o goal → planejar phases/tasks e escrever.
- Ele trouxe o plano → escrever e sugerir; não substituir o plano.
- Editar phase/task existente: conversa → acordo → aí muda.
- Independent: ele dá o simple goal; montar a task; respeitar restrições em `user/schedule/constraints.md` se houver.

## Dates

- Sem prazo: perguntar no fim, depois de escrito.
- Só data final: perguntar início (obrigatório) → datar e preencher `user/schedule/YYYY/MM/DD.md`, lendo `constraints.md` e o que já cai em cada dia.
- Só data início: perguntar final; se não der, sugerir e agendar.
- Conflito schedule vs YAML da task → vale a task.
- Planejar no dia que ele quiser. Domingo sem task só se ele pedir (constraints).

## How and research

- How vago → `user/research/{slug}.md`, não task.
- Research aberto = `## Decision` vazia. Ordem: Object → Question → Options → Decision → Implications.

## Close, cancel, obsolete

- Task inútil: ele diz + motivo → `{project}/notes.md` + mover para `user/tasks/obsolete/` + reescrever links.
- Until evento / fim de maintenance / cancelar: só sob comando.
- Cancelar project = mover `user/projects/{status}/{slug}/` → `user/projects/canceled/{slug}/`.
- Goal atingido não vira maintenance sozinho. Se ele pedir, cria-se maintenance nova.

## What the agent must not do

- Não inventar pessoas, endereços, datas pessoais, hábitos.
- Não dar `x` no lugar do usuário.
- Não completar unique via cron (e a IA não simula o cron).
- Não mover project por conta própria sem pedido.
- Quem muda status de project é o usuário/IA, nunca o cron.

## After writing

Rodar `aos reindex`.
