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

Status and evidence reflect **reality**, not volume of work. Task complete ≠ positive outcome. Phase complete = **condition** true, not a 100% checklist.

**Stack:** Markdown = source of truth · deterministic scripts · AI for planning · any editor as UI. The system **does not know Obsidian**. No required plugin.

**Human cadence:** the user may plan on Sunday and only execute later in the week. That is **their habit**, not a software rule. Planning can happen on any day. Preferences (no tasks on Sunday unless they ask, unavailable dates, language) live in `user/preferences.md`.

---

## 2. Model

```text
GOAL        abstraction to make real
  → PROJECT when it must split
    → PHASE lower abstraction (flat; depends_on)
      → CONDITION how I know it is real
        ↑ TASKS chosen concrete form
          → reality / evidence / review
```

```text
state reached → MAINTENANCE → recurring tasks → state preserved → repeat
```

A reached goal **does not** become maintenance by itself. If the user asks, a **new** maintenance is created; the historical project task does not change class.

### 2.1 Goal

No folder.

- Complex: **Goal** + **Condition** on the project hub. Only the user defines it and only the user changes it.
- Simple: on the independent task itself (`## Goal`).

A project-task does not repeat the why beyond `project:` / `phase:`.

### 2.2 Project

Folder 1:1 with status: `pending` · `ongoing` · `completed` · `canceled`.

There is no `paused`. Pause = `due: null` on the hub. The folder stays `pending` or `ongoing`.

**Completed** = the user declares the **goal** condition true. Completed phases are operational, not authority.

Project `due`: a date or `null`. No `projects.md`. Who changes project status is the user/AI, **never** cron. Move the whole `{slug}/` folder (hub, `phases/`, `notes.md`). Links *inside* the project do not change. Links *from outside* (`tasks.md` does not point at projects; a phase points at tasks — see § 6.3).

### 2.3 Phase

A lower abstraction that is still a state, not a bucket. Heuristic: if you removed the phase, would that state still be worth having? After a split, keep the higher phase only if its condition is not merely the AND of `depends_on`. If it is only that AND, it is a ghost level: delete it; the hub goal aggregates.

Complete ⇔ condition true, **even with pending tasks**. Leftover: the user names the task + a reason → the AI appends to `{project}/notes.md` and moves the file to `user/tasks/obsolete/`.

Tasks done + condition false ⇒ the phase is **not** complete.

Status: `pending` · `ongoing` · `completed` · `obsolete`.

Deps = a graph in frontmatter `depends_on` (slugs). No body section. Further descent = new phases on the same graph; the still-abstract phase depends on them. Parallel if there is no edge. The phase path only changes if the project folder changes.

No `## How` and no `## Deliverable` on the phase. Concretion is the task. Several possible forms → `user/research/`.

### 2.4 Condition

A `## Condition` block on the phase and on the hub. No mandatory metrics in v1. **Only the user** declares it true.

### 2.5 Task: class vs folder

`type`: `unique-independent` · `unique-project` · `recurring-independent` · `recurring-project` · `maintenance`

| Folder | Who |
|---|---|
| `pending/` | unfinished uniques, **loose** files |
| `recurring/` | recurring-* and maintenance, **loose**; class only in YAML |
| `completed/` | finished uniques; recurring whose cycle **ended** |
| `obsolete/` | was not needed |
| `canceled/` | aborted by the user |

No `ongoing` for uniques. No `maintenance/` subfolder and no due-date buckets on disk.

- Unique: `due` a date or `null`.
- `recurring-independent` / `recurring-project`: `until` **XOR** `until_event` required.
- `maintenance`: no end until the user says so.

Task slugs are **global**.

### 2.6 Research

Not a task. `user/research/{slug}.md`. The same abstraction often admits several concrete forms; research chooses which is adequate — including a still-vague how. On demand or during planning. Open = empty `## Decision`.

Order: Object → Question → Options → Decision → Implications.

### 2.7 Notes

`{project}/notes.md` — one file, created when there is something to record (outcome, obsolete task, observation). No `evidence/` folder.

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
      recurring/
      completed/
      obsolete/
      canceled/
    daily/
    research/
    schedule/
      YYYY/MM/DD.md         # unique: the due; recurring: the until; only if > today
```

Hub `user/projects/{status}/{slug}/{slug}.md`  
Phase `.../phases/{prefix}-{nn}-{name}.md`  
Unique `user/tasks/pending/{slug}.md`  
Recurring `user/tasks/recurring/{slug}.md`

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
project: my-project          # unique-project only
phase: mp-01-my-phase        # unique-project only; filename stem
---
```

Body: H1 = title (the label in the index). `## What` · `## How` · `## When` if due · `## Where` / `## With who` if they apply · independent: `## Goal`.

