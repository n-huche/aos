# Agency Operating System (AOS)

**What this file is:** the full law. An IDE session implements AOS **from this document only**, creating the repo from scratch. Do not migrate another user tree, repo, or draft.

**Name:** Agency Operating System · **abbrev:** AOS  
**Root:** any directory; `aos` finds it via `AOS_ROOT` or the folder that contains `scripts/`.  
**Timezone:** `America/Sao_Paulo` (Rio de Janeiro)  
**Language:** this repository (law, scripts, templates, tests) is English. Folder names, file names, frontmatter keys, and section headings (`##`) are English, kebab-case, ASCII. Prose inside the nested `user/` tree follows `user/preferences.md`. If that file does not set a language, use the language of the current conversation.

**v1 does not include:** streaks, progress bars, mandatory leading/lagging metrics, Dataview, a web app, a `goals/` folder, a `paused/` folder, or real life content (zero real projects/tasks in this public tree).

---

## 1. Core idea

Actions are centralized in **tasks**, whose intent is to reach or preserve a **desired state of reality**.

- **Goal:** reach a new state.
- **Maintenance:** preserve a state already reached.

A goal is an abstraction. Far from what can be executed, the path to reality is not obvious. AOS **lowers** that abstraction until something concrete can run.

- **Simple:** already close to concrete. No intermediate split. One task, or the same one repeated until the goal.
- **Complex:** composed of lower abstractions. Those become **phases** (a **project**). No nesting: if a phase is still too abstract, the pieces are also phases, and the higher phase `depends_on` them.

A **task** is not a smaller phase. Decomposition stops there: one concrete form is chosen. The same abstraction often admits several concretions; **research** picks which is adequate. Then execution is mechanical: `what` / `how` / `when`; `where` / `with who` if they apply. **How** is the most critical field.

Status and evidence reflect **reality**, not volume of work. Task complete ≠ positive outcome. Phase or project complete = **Goal** true (or **Tests**, if present), not a 100% checklist.

**Stack:** Markdown = source of truth · deterministic scripts · AI for planning · any editor as UI. The system **does not know Obsidian**. No required plugin.

**Human cadence:** the user may plan on Sunday and only execute later in the week. That is **their habit**, not a software rule. Planning can happen on any day. Preferences (no tasks on Sunday unless they ask, unavailable dates, language) live in `user/preferences.md`.

---

## 2. Model

```text
GOAL        abstraction to make real (Tests if not observable)
  → PROJECT when it must split
    → PHASE lower abstraction (flat; depends_on)
      → PLAN  the descent at that level
        ↑ TASKS chosen concrete form
          → reality / evidence / review
```

```text
state reached → MAINTENANCE → recurring tasks → state preserved → repeat
```

A reached goal **does not** become maintenance by itself. If the user asks, a **new** maintenance is created; the historical project task does not change class.

### 2.1 Goal

No folder. The statement of the abstraction at that level: a **state** to make real.

- Complex (project hub): global at that abstraction. Only the user defines it and only the user changes it.
- Phase: local at that abstraction.
- Simple: on the independent task itself (`## Goal`).

A project-task does not repeat the why beyond `project:` / `phase:` — no `## Goal` on it.

The Goal must be observable, or the file has `## Tests`. Both vague is illegal.

### 2.2 Project

Folder 1:1 with status: `pending` · `ongoing` · `completed` · `canceled`.

There is no `paused`. Pause = `due: null` on the hub. The folder stays `pending` or `ongoing`.

**Completed** = the user declares the hub Goal true (or its Tests, if present). Completed phases are operational, not authority.

Project `due`: a date or `null`. No `projects.md`. Who changes project status is the user/AI, **never** cron. Move the whole `{slug}/` folder (hub, `phases/`, `notes.md`). Links *inside* the project do not change. Links *from outside* (`tasks.md` does not point at projects; a phase points at tasks — see § 6.3).

### 2.3 Phase

A lower abstraction that is still a state, not a bucket. Heuristic: if you removed the phase, would that state still be worth having? After a split, keep the higher phase only if its Goal is not merely the AND of `depends_on`. If it is only that AND, it is a ghost level: delete it; the hub Goal aggregates.

