# Agency Operating System (AOS)

**O que é este arquivo:** lei completa. Uma sessão IDE implementa o AOS **só a partir daqui**, criando `/workspace/aos` do zero. Sem migrar outro vault, repo ou rascunho.

**Nome:** Agency Operating System · **sigla:** AOS  
**Path a criar:** `/workspace/aos`  
**Fuso:** `America/Sao_Paulo` (Rio de Janeiro)  
**Idioma:** textos do usuário em português; pastas, arquivos, chaves de frontmatter e títulos de seção (`##`) em inglês, kebab-case, ASCII.

**v1 não inclui:** streak, progress bar, métricas leading/lagging obrigatórias, Dataview, app web, pasta `goals/`, pasta `paused/`, conteúdo real de vida (zero project/task de verdade).

---

## 1. Core idea

Ações centralizadas em **tasks**, cuja intenção é alcançar ou preservar um **estado desejado da realidade**.

- **Goal:** alcançar um estado novo.
- **Maintenance:** preservar um estado já alcançado.

Goals **simples** (uma task, ou a mesma repetida até o goal) ou **complexos** (viram **project**).

O máximo de decisão é **antes** da execução. Na execução a task é mecânica: `what` / `how` / `when`; `where` / `with who` se couber. O **how** é o campo mais crítico.

Status e evidência refletem **realidade**, não volume de trabalho. Task complete ≠ outcome positivo. Phase complete = **condition** verdadeira, não checklist 100%.

**Stack:** Markdown = source of truth · scripts determinísticos · IA no planejamento · qualquer editor como UI. O sistema **não conhece Obsidian**. Sem plugin obrigatório.

**Cadência humana:** o usuário pode planejar no domingo e só executar no resto da semana. Isso é **hábito dele**, não regra de software. Dá para planejar qualquer dia. Preferências (domingo sem task salvo pedido explícito, datas indisponíveis) ficam em `user/schedule/constraints.md`.

---

## 2. Model

```text
GOAL        estado a alcançar
  → PROJECT goal complexo
    → PHASE estado intermediário com valor próprio
      → CONDITION como sei que o estado é verdadeiro
        ↑ TASKS meios mecânicos
          → realidade / evidência / review
```

```text
estado alcançado → MAINTENANCE → tasks recorrentes → estado preservado → repeat
```

Goal atingido **não** vira maintenance sozinho. Se o usuário pedir, cria-se maintenance **nova**; a task histórica do project não muda de classe.

### 2.1 Goal

Sem pasta.

- Complexo: **Goal** + **Condition** no hub do project. Só o usuário define e só ele muda.
- Simples: na própria independent (`## Goal`).

Project-task não repete o why além de `project:` / `phase:`.

### 2.2 Project

Pasta 1:1 com status: `pending` · `ongoing` · `completed` · `canceled`.

Não existe `paused`. Pausar = `due: null` no hub. A pasta permanece `pending` ou `ongoing`.

**Completed** = o usuário declara a condition do **goal** verdadeira. Phases complete são operacionais, não autoridade.

`due` do project: data ou `null`. Sem `projects.md`. Quem muda status de project é o usuário/IA, **nunca** o cron. Mover a pasta inteira `{slug}/` (hub, `phases/`, `notes.md`). Links *dentro* do project não mudam. Links *de fora* (tasks.md não aponta project; phase aponta tasks — ver § 6.3).

### 2.3 Phase

Estado com valor próprio, não agrupador. Heurística: se tirar a phase, aquele estado ainda valeria a pena?

Complete ⇔ condition verdadeira, **mesmo com tasks pendentes**. Sobra: o usuário cita a task + motivo → IA acrescenta em `{project}/notes.md` e move o arquivo para `user/tasks/obsolete/`.

Tasks feitas + condition falsa ⇒ phase **não** complete.

Status: `pending` · `ongoing` · `completed` · `obsolete`.