### 4.2 Recurring

```yaml
---
type: maintenance            # or recurring-independent | recurring-project
status: recurring
until: 2026-12-01            # XOR until_event; omit on maintenance
until_event: null
project: my-project          # if recurring-project
phase: mp-01-my-phase        # filename stem
done_on: []                  # completed occurrences, YYYY-MM-DD
cadence:
  kind: daily                # daily | weekdays | interval
  days: [wed, thu]           # weekdays only; mon tue wed thu fri sat sun
  every: 2                   # interval only
  unit: months               # days | weeks | months
  anchor: 2026-09-16         # interval only
---
```

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

Phase filename = `{prefix}-{nn}-{name}.md`, all lowercase. `nn` is a two-digit id assigned at creation (next unused number in that project). It does not change if `## Phases` is reordered. Example: prefix `F`, name Agency system → `f-01-agency-system.md`.

H1 = `{PREFIX}-{nn} {Name}` with `prefix` as written in YAML. Example: `# F-01 Agency system`.

Slug = filename stem. Same stem in `depends_on`, task `phase:`, and links. One identity.

Body: `## Goal` · `## Condition` · `## Phases` (links).

### 4.4 Phase

```yaml
---
status: pending
due: null
project: my-project
depends_on: [mp-01-other-phase]
---
```

Body: `## Condition` · `## Tasks`. How is the task's field. Deps are YAML only. No Deliverable.

In `## Tasks`, link by **slug** relative to `user/tasks/` **without** assuming a forever folder: when the script moves the task, it **rewrites** those links (`pending/x.md` → `completed/x.md` or `obsolete/x.md`).

### 4.5 Research

No status in YAML. Headings in the order of § 2.6. Optional frontmatter:

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

The title of each line = H1 of the task file.

### 5.1 Placement

Unique: `due` null → Undefined. `due < today` → Overdue. Else bucket of `delta = due - today`.

Recurring: at most two lines:

1. **Today** if the cadence falls today and today ∉ `done_on`
2. one bucket for the **next date > today** (a single window)

No Maintenance / Recurring sections. Overdue = **uniques only**.

### 5.2 Cadence

- `daily`: today if ∉ `done_on`; next = tomorrow.
- `weekdays`: next calendar dates whose weekday ∈ `days`, skipping `done_on`.
- `interval`: from `anchor`, step `every`/`unit` until dates ≥ today ∉ `done_on`.

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
| unique `due` null | `## Undefined` |

Rolling windows. No ISO week / civil month as a bucket.

Order: Overdue → Today → 1 day → 2-3 days → 4-7 days → 8-30 days → +30 days → Undefined.

Heading **only if** ≥1 item. Empty file allowed:

```markdown
# Tasks
```

Item:

```markdown
- [ ] [Title](pending/slug.md)
```

Relative to `user/tasks/`. Unique: 1 line. Recurring: up to 2, both `- [ ]`.

### 5.4 Examples

`weekdays: [wed, thu]`, today Wednesday → Today + 1 day. Today Thursday → Today + 4-7 days (next Wednesday = 6).

2-month interval, anchor today → Today + +30 days. Anchor yesterday → only +30 days.

`daily` → Today + 1 day if today ∉ `done_on`.

### 5.5 Schedule

`user/schedule/YYYY/MM/DD.md` only if `DD > today`. Body = links. Cron deletes dates ≤ the day it closed.

Unique: **the due only** (one file, the deadline day). Not a start date, not a range. Recurring: only `until` if it exists and is in the future — not every cadence occurrence.

`user/preferences.md`: prose; **scripts do not read it**.

Schedule vs task YAML conflict → **the task wins**.

---

## 6. Checkbox — `aos watch` / `aos sync`

Watch: inotify or poll ≤2 s on `user/tasks/tasks.md`.

### 6.1 How to read the section

Walk the file top to bottom. `## …` sets the current section. Each `- [x]` or `- [X]` inherits that section.

One pass, rules in this order:

1. An `[x]` line whose href is in `recurring/` **and** section **≠** `Today` → treat as **forbidden**: the line goes back to `[ ]`. Do not touch `done_on`.
2. An `[x]` `recurring/` line in section **Today** → § 6.2.
3. An `[x]` `pending/` line (any section) → § 6.3.

Then `reindex` (rebuilds the MD). If the only action was reverting rule 1, still write `tasks.md` unchecked.

### 6.2 Recurring on Today

1. Append today to `done_on` (no duplicates).
2. If `until == today`: `status: completed`, move `recurring/` → `completed/`, rewrite links in phases (§ 6.4).
3. Otherwise the file stays in `recurring/`.
4. Commit `aos: sync tasks`. Push if `origin` exists.