Complete ⇔ the phase Goal is true (Tests if present), **even with pending tasks**. Leftover: the user names the task + a reason → the AI appends to `{project}/notes.md` and moves the file to `user/tasks/obsolete/`.

Tasks done + Goal false ⇒ the phase is **not** complete. Plan done ≠ complete.

Status: `pending` · `ongoing` · `completed` · `obsolete`.

Deps = a graph in frontmatter `depends_on` (slugs). No body section. Further descent = new phases on the same graph; the still-abstract phase depends on them. Parallel if there is no edge. The phase path only changes if the project folder changes.

No `## How`, no `## Deliverable`, no `## Condition` on the phase. Concretion is the task. Several possible forms → `user/research/`.

### 2.4 Tests

`## Tests` on the hub or phase **only** when that level's Goal is not itself observable. Omit when the Goal is the test.

If Tests exist, the user declares the Tests; otherwise the Goal. **Only the user** declares it true. Not metrics: observable proxies (pass Y, create Z). No mandatory numbers in v1.

### 2.5 Plan

`## Plan` always on the hub and on the phase. Numbered list (`1.` `2.` `3.` …) of **what to do** at that abstraction level, in graph order (`depends_on`), not calendar time. One item per cut; not always three. Hub: the phases. Phase: the next drop (usually the tasks). Same altitude as this file's Goal — not the mechanical `## How` of a task. Identity stays in `## Phases` / `## Tasks` (links).

### 2.6 Task: class vs folder

`type` is required YAML. Values: `unique-independent` · `unique-project` · `recurring-independent` · `recurring-project` · `maintenance`

| Folder | Who |
|---|---|
| `pending/` | unfinished uniques; recurring-* that has not started |
| `ongoing/` | live recurring-* and live maintenance |
| `completed/` | finished uniques; recurring whose cycle **ended** |
| `obsolete/` | unique or recurring that was not needed |
| `canceled/` | aborted by the user, including a maintenance the user stopped |

No `ongoing` status for uniques. No `completed` or `obsolete` for maintenance. No due-date buckets on disk. There is no `times` field.

- Unique: `due` a date or `null`. Status: `pending` · `completed` · `obsolete` · `canceled`.
- Recurring: `due` is the deadline to **start**, or `null`. `until` **XOR** `until_event`. Status: `pending` · `ongoing` · `completed` · `obsolete` · `canceled`.
- `due` null → the series has not begun: file stays in `pending/`, `status: pending`, Undefined, **no** daily occurrence. The user may start whenever they want. Cron does **not** move the file on `due`.
- The first `[x]` starts the series, in any section: `status: ongoing`, move `pending/` → `ongoing/`, and that day is `done_on`. Later `[x]` count only in **Today**.
- After it is `ongoing`, `due` is only a record. Occurrences follow the cadence. The first check counts even off a cadence day. The next ones follow the cadence. `cadence.anchor` is not rewritten.
- Passed `due` still `pending`: **Overdue**. The daily fails each day until the first check.
- `maintenance`: cadence; no `due`, no `until`. Status: `ongoing` · `canceled` only. Folder `ongoing/` while live. It does not complete and does not become obsolete.

Task slugs are **global**.

Unstarted recurring and unique share `pending/`. Class is YAML `type`, not the folder.

### 2.7 Research

Not a task. `user/research/{slug}.md`. The same abstraction often admits several concrete forms; research chooses which is adequate — including a still-vague how. On demand or during planning. Open = empty `## Decision`.

Order: Object → Question → Options → Decision → Implications.

### 2.8 Notes

`{project}/notes.md` — one file, created when there is something to record (outcome, obsolete task, observation). No `evidence/` folder.

**Atemporal.** The file states what remains true of the project. It is not a log and not a snapshot of status.

- Headings (`##`) are English. No dates in headings.
- Status, dues, and diary words (`already` / `pending` / `ongoing` as a journal of when something was true) live in YAML, `daily/`, and git — not here.
- A sentence that needs its writing date to stay true does not belong.
- When a fact dies: rewrite or delete. Do not append a later correction.