Deps = grafo: frontmatter `depends_on` **e** `## Depends on` com links. Paralelo se não há aresta. Path da phase só muda se o project mudar de pasta.

### 2.4 Condition

Bloco `## Condition` na phase e no hub. Sem métricas obrigatórias na v1. **Só o usuário** declara verdadeira.

### 2.5 Task: class vs folder

`type`: `unique-independent` · `unique-project` · `recurring-independent` · `recurring-project` · `maintenance`

| Pasta | Quem |
|---|---|
| `pending/` | unique não feitas, arquivos **soltos** |
| `recurring/` | recurring-* e maintenance, **soltos**; classe só no YAML |
| `completed/` | unique feitas; recorrente com ciclo **terminado** |
| `obsolete/` | não foi necessária |
| `canceled/` | abortada pelo usuário |

Sem `ongoing` em unique. Sem subpasta `maintenance/` nem buckets de prazo em disco.

- Unique: `due` data ou `null`.
- `recurring-independent` / `recurring-project`: `until` **XOR** `until_event` obrigatório.
- `maintenance`: sem fim até o usuário mandar.

Slug de task **global**.

### 2.6 Research

Não é task. `user/research/{slug}.md`. Sob demanda ou no planejamento. Aberto = `## Decision` vazia.

Order: Object → Question → Options → Decision → Implications.

### 2.7 Notes

`{project}/notes.md` — um arquivo, criado quando houver o que registrar (outcome, task obsoleta, observação). Sem pasta `evidence/`.

---

## 3. Tree

```text
/workspace/aos/
  AGENTS.md
  docs/
    spec.md                 # esta lei, copiada para dentro do repo
    cron.md
    crontab                 # calendário; `aos up` instala com AOS_ROOT real
    templates/              # § 12
  scripts/
    aos
    aos_lib/                # Python 3, só stdlib
  user/
    projects/
      pending/{slug}/{slug}.md
      ongoing/{slug}/...
      completed/{slug}/...
      canceled/{slug}/...
        phases/{phase-slug}.md
        notes.md
    tasks/
      tasks.md
      pending/
      recurring/
      completed/
      obsolete/
      canceled/
    daily/
    research/
    schedule/
      constraints.md
      YYYY/MM/DD.md         # só data > hoje
```

Hub `user/projects/{status}/{slug}/{slug}.md`  
Phase `.../phases/{phase-slug}.md`  
Unique `user/tasks/pending/{slug}.md`  
Recorrente `user/tasks/recurring/{slug}.md`

Pasta só com nota. Links `[texto](relativo)` — nunca wiki.

Repo git. `origin` = `https://github.com/n-huche/aos.git` (privado) — durabilidade contra Update/reset desta box. Sync e daily-close fazem push se `origin` existir. `.gitignore`: `.obsidian/`, `__pycache__/`, `.DS_Store`. Não alterar `git config`.

---

## 4. Frontmatter

Canônico para scripts. `null` YAML e chave omitida = a mesma coisa para campos opcionais.

### 4.1 Unique

```yaml
---
type: unique-independent     # ou unique-project
status: pending              # pending | completed | obsolete | canceled
due: 2026-09-18              # YYYY-MM-DD ou null
completed_on: null           # preenchido no x; YYYY-MM-DD
project: my-project          # só unique-project
phase: my-phase              # só unique-project
---
```

Corpo: H1 = título (é o rótulo do índice). `## What` · `## How` · `## When` se due · `## Where` / `## With who` se couber · independent: `## Goal`.

### 4.2 Recurring

```yaml
---
type: maintenance            # ou recurring-independent | recurring-project
status: recurring
until: 2026-12-01            # XOR until_event; omitir em maintenance
until_event: null
project: my-project          # se recurring-project
phase: my-phase
done_on: []                  # ocorrências cumpridas, YYYY-MM-DD
cadence:
  kind: daily                # daily | weekdays | interval
  days: [wed, thu]           # só weekdays; mon tue wed thu fri sat sun
  every: 2                   # só interval
  unit: months               # days | weeks | months
  anchor: 2026-09-16         # só interval
---
```