### 6.3 Unique (any section)

Early check is OK; **do not** change `due`.

1. `status: completed`, `completed_on: <today>`
2. Move `pending/` → `completed/`
3. Rewrite links § 6.4
4. Reindex, commit, push if origin

### 6.4 Rewrite links

Search the `user/` tree for strings `pending/{slug}.md`, `recurring/{slug}.md`, etc., and point them at the new folder. Includes the phase `## Tasks` and future `schedule/` files.

---

## 7. `aos daily-close` (00:00)

Timezone `America/Sao_Paulo`. D = the day that **ended**. The next reindex clock = D+1.

1. Unique still in `pending/` with `due==D` or `due<D` → failure on daily D.
2. Recurring whose cadence includes D, D ∉ `done_on`, `until != D` → failure; **not** Overdue; the series continues.
3. Recurring `until == D`:
   - D ∈ `done_on`: if still in `recurring/`, move to `completed/` (same as § 6.2.2). Daily: done.
   - D ∉ `done_on`: move to `completed/` anyway. Daily: **not done**.
4. Write `user/daily/D.md` (idempotent if the set is the same).
5. Delete `schedule` dates ≤ D. Non-date markdown under `schedule/` is left alone.
6. Reindex with today = D+1.
7. Commit `aos: daily-close D`. Push if origin.

Cron **does not** complete uniques. **Does not** move projects. Until **event** and ending maintenance: AI command only.

`daily-close` can also be run by hand. Document the crontab in `docs/cron.md`. Watch is a separate process: `aos up` starts it if it is dead; keeping it alive after that is the host, not AOS.

If the process was dead while the calendar moved, `aos up` does **catch-up** before starting watch:

1. Snapshot leftover `[x]` in `tasks.md` (close rewrites the index).
2. `daily-close` each day without a daily after the last one, through yesterday (no daily at all: yesterday only). Those days get no credit for the `[x]`. Schedule ≤ last D goes away.
3. Apply the snapshotted `[x]` with date = **today** (the day of return): unique `completed_on`, recurring `done_on` only if it was in Today.
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

Omit failed if empty. Recurring completed that day (still in `recurring/`): link `../tasks/recurring/slug.md`. Recurring closed on `until`: `completed/`.

**Done on D:** unique with `completed_on == D`; recurring with D ∈ `done_on`.

**Failure on D:** unique `due==D` or `due<D` still pending; recurring with an occurrence on D and no `done_on` (including `until==D` without a check).

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
- No due: ask **at the end**, after writing.
- Unique with due: YAML + `schedule/` **only on the due** (if `due > today`). Do not ask for a start date.
- Start date only: ask for the due; if they will not give one, **suggest** and schedule on the due.
- Recurring on the schedule: only a future `until`, not every occurrence.
- Several concrete forms, or a vague how → `user/research/`, not a task.
- Do not declare a condition true.
- Useless task: they say so + a reason → `notes.md` + `obsolete/` + links.
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

`reindex` does not apply `until` (only `daily-close` and the last day's `x`).

---

## 11. Templates

Files in `docs/templates/`. Body matches sections 4.x + the listed headings. No engine.

`project.md` · `phase.md` · `task-unique.md` · `task-recurring.md` · `research.md` · `daily.md` · `schedule-day.md` · `preferences.md`

---

## 12. Done when

1. Tree § 3; `user/` without real life; `preferences.md` empty/minimal is OK.
2. `docs/spec.md` = this law; `AGENTS.md`; templates; `docs/cron.md`; `README.md`.
3. The commands work (`reindex`, `watch`, `sync`, `daily-close`, `validate`, `up`).
4. Tests in `scripts/tests/` (not in `user/`): unique, daily, weekdays, interval, until date — empty sections omitted; Overdue uniques only; `x` on a recurring 1 day line reverted; `x` unique moves + `completed_on` + commit; `x` recurring Today fills `done_on`; `daily-close` until without x → completed + daily failure; past schedule gone; catch-up closes missed days with no credit and applies `[x]` on the return day; with `user/.git`, daily-close commits in the nested user git and the parent stays clean.
5. `origin` on GitHub; public tree without real-life projects/tasks (`/user/` in gitignore).

---

## 13. Do not yield

- Reality > checklist.
- Phase = state + condition.
- A deadline is a calculation, not a folder.
- Unique: `x` moves the file. Recurring: `x` (Today only) records an occurrence.
- Cron: index + daily + past schedule; completes recurring only on a date `until`.
- `aos up` installs the calendar crontab (`daily-close`), catch-up of missed days, and starts watch if it is dead. It does not start the `cron` daemon and does not reinstall every minute. Process persistence is the host.
- The AI does not replace the goal or the `x`.
