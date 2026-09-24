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

- No due: ask at the end, after writing. Recurring `due` (the deadline to start): same. `due` null gets no `do_in` and no `do_after`, and the agent does not ask for them.
- When a `due` is set, ask `do_in` (`HH:MM`) or `do_after` (slug). If they still do not choose, omit both.
- Maintenance has no `due`. Ask `do_in` or `do_after` when creating it. If they still do not choose, omit both.
- Unique with due: YAML `due` + **one** day in `user/schedule/YYYY/MM/DD.md` (the due, if `due > today`). Do not spread the task across other days. Complete → scripts drop it from `schedule/`.
- Recurring `due`: ask at the end; if they will not give one, `due: null` (file in `pending/`, Undefined). Schedule lists a future `due` and/or a future `until` — not every occurrence. The series starts when they check it the first time, not on the due date.
- The same action twice in one day is two task files, each with its own `do_in` or `do_after`. There is no `times`.
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
- Do not move a project on its own without being asked.
- Who changes project status is the user/AI, never cron.

## After writing

Run `aos reindex`.