`interval` + `months`: somar meses calendário; se o dia não existir no mês alvo, usar o **último dia** desse mês (31 jan + 1 month → 28/29 fev).

### 4.3 Project hub

```yaml
---
status: pending
due: null
prefix: MP
---
```

`prefix` = sigla para headings humanos das phases, não entra no filename. Filename da phase = kebab do nome.

Corpo: `## Goal` · `## Condition` · `## Phases` (links).

### 4.4 Phase

```yaml
---
status: pending
due: null
project: my-project
depends_on: [other-phase]
---
```

Corpo: `## Condition` · `## Deliverable` · `## How` · `## Depends on` · `## Tasks`.

Em `## Tasks`, link pelo **slug** relativo a `user/tasks/` **sem** assumir pasta eterna: o script, ao mover a task, **reescreve** esses links (`pending/x.md` → `completed/x.md` ou `obsolete/x.md`).

### 4.5 Research

Sem status no YAML. Headings na ordem do § 2.6. Frontmatter opcional:

```yaml
---
object: my-project           # slug de project, phase, task, ou texto livre
---
```

---

## 5. `user/tasks/tasks.md`

100% derivado. Relógio `America/Sao_Paulo`.

Título de cada linha = H1 do arquivo da task.

### 5.1 Placement

Unique: `due` null → Undefined. `due < hoje` → Overdue. Senão bucket de `delta = due - hoje`.

Recorrente: no máximo duas linhas:

1. **Today** se a cadência cai hoje e hoje ∉ `done_on`
2. um bucket da **próxima data > hoje** (uma só janela)

Sem seções Maintenance / Recurring. Overdue = **só unique**.

### 5.2 Cadence

- `daily`: hoje se ∉ `done_on`; próxima = amanhã.
- `weekdays`: próximos calendário com weekday ∈ `days`, pulando `done_on`.
- `interval`: a partir de `anchor`, avançar `every`/`unit` até datas ≥ hoje ∉ `done_on`.

### 5.3 Buckets

| condição | heading |
|---|---|
| unique `due < hoje` | `## Overdue` |
| ocorre hoje | `## Today` |
| delta == 1 | `## 1 day` |
| delta ∈ {2, 3} | `## 2-3 days` |
| delta ∈ {4, 5, 6, 7} | `## 4-7 days` |
| delta ∈ [8, 30] | `## 8-30 days` |
| delta ≥ 31 | `## +30 days` |
| unique `due` null | `## Undefined` |

Janelas rolantes. Sem semana ISO / mês civil como bucket.

Ordem: Overdue → Today → 1 day → 2-3 days → 4-7 days → 8-30 days → +30 days → Undefined.

Heading **só se** ≥1 item. Arquivo vazio permitido:

```markdown
# Tasks
```

Item:

```markdown
- [ ] [Título](pending/slug.md)
```

Relativo a `user/tasks/`. Unique: 1 linha. Recorrente: até 2, ambas com `- [ ]`.

### 5.4 Examples

`weekdays: [wed, thu]`, hoje quarta → Today + 1 day. Hoje quinta → Today + 4-7 days (próxima quarta = 6).

Intervalo 2 meses, âncora hoje → Today + +30 days. Âncora ontem → só +30 days.

`daily` → Today + 1 day se hoje ∉ `done_on`.

### 5.5 Schedule

`user/schedule/YYYY/MM/DD.md` só se `DD > hoje`. Corpo = links. Cron apaga data ≤ dia que fechou.

`constraints.md`: prosa; **script não lê**.

Conflito schedule vs YAML da task → **vale a task**.

---

## 6. Checkbox — `aos watch` / `aos sync`

Watch: inotify ou poll ≤2 s em `user/tasks/tasks.md`.

### 6.1 How to read the section