Daily `## Notes, optional` are of that day. They are not this file.

---

## 3. Tree

```text
aos/                        # repo root (wherever it lives)
  AGENTS.md
  README.md
  docs/
    spec.md                 # this law, copied into the repo
    cron.md
    crontab                 # calendar; `aos up` installs it with the real AOS_ROOT
    templates/              # § 11
  scripts/
    aos
    aos_lib/                # Python 3, stdlib only
  user/
    preferences.md
    projects/
      pending/{slug}/{slug}.md
      ongoing/{slug}/...
      completed/{slug}/...
      canceled/{slug}/...
        phases/{prefix}-{nn}-{name}.md
        notes.md
    tasks/
      tasks.md
      pending/
      ongoing/
      completed/
      obsolete/
      canceled/
    daily/
    research/
    schedule/
      YYYY/MM/DD.md         # unique: the due; pending recurring: the due; recurring: until; only if > today
```

Hub `user/projects/{status}/{slug}/{slug}.md`  
Phase `.../phases/{prefix}-{nn}-{name}.md`  
Unique `user/tasks/pending/{slug}.md`  
Unstarted recurring `user/tasks/pending/{slug}.md`  
Live recurring and live maintenance `user/tasks/ongoing/{slug}.md`

A folder may exist with only a note. Links `[text](relative)` — never wiki links.

Two gits, one disk. This law (`scripts/`, `docs/`) is the public repo; `origin` = `https://github.com/n-huche/aos.git`. Life (`user/`) is a **nested** git at `user/.git` — a private repo, not a submodule, not `AOS_ROOT`. The public clone gitignores `/user/` and does not ship real projects/tasks. On disk the root still needs `user/`: clone your private user repository into `user/`, or mkdir the empty tree from this § 3.

`commit_user` / `push_if_origin`: if `user/.git` exists, add/commit/push **there**. Otherwise (test fixtures) the parent runs `git add user`. Sync and daily-close push if **that** git has an `origin`. Parent `.gitignore`: `.obsidian/`, `__pycache__/`, `.DS_Store`, `logs/`, `/user/`. Do not change `git config`.

---

## 4. Frontmatter

Canonical for scripts. YAML `null` and an omitted key are the same for optional fields.

### 4.1 Unique

```yaml
---
type: unique-independent     # or unique-project
status: pending              # pending | completed | obsolete | canceled
due: 2026-09-18              # YYYY-MM-DD or null
completed_on: null           # filled on check; YYYY-MM-DD
infinitive: Do the thing     # index label; required
project: my-project          # unique-project only
phase: mp-01-my-phase        # unique-project only; filename stem
---
```

Body: H1 is the thing, not the act (`# Café da manhã`). The slug is that title in English (`breakfast`). `infinitive` is the index phrase (`Tomar café da manhã`). `## What` · `## How` · `## When` if due · `## Where` / `## With who` if they apply · independent: `## Goal`.

### 4.2 Recurring

```yaml
---
type: recurring-independent  # or recurring-project
status: pending              # pending | ongoing | completed | obsolete | canceled
due: 2026-10-01              # deadline to start; YYYY-MM-DD or null
until: 2026-12-01            # XOR until_event
until_event: null
infinitive: Do the thing
project: my-project          # recurring-project only
phase: mp-01-my-phase        # filename stem
done_on: []                  # at most the open day; a later date may remain across catch-up
cadence:
  kind: daily                # daily | weekdays | interval
  days: [wed, thu]           # weekdays only; mon tue wed thu fri sat sun
  every: 2                   # interval only
  unit: months               # days | weeks | months
  anchor: 2026-09-16         # interval only
---
```

`status: pending` while unstarted (folder `pending/`). `status: ongoing` while live (folder `ongoing/`).

One `[x]` on a live series in **Today** records that day in `done_on` and the line leaves Today. There is no intra-day quota. `done_on` holds at most that open day. On daily-close of D, D is removed. A later date stays. The history of the day lives in `daily/`.

### 4.2.1 Maintenance

```yaml
---
type: maintenance
status: ongoing              # ongoing | canceled
infinitive: Do the thing
done_on: []
cadence:
  kind: daily                # daily | weekdays | interval
  days: [wed, thu]
  every: 2
  unit: months
  anchor: 2026-09-16
---
```

