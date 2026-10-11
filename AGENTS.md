# AGENTS

AI contract for the Agency Operating System (AOS). The full law is [docs/spec.md](docs/spec.md).

This repository is English. Folder names, file names, and frontmatter keys: English, kebab-case, ASCII. Timezone: `America/Sao_Paulo`. Section headings (`##`) in `{project}/notes.md`: English. That file is atemporal (spec § 2.8).

Prose inside `user/` follows `user/preferences.md`. If that file does not set a language, use the language of the current conversation.

Markdown is the source of truth. After creating or editing tasks/projects, run `aos reindex`.

## Goal

- Only the user creates and changes the goal.
- Do not declare a Goal or Tests true.
- Hub/phase Goal must be observable, or the file has `## Tests`.

## When to write

- Write a project/task only if they asked.
- Goal only → plan phases/tasks and write.
- They brought the plan → write and suggest; do not replace the plan.
- Edit an existing phase/task: conversation → agreement → then change.
- Independent: they give the simple goal; build the task; honor restrictions in `user/preferences.md` if present.

## Dates

- No `do_on`: ask at the end, after writing. Recurring `do_on` (the next occurrence, including the first): same. If they will not give one, omit `do_on`. The file is `paused`. Do not ask for a clock. It is not in the index and it does not fail.
- When a `do_on` is set, ask `do_at` (one or more `HH:MM`). If they still do not choose, omit it. The task goes under `Sem horário` and stays off the month grid.
- Maintenance has no `do_on`. Ask `do_at` when creating it. If they still do not choose, omit it. It stays active.
- Unique with `do_on`: the day is the YAML date. Scripts build `user/schedule/YYYY/YYYY-MM.md` from clocks, one table per Sunday–Saturday week. Do not write the grid by hand. Complete → scripts drop it from open columns. Closed columns stay.
- Recurring: `do_on` moves when they check it, from the scheduled day, not from today. A missed day does not move it. The series starts on the first check. On the grid, cadence days run from `do_on` through `until`, or through the current month when `until` is absent.
- The same action twice in one day is two clocks in `do_at`, or two task files when they are two actions. There is no `times`. The index shows that task once, at the first clock in the list. The month grid keeps every clock.
- H1 is the thing (`# Café da manhã`). Slug is that title in English. `infinitive` is the index phrase (`Tomar café da manhã`), required, no exceptions.
- Schedule vs task YAML conflict → the task wins.
- Plan on whichever day they want. No tasks on Sunday only if they ask (preferences).

## How and research

- Several concrete forms of the same abstraction, or a vague how → `user/research/{slug}.md`, not a task.
- Open research = empty `## Decision`. Order: Object → Question → Options → Decision → Implications.

## Close, cancel, obsolete

- Useless task: they say so + a reason → `{project}/notes.md` + move to `user/tasks/obsolete/` + rewrite links.
- `{project}/notes.md` is atemporal. Rewrite so current truth stands alone. Do not append a dated log.
- Until event / end of maintenance / cancel: only on command.
- Cancel project = move `user/projects/{status}/{slug}/` → `user/projects/canceled/{slug}/`.
- A reached goal does not become maintenance by itself. If they ask, a new maintenance is created.
- Maintenance ends only by cancel. It does not complete and does not become obsolete.

## What the agent must not do

- Do not invent people, addresses, personal dates, habits.
- Do not check `x` in the user's place.
- Do not complete a unique via cron (and the AI does not simulate cron).
- Do not cancel a project, and do not declare its Goal true, unless they asked. Other project and phase statuses follow the tasks: `reindex` and `daily-close` move the folder.
- A project they marked `completed` or `canceled` stays that way.

## After writing

Run `aos reindex`. That command, and `aos daily-close`, commit and push `user/` with the identity already configured in the vault. They do not change `git config`.