Percorrer o arquivo de cima a baixo. `## …` define a seção corrente. Cada `- [x]` ou `- [X]` herda essa seção.

Uma passagem, nesta ordem de regras:

1. Linha `[x]` cujo href está em `recurring/` **e** seção **≠** `Today` → tratar como **proibido**: a linha volta `[ ]`. Não mexe `done_on`.
2. Linha `[x]` `recurring/` na seção **Today** → § 6.2.
3. Linha `[x]` `pending/` (qualquer seção) → § 6.3.

Depois, `reindex` (reconstrói o MD). Se só houve revert da regra 1, ainda assim gravar `tasks.md` desmarcado.

### 6.2 Recurring on Today

1. Append hoje em `done_on` (sem duplicar).
2. Se `until == hoje`: `status: completed`, mover `recurring/` → `completed/`, reescrever links em phases (§ 6.4).
3. Senão o arquivo permanece em `recurring/`.
4. Commit `aos: sync tasks`. Push se `origin` existir.

### 6.3 Unique (any section)

Adiantar ok; **não** alterar `due`.

1. `status: completed`, `completed_on: <hoje>`
2. Mover `pending/` → `completed/`
3. Reescrever links § 6.4
4. Reindex, commit, push se origin

### 6.4 Rewrite links

Buscar no repo `user/` strings `pending/{slug}.md`, `recurring/{slug}.md`, etc., e apontar para a pasta nova. Inclui `## Tasks` da phase e `schedule/` futuro.

---

## 7. `aos daily-close` (00:00)

Fuso `America/Sao_Paulo`. D = dia que **acabou**. Relógio do reindex seguinte = D+1.

1. Unique ainda em `pending/` com `due==D` ou `due<D` → fracasso no daily D.
2. Recorrente cuja cadência inclui D, D ∉ `done_on`, `until != D` → fracasso; **não** Overdue; série segue.
3. Recorrente `until == D`:
   - D ∈ `done_on`: se ainda em `recurring/`, mover para `completed/` (idem § 6.2.2). Daily: feito.
   - D ∉ `done_on`: mover para `completed/` mesmo assim. Daily: **não feito**.
4. Escrever `user/daily/D.md` (idempotente se o conjunto for o mesmo).
5. Apagar `schedule` com data ≤ D.
6. Reindex com hoje = D+1.
7. Commit `aos: daily-close D`. Push se origin.

Cron **não** completa unique. **Não** move project. Until **evento** e encerrar maintenance: só comando à IA.

`daily-close` também pode ser chamado à mão. Documentar crontab em `docs/cron.md`. Watch é processo separado: `aos up` sobe se estiver morto; quem o mantém no ar depois disso é o host, não o AOS.

Se o processo ficou morto enquanto o calendário andou, `aos up` faz **catch-up** antes de subir o watch:

1. Fotografa os `[x]` ainda no `tasks.md` (o close regrava o índice).
2. `daily-close` de cada dia sem daily depois do último, até ontem (sem daily nenhum: só ontem). Sem crédito dos `[x]`. Schedule ≤ último D some.
3. Aplica os `[x]` fotografados com data = **hoje** (o dia da volta): unique `completed_on`, recorrente `done_on` só se estava em Today.
4. Reindex = hoje. O relógio que vale é o do AOS ligado.


---

## 8. Daily

`user/daily/YYYY-MM-DD.md`

```markdown
# YYYY-MM-DD

**Result:** success | satisfactory | failure

## Completed tasks

- [Título](../tasks/completed/slug.md)

## Failed tasks

- [Título](../tasks/pending/slug.md)

## Notes, optional
```

Omitir fracassadas se vazia. Recorrente concluída no dia (ainda em `recurring/`): link `../tasks/recurring/slug.md`. Recorrente encerrada no `until`: `completed/`.

**Feitas em D:** unique com `completed_on == D`; recorrente com D ∈ `done_on`.