No `due`, no `until`. Folder `ongoing/` while live, `canceled/` when the user stops it. Same `done_on` rule as recurring.

`interval` + `months`: add calendar months; if the day does not exist in the target month, use the **last day** of that month (31 Jan + 1 month → 28/29 Feb).

### 4.3 Project hub

```yaml
---
status: pending
due: null
prefix: MP
---
```

`prefix` = short label for the project. It enters the phase filename and the phase H1.

Phase filename = `{prefix}-{nn}-{name}.md`, all lowercase. `nn` is a two-digit id assigned at creation (next unused number in that project). It does not change if `## Phases` is reordered. Example: prefix `F`, name Box access → `f-01-box-access.md`.

H1 = `{PREFIX}-{nn} {Name}` with `prefix` as written in YAML. Example: `# F-01 Box access`.

Slug = filename stem. Same stem in `depends_on`, task `phase:`, and links. One identity.

Body: `## Goal` · `## Tests` (only if Goal is not observable) · `## Plan` (numbered list) · `## Phases` (links).

### 4.4 Phase

```yaml
---
status: pending
due: null
project: my-project
depends_on: [mp-01-other-phase]
---
```

Body: `## Goal` · `## Tests` (only if Goal is not observable) · `## Plan` (numbered list) · `## Tasks`. How is the task's field. Deps are YAML only.

In `## Tasks`, link by **slug** relative to `user/tasks/` **without** assuming a forever folder: when the script moves the task, it **rewrites** those links (`pending/x.md` → `completed/x.md` or `obsolete/x.md`).

### 4.5 Research

No status in YAML. Headings in the order of § 2.7. Optional frontmatter:

```yaml
---
object: my-project           # project, phase, task slug, or free text
---
```

### 4.6 Preferences

`user/preferences.md`. Prose for the agent. No required frontmatter. Scripts **do not read** it.

Suggested headings: `## Language` · `## Restrictions`. The user may add more.

---

## 5. `user/tasks/tasks.md`

100% derived. Clock `America/Sao_Paulo`.

The label of each line is `infinitive`, never the H1. A missing `infinitive` is an index error.

### 5.1 Placement

Unique: `due` null → Undefined. `due < today` → Overdue. Else bucket of `delta = due - today`.

Unstarted recurring (`pending/`, `due` null) → Undefined. Unstarted with a future `due` → bucket of `delta = due - today`. Unstarted with `due < today` → Overdue. Href `pending/{slug}.md`. The first `[x]` starts the series (§ 6.1).

Live recurring and maintenance (`ongoing/`): at most two lines:

1. **Today** if the cadence falls today and today is not in `done_on`
2. one bucket for the **next cadence date > today**

No Maintenance / Recurring sections. Overdue holds uniques past due and recurring still `pending` past due.

### 5.2 Cadence

- `daily`: today if not done; next = tomorrow.
- `weekdays`: next calendar dates whose weekday ∈ `days`, skipping a date already in `done_on`.
- `interval`: from `anchor`, step `every`/`unit` until dates ≥ today not in `done_on`. The first check does not change `anchor`.

### 5.3 Buckets

| condition | heading |
|---|---|
| unique `due < today` | `## Overdue` |
| occurs today | `## Today` |
| delta == 1 | `## 1 day` |
| delta ∈ {2, 3} | `## 2-3 days` |
| delta ∈ {4, 5, 6, 7} | `## 4-7 days` |
| delta ∈ [8, 30] | `## 8-30 days` |
| delta ≥ 31 | `## +30 days` |
| unique or unstarted recurring `due` null | `## Undefined` |

Rolling windows. No ISO week / civil month as a bucket.

Order: Overdue → Today → 1 day → 2-3 days → 4-7 days → 8-30 days → +30 days → Undefined.

Heading **only if** ≥1 item. Empty file allowed:

```markdown
# Tasks
```

Item:

```markdown
- [ ] [Tomar café da manhã](ongoing/breakfast.md)

### Depois de tomar café da manhã

- [ ] [Postar vídeo para namorada](ongoing/video-for-girlfriend.md)
```

Relative to `user/tasks/`. Unique: 1 line. Recurring (live or unstarted) and maintenance: up to 2 live lines, or 1 unstarted line; all `- [ ]`.

### 5.3.1 Order inside a bucket

The order is a suggestion. The checkbox does not depend on position.

In a bucket that spans more than one day, the occurrence day comes first.

`do_in` is `HH:MM` (24h, `America/Sao_Paulo`). `do_after` is a task slug. A task has one of them, or neither. Both is an error. A cycle, or a slug that does not exist, is an index error.

A `do_in` task is a fence. Tasks with `do_after` pointing at it sit after it and before the next later `do_in` that day. The block stays together: the task, its children, and their children. Two tasks with the same `do_in` are two fences, ordered by the five bands below. Each has its own heading if it has children. Those children come before the next later time.

Inside one parent, the bands are:

1. maintenance
2. recurring independent
3. unique independent
4. recurring project
5. unique project

Tasks of the same project stay in `## Phases` order and then `## Tasks` order, across types. The five bands apply only between different projects, and between tasks that have no project. A project takes the band of its earliest type in that list. Inside a band, tasks without a project sort by `infinitive`. Between projects in the same band, sort by the project H1.

A `do_in` line stays `- [ ]`. If that section has a child, the next heading is `### Depois de {infinitive}`. A child that itself has children uses `####`. Deeper than that stays a list under the nearest `do_in`, with no further heading. The clock is not written in the heading. The heading is omitted when no child remains in the section. If the parent is already absent from the section, the heading still shows while a child remains.

`###` does not change the bucket. Sync reads only a line that starts with `## `.

Tasks with neither key go at the end of the section, under `### Sem posição`, in the five bands. Undefined has no `###` headings: only the five bands, and the same project grouping.

`due` null (unique, or recurring still `pending`) forbids `do_in` and `do_after`. The agent asks for one of them only when a `due` is set. Maintenance has no `due`; the agent asks at creation. If the user still does not choose, the task is unplaced.

The phrases `Depois de` and `Sem posição` are fixed. Scripts do not read `preferences.md`.

### 5.4 Examples

`weekdays: [wed, thu]`, today Wednesday → Today + 1 day. Today Thursday → Today + 4-7 days (next Wednesday = 6).

2-month interval, anchor today → Today + +30 days. Anchor yesterday → only +30 days.

`daily` → Today + 1 day if today is not in `done_on`.

### 5.5 Schedule

`user/schedule/YYYY/MM/DD.md` only if `DD > today`. Body = links. Cron deletes dates ≤ the day it closed.

Unique: **the due only** (one file, the deadline day). When the unique completes, scripts **drop it from `schedule/`** (the line). If that day has no links left, delete the file. Pending recurring: a future `due` if it exists, and a future `until` if it exists — not every cadence occurrence. Maintenance: not on the schedule.

`user/preferences.md`: prose; **scripts do not read it**.

Schedule vs task YAML conflict → **the task wins**.

---

## 6. Checkbox — `aos watch` / `aos sync`

Watch: inotify or poll ≤2 s on `user/tasks/tasks.md`.

### 6.1 How to read the section

Walk the file top to bottom. A line `## …` sets the current section. `###` does not. Each `- [x]` or `- [X]` inherits that section.

One pass, rules in this order:

1. An `[x]` line whose href is in `ongoing/` **and** section **≠** `Today` → **forbidden**: the line goes back to `[ ]`. Do not touch `done_on`.
2. An `[x]` `ongoing/` line in section **Today** → § 6.2.
3. An `[x]` `pending/` line whose task `type` is recurring-* → start the series (§ 6.2), in any section including Overdue and Undefined.
4. An `[x]` `pending/` unique (any section) → § 6.3.

Then `reindex` (rebuilds the MD). If the only action was reverting rule 1, still write `tasks.md` unchecked.

### 6.2 Series check

Live series (recurring or maintenance) in **Today**:

1. Record today in `done_on` (drop earlier dates; keep a later date).
2. Recurring with `until == today`: `status: completed`, move `ongoing/` → `completed/`, rewrite links (§ 6.4).
3. Otherwise the file stays in `ongoing/`. Reindex drops the Today line.
4. Commit `aos: sync tasks`. Push if `origin` exists.

First `[x]` on a `pending` recurring, any section:

1. `status: ongoing`, move `pending/` → `ongoing/`, record today in `done_on`.
2. If `until == today`, complete it as above.
3. Reindex. That day counts even when it is not a cadence day.

### 6.3 Unique (any section)

Early check is OK; **do not** change `due`.

1. `status: completed`, `completed_on: <today>`
2. Move `pending/` → `completed/`
3. Drop the unique from `schedule/` (§ 5.5)
4. Rewrite links § 6.4
5. Reindex, commit, push if origin

### 6.4 Rewrite links

Search the `user/` tree for strings `pending/{slug}.md`, `ongoing/{slug}.md`, etc., and point them at the new folder. Includes the phase `## Tasks`. Not `schedule/`: that is dropped on unique complete (§ 6.3), not rewritten.

---

## 7. `aos daily-close` (00:00)

Timezone `America/Sao_Paulo`. D = the day that **ended**. The next reindex clock = D+1.

1. Unique still in `pending/` with `due==D` or `due<D` → failure on daily D.
2. Recurring still `pending` with `due==D` or `due<D` → failure. It stays `pending`. No cadence occurrence until the first check.
3. Live recurring whose cadence includes D and D is not in `done_on`, `until != D` → failure; the series continues. The same for maintenance.
4. Recurring `until == D` (the series is `ongoing`):
   - D in `done_on`: move `ongoing/` → `completed/`. Daily: done.
   - D not in `done_on`: move to `completed/` anyway. Daily: **not done**.
5. Write `user/daily/D.md` (idempotent if the set is the same).
6. Remove D from `done_on`. A later date stays.
7. Delete `schedule` dates ≤ D. Non-date markdown under `schedule/` is left alone.
8. Reindex with today = D+1.
9. Commit `aos: daily-close D`. Push if origin.

Cron **does not** complete uniques. **Does not** move projects. **Does not** start a recurring series. Until **event** and canceling maintenance: AI command only.

`daily-close` can also be run by hand. Document the crontab in `docs/cron.md`. Watch is a separate process: `aos up` starts it if it is dead; keeping it alive after that is the host, not AOS.

If the process was dead while the calendar moved, `aos up` does **catch-up** before starting watch:

1. Snapshot leftover `[x]` in `tasks.md` (close rewrites the index).
2. `daily-close` each day without a daily after the last one, through yesterday (no daily at all: yesterday only). Those days get no credit for the `[x]`. Schedule ≤ last D goes away.
3. Apply the snapshotted `[x]` with date = **today** (the day of return): unique `completed_on`; a live series `done_on` only if it was in Today; a pending recurring starts.
4. Reindex = today. The clock that counts is the AOS that is up.


---

## 8. Daily

`user/daily/YYYY-MM-DD.md`

```markdown
# YYYY-MM-DD

**Result:** success | satisfactory | failure

## Completed tasks

- [Title](../tasks/completed/slug.md)

## Failed tasks

- [Title](../tasks/pending/slug.md)

## Notes, optional
```

Omit failed if empty. Live series: link `../tasks/ongoing/slug.md`. Recurring closed on `until`: `completed/`.

**Done on D:** unique with `completed_on == D`; live recurring/maintenance with D in `done_on`.

**Failure on D:** unique `due==D` or `due<D` still pending; recurring still `pending` with `due<=D`; live recurring/maintenance with an occurrence on D and D not in `done_on` (including `until==D` without the day). Unstarted recurring with `due` null does not fail.

- `failure` if ≥1 failure
- `satisfactory` if zero failures
- `success` if satisfactory **and** ≥1 unique with `completed_on==D` and `due` date ≠ D

---

## 9. Agent contract

The implementation writes this (it may be the body of `AGENTS.md`), pointing at `docs/spec.md`.

- Goal: only the user creates and changes it.
- Write a project/task only if they **asked**.
  - Goal only → plan phases/tasks and write.
  - They brought the plan → write and **suggest**; do not replace the plan.