**Fracasso em D:** unique `due==D` ou `due<D` ainda pending; recorrente com ocorrência em D sem `done_on` (incluindo `until==D` sem x).

- `failure` se ≥1 fracasso
- `satisfactory` se zero fracassos
- `success` se satisfactory **e** ≥1 unique com `completed_on==D` e `due` data ≠ D

---

## 9. Agent contract

A implementação grava isto (pode ser o corpo de `AGENTS.md`), apontando para `docs/spec.md`.

- Goal: só o usuário cria e muda.
- Escrever project/task só se ele **pediu**.
  - Só o goal → planejar phases/tasks e escrever.
  - Ele trouxe o plano → escrever e **sugerir**; não substituir o plano.
- Editar phase/task existente: conversa → acordo → aí muda.
- Independent: ele dá o simple goal; montar a task; respeitar restrições se houver.
- Sem prazo: perguntar **no fim**, depois de escrito.
- Só data final: perguntar **início** (obrigatório) → datar e preencher `schedule/`, lendo `constraints.md` e o que já cai em cada dia.
- Só data início: perguntar final; se não der, **sugerir** e agendar.
- How vago → `user/research/`, não task.
- Não declarar condition verdadeira.
- Task inútil: ele diz + motivo → `notes.md` + `obsolete/` + links.
- Until evento / fim de maintenance / cancelar: só sob comando. Cancelar project = mover `projects/{status}/{slug}/` → `projects/canceled/{slug}/`.
- Não inventar pessoas, endereços, datas pessoais, hábitos.
- Não dar `x` no lugar do usuário.
- Planejar no dia que ele quiser.
- No fim: `aos reindex`.

---

## 10. Scripts

Python 3, **somente stdlib**. `scripts/aos`:

```text
aos reindex
aos watch
aos watch --loop         # reinicia se o loop interno cair
aos sync
aos daily-close          # D = ontem no fuso, override por arg
aos validate             # type vs pasta, slug único, XOR until,
                         # cadence válida, status vs pasta, links
aos up                   # crontab de calendário + catch-up + watch se morto
aos up --quiet           # sem stdout em sucesso
aos up --watch-only      # só o watch; sem crontab nem catch-up
```

`reindex` não aplica `until` (só `daily-close` e o `x` do último dia).

---

## 11. Templates

Arquivos em `docs/templates/`. Corpo igual às seções 4.x + headings listados. Sem engine.

`project.md` · `phase.md` · `task-unique.md` · `task-recurring.md` · `research.md` · `daily.md` · `schedule-day.md`

---

## 12. Done when

1. Árvore § 3; `user/` sem vida real; `constraints.md` vazio ok.
2. `docs/spec.md` = esta lei; `AGENTS.md`; templates; `docs/cron.md`.
3. Os comandos funcionam (`reindex`, `watch`, `sync`, `daily-close`, `validate`, `up`).
4. Testes em `scripts/tests/` (não em `user/`): unique, daily, weekdays, interval, until data — seções vazias omitidas; Overdue só unique; `x` em 1 day de recorrente revertido; `x` unique move + `completed_on` + commit; `x` recorrente Today preenche `done_on`; `daily-close` until sem x → completed + daily fracasso; schedule passado some; catch-up fecha dias perdidos sem crédito e aplica `[x]` no dia da volta.
5. `origin` no GitHub; `user/` sem project/task de vida real.

---

## 13. Do not yield

- Realidade > checklist.
- Phase = estado + condition.
- Prazo é cálculo, não pasta.
- Unique: `x` move arquivo. Recorrente: `x` (só Today) registra ocorrência.
- Cron: índice + daily + schedule passado; completa recorrente só no `until` data.
- `aos up` instala o crontab de calendário (`daily-close`), faz catch-up de dias perdidos e sobe o watch se estiver morto. Não sobe o daemon `cron` nem se reinstala a cada minuto. Persistência de processos é do host.
- IA não substitui o goal nem o `x`.