- Edit an existing phase/task: conversation → agreement → then change.
- Independent: they give the simple goal; build the task; honor `user/preferences.md` if present.
- Talk and write `user/` prose in the language `user/preferences.md` sets. If it does not set one, use the language of the current conversation.
- No due: ask **at the end**, after writing. Recurring `due`: same — ask at the end; if they will not give one, leave `due: null` (pending / Undefined, no `do_in` / `do_after`). When `due` is set, ask `do_in` or `do_after`.
- Unique with due: YAML + `schedule/` **only on the due** (if `due > today`). Do not ask for a start date. Complete → scripts drop it from `schedule/`.
- Start date only: ask for the due; if they will not give one, **suggest** and schedule on the due.
- Recurring on the schedule: a future `due` and/or a future `until`, not every occurrence.
- The same action twice in one day is two files. There is no `times`.
- Several concrete forms, or a vague how → `user/research/`, not a task.
- Do not declare a Goal or Tests true.
- Useless task: they say so + a reason → `notes.md` + `obsolete/` + links.
- `{project}/notes.md` is atemporal (§ 2.8). Rewrite so current truth stands alone. Do not append a dated log.
- Until event / end maintenance / cancel: only on command. Cancel project = move `projects/{status}/{slug}/` → `projects/canceled/{slug}/`.
- Do not invent people, addresses, personal dates, habits.
- Do not check `x` in the user's place.
- Plan on whichever day they want.
- At the end: `aos reindex`.

---

## 10. Scripts

Python 3, **stdlib only**. `scripts/aos`:

```text
aos reindex
aos watch
aos watch --loop         # restart if the inner loop dies
aos sync
aos daily-close          # D = yesterday in the timezone, override by arg
aos validate             # type vs folder, unique slug, XOR until,
                         # valid cadence, status vs folder, links
aos up                   # calendar crontab + catch-up + watch if dead
aos up --quiet           # no stdout on success
aos up --watch-only      # watch only; no crontab or catch-up
```

`reindex` does not start a recurring series. It does not apply `until` (only `daily-close` and the last day's `x`).

---

## 11. Templates

Files in `docs/templates/`. Body matches sections 4.x + the listed headings. No engine.

`project.md` · `phase.md` · `task-unique.md` · `task-recurring.md` · `task-maintenance.md` · `research.md` · `daily.md` · `schedule-day.md` · `preferences.md`

---

## 12. Done when

1. Tree § 3; `user/` without real life; `preferences.md` empty/minimal is OK.
2. `docs/spec.md` = this law; `AGENTS.md`; templates; `docs/cron.md`; `README.md`.
3. The commands work (`reindex`, `watch`, `sync`, `daily-close`, `validate`, `up`).
4. Tests in `scripts/tests/` (not in `user/`): unique, daily, weekdays, interval, until date — empty sections omitted; Overdue includes a pending recurring past due; `x` on an ongoing line outside Today reverted; `x` unique moves + `completed_on` + commit; `x` ongoing Today fills `done_on` and leaves Today; first `x` on pending recurring starts it; `daily-close` until without x → completed + daily failure; past schedule gone; catch-up closes missed days with no credit and applies `[x]` on the return day; with `user/.git`, daily-close commits in the nested user git and the parent stays clean; recurring `due` null stays pending; maintenance lives in `ongoing/`; `done_on` drops the closed day; `times` is rejected.
5. `origin` on GitHub; public tree without real-life projects/tasks (`/user/` in gitignore).

---

## 13. Do not yield

- Reality > checklist.
- Phase = state + Goal (Tests if the Goal is not observable).
- A deadline is a calculation, not a folder.
- Unique: `x` moves the file. Live series: `x` in Today records the day. Pending recurring: `x` in any section starts the series.
- Cron: index + daily + past schedule; completes recurring only on a date `until`. It does not start a series.
- `aos up` installs the calendar crontab (`daily-close`), catch-up of missed days, and starts watch if it is dead. It does not start the `cron` daemon and does not reinstall every minute. Process persistence is the host.
- The AI does not replace the goal or the `x`.
