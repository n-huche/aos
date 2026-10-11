# Agency Operating System (AOS)

**What this file is:** the full law. An IDE session implements AOS **from this document only**, creating the repo from scratch. Do not migrate another user tree, repo, or draft.

**Name:** Agency Operating System · **abbrev:** AOS  
**Root:** any directory; `aos` finds it via `AOS_ROOT` or the folder that contains `scripts/`.  
**Timezone:** `America/Sao_Paulo` (Rio de Janeiro)  
**Language:** this repository (law, scripts, templates, tests) is English. Folder names, file names, frontmatter keys, and section headings (`##`) are English, kebab-case, ASCII. Prose inside the nested `user/` tree follows `user/preferences.md`. If that file does not set a language, use the language of the current conversation.

**v1 does not include:** streaks, progress bars, Dataview, a web app, a `goals/` folder, or real life content (zero real projects/tasks in this public tree).

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

Folder 1:1 with status: `pending` · `ongoing` · `paused` · `completed` · `canceled`.

Status is derived from the project's tasks, except two sticky cases the user sets by hand:

- `canceled` stays canceled (manual cancel).
- `completed` stays completed (the user has declared the Goal, or its Tests, true). It is not demoted.

Otherwise, from the tasks that name this project (`canceled` and `obsolete` tasks do not count):

| tasks | project |
|---|---|
| none, or every task canceled or obsolete | `canceled` |
| any `ongoing` | `ongoing` |
| every live task `paused` | `paused` |
| `pending` and `paused`, none `completed` | `pending` |
| every live task `pending` | `pending` |
| `pending` and at least one `completed` | `ongoing` |
| `paused` and `completed`, none `pending` | `ongoing` |
| no `pending` and no `paused` | `completed` |

`aos reindex` applies this and moves the whole `{slug}/` folder. `daily-close` applies the same rule first, so a date edit shows up without a checkbox pass. Links *inside* the project do not change. Links from outside that contain `projects/{status}/{slug}` are rewritten. No `projects.md`.

An old hub may still carry `do_on`. That value is history. It is not a deadline. New hubs omit the key. The key `due` is not a field.

### 2.3 Phase

A lower abstraction that is still a state, not a bucket. Heuristic: if you removed the phase, would that state still be worth having? After a split, keep the higher phase only if its Goal is not merely the AND of `depends_on`. If it is only that AND, it is a ghost level: delete it; the hub Goal aggregates.

Complete ⇔ the phase Goal is true (Tests if present), **even with pending tasks**. Leftover: the user names the task + a reason → the AI appends to `{project}/notes.md` and moves the file to `user/tasks/obsolete/`.

Tasks done + Goal false ⇒ the phase is **not** complete. Plan done ≠ complete.

Status: `pending` · `ongoing` · `paused` · `completed` · `obsolete`.

A phase uses the same task table as the hub, scoped to tasks whose `phase` is that file. The outcome `canceled` is written `obsolete` (a phase has no canceled status). `completed` and `obsolete` stay as the user left them. An old phase may still carry `do_on` as history, not as a deadline. New phases omit it. The key `due` is not a field.

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
| `pending/` | uniques and recurring-* that have a `do_on` and have not started |
| `ongoing/` | live recurring-* and live maintenance |
| `paused/` | unique or recurring with no `do_on`; maintenance the user paused |
| `completed/` | finished uniques; recurring whose cycle **ended** |
| `obsolete/` | unique or recurring that was not needed |
| `canceled/` | aborted by the user, including a maintenance the user stopped |

No `ongoing` status for uniques. No `completed` or `obsolete` for maintenance. No date buckets on disk. There is no `times` field. `do_at` is a list of clocks on the one task, not a second file.

- Unique: `do_on` a date, or absent. Status: `pending` · `paused` · `completed` · `obsolete` · `canceled`. With `do_on` the file is `pending`. Without `do_on` it is `paused`. Pausing a dated unique is removing `do_on`.
- Recurring: `do_on` is the day of the **next** occurrence, including the first one. `until` **XOR** `until_event`. Status: `pending` · `ongoing` · `paused` · `completed` · `obsolete` · `canceled`.
- Not started and no `do_on` → `paused/`. It is not in the index and it does not fail. The user writes a new `do_on` to make it `pending` again.
- The first `[x]` starts the series, in any section: `status: ongoing`, move to `ongoing/`, record today in `done_on`, and advance `do_on` to the next cadence day **after the scheduled `do_on`** (not after today).
- After it is `ongoing`, `do_on` stays the next occurrence. It moves only on `[x]`, from that scheduled day. A missed day does not move it. The task stays overdue and the daily fails each day until the check. `cadence.anchor` is not rewritten.
- If the next cadence day would pass `until`, the series completes instead of advancing. `until_event` is not a date. Close does not invent the end.
- An ongoing series that still has no `do_on` (it was already live) keeps the cadence clock: at most today and the next cadence day. It does not pause for lack of a date.
- Passed `do_on` still open: **Overdue**. The daily fails each day it stays open. Checking the Overdue line is allowed and advances exactly one occurrence. The line comes back, still unchecked, while `do_on` is still before today, so the gap can be closed the same day. `done_on` records the check day, not the missed day.
- Doing it before `do_on` counts as done, writes no failure on `do_on`, and frees that window.
- `maintenance`: cadence; no `do_on`, no `until`. Status: `ongoing` · `paused` · `canceled`. It does not pause for lack of a date. Pause is explicit. It does not complete and does not become obsolete.

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
      paused/{slug}/...
      completed/{slug}/...
      canceled/{slug}/...
        phases/{prefix}-{nn}-{name}.md
        notes.md
    tasks/
      tasks.md
      pending/
      ongoing/
      paused/
      completed/
      obsolete/
      canceled/
    daily/
      YYYY/YYYY-MM/YYYY-MM-DD.md  # hour table; metrics when the day is closed
      YYYY/YYYY-MM/YYYY-MM.md     # month rollup of closed days
    research/
    schedule/
      YYYY/YYYY-MM.md       # hour rows; one table per Sun–Sat week; closed days frozen
    vocabulary.md           # hour labels the user maintains; scripts do not require it
```

Hub `user/projects/{status}/{slug}/{slug}.md`  
Phase `.../phases/{prefix}-{nn}-{name}.md`  
Unique `user/tasks/pending/{slug}.md`  
Unstarted recurring `user/tasks/pending/{slug}.md`  
Live recurring and live maintenance `user/tasks/ongoing/{slug}.md`

A folder may exist with only a note. Links `[text](relative)` — never wiki links.

Two gits, one disk. This law (`scripts/`, `docs/`) is the public repo; `origin` = `https://github.com/n-huche/aos.git`. Life (`user/`) is a **nested** git at `user/.git` — a private repo, not a submodule, not `AOS_ROOT`. The public clone gitignores `/user/` and does not ship real projects/tasks. On disk the root still needs `user/`: clone your private user repository into `user/`, or mkdir the empty tree from this § 3.

`commit_user` / `push_if_origin`: if `user/.git` exists, add/commit/push **there**. Otherwise (test fixtures) the parent runs `git add user`. Reindex (when it applied a check) and daily-close push if **that** git has an `origin` and commits `origin` does not have (a push that failed earlier goes out with the next one). Git never prompts (`GIT_TERMINAL_PROMPT=0`). A failed push is printed and does not fail reindex or daily-close; `aos watch` retries unpushed commits every 10 minutes. AOS git writes take `aos-git.lock` in that git dir, so watch and cron do not collide; while another process holds `index.lock`, add/commit wait and retry for about 10 seconds. Parent `.gitignore`: `.obsidian/`, `__pycache__/`, `.DS_Store`, `logs/`, `/user/`. Do not change `git config`.

---

## 4. Frontmatter

Canonical for scripts. YAML `null` and an omitted key are the same for optional fields.

### 4.1 Unique

```yaml
---
type: unique-independent     # or unique-project
status: pending              # pending | paused | completed | obsolete | canceled
do_on: 2026-09-18            # YYYY-MM-DD; omit when paused
do_at: ["09:00"]             # clocks; omit when there is no hour
completed_on: null           # filled on check; YYYY-MM-DD
infinitive: Do the thing     # index label; required
project: my-project          # unique-project only
phase: mp-01-my-phase        # unique-project only; filename stem
---
```

Body: H1 is the thing, not the act (`# Café da manhã`). The slug is that title in English (`breakfast`). `infinitive` is the index phrase (`Tomar café da manhã`). `## What` · `## How` · `## When` if `do_on` · `## Where` / `## With who` if they apply · independent: `## Goal`.

`do_at` is one or more `HH:MM` values (24h, `America/Sao_Paulo`), a YAML list or one comma-separated string. No duplicates. `do_in`, `do_after`, and `due` are not fields.

### 4.2 Recurring

```yaml
---
type: recurring-independent  # or recurring-project
status: pending              # pending | ongoing | paused | completed | obsolete | canceled
do_on: 2026-10-01            # next occurrence; omit when paused or when a live series has no date yet
do_at: ["09:00"]             # clocks; omit when there is no hour
until: 2026-12-01            # XOR until_event
until_event: null
infinitive: Do the thing
project: my-project          # recurring-project only
phase: mp-01-my-phase        # filename stem
done_on: []                  # at most the open day; a later date may remain across catch-up
cadence:
  kind: daily                # daily | weekdays | interval | month-weekday
  days: [wed, thu]           # weekdays only; mon tue wed thu fri sat sun
  every: 2                   # interval only
  unit: months               # days | weeks | months
  anchor: 2026-09-16         # interval only
  day: mon                   # month-weekday only
  n: 1                       # month-weekday only; 1–5, or a list such as [1, 3]
---
```

`status: pending` while unstarted and dated (folder `pending/`). `status: ongoing` while live (folder `ongoing/`). `status: paused` with no `do_on`.

`do_on` on a live series is the next occurrence. One `[x]` records today in `done_on` and moves `do_on` to the next cadence day after the scheduled one. There is no intra-day quota. Several clocks are one index line, at the first `do_at` in the order written, and one grid cell per clock for that same occurrence. `done_on` holds at most that open day. On daily-close of D, D is removed. A later date stays. The history of the day lives in `daily/`.

### 4.2.1 Maintenance

```yaml
---
type: maintenance
status: ongoing              # ongoing | paused | canceled
do_at: ["06:00"]             # clocks; omit when there is no hour
infinitive: Do the thing
done_on: []
cadence:
  kind: daily                # daily | weekdays | interval | month-weekday
  days: [wed, thu]
  every: 2
  unit: months
  anchor: 2026-09-16
  day: mon                   # month-weekday only
  n: 1                       # 1–5, or a list such as [1, 3]
---
```

No `do_on`, no `until`. Folder `ongoing/` while live, `paused/` when the user pauses it, `canceled/` when the user stops it. Same `done_on` rule as a dateless live series: the check counts in **Today**, and today leaves the index once it is in `done_on`.

`interval` + `months`: add calendar months; if the day does not exist in the target month, use the **last day** of that month (31 Jan + 1 month → 28/29 Feb).

### 4.3 Project hub

```yaml
---
status: pending              # pending | ongoing | paused | completed | canceled
prefix: MP
---
```

`do_on` on an old hub is history. Omit it on a new hub.

`prefix` = short label for the project. It enters the phase filename and the phase H1.

Phase filename = `{prefix}-{nn}-{name}.md`, all lowercase. `nn` is a two-digit id assigned at creation (next unused number in that project). It does not change if `## Phases` is reordered. Example: prefix `F`, name Box access → `f-01-box-access.md`.

H1 = `{PREFIX}-{nn} {Name}` with `prefix` as written in YAML. Example: `# F-01 Box access`.

Slug = filename stem. Same stem in `depends_on`, task `phase:`, and links. One identity.

Body: `## Goal` · `## Tests` (only if Goal is not observable) · `## Plan` (numbered list) · `## Phases` (links).

### 4.4 Phase

```yaml
---
status: pending              # pending | ongoing | paused | completed | obsolete
project: my-project
depends_on: [mp-01-other-phase]
---
```

`do_on` on an old phase is history. Omit it on a new phase.

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

Paused tasks are absent.

Unique and unstarted recurring: one line, on `do_on`. `do_on < today` → Overdue. Else the bucket of `delta = do_on - today`. No `do_on` → paused, not indexed.

Live recurring **with** `do_on`: one line, on that date, including when today is already in `done_on`. That is what lets an overdue series be checked again the same day.

Live recurring **without** `do_on`, and maintenance: at most two lines:

1. **Today** if the cadence falls today and today is not in `done_on`
2. one bucket for the **next cadence date > today**

No Maintenance / Recurring sections. Overdue is its own bucket. It is not merged into Today. Each open day is still a failure.

### 5.2 Cadence

- `daily`: today if not done; next = tomorrow.
- `weekdays`: next calendar dates whose weekday ∈ `days`, skipping a date already in `done_on`.
- `interval`: from `anchor`, step `every`/`unit` until dates ≥ today not in `done_on`. The first check does not change `anchor`.
- `month-weekday`: the `n`th `day` of each month (`n` is 1–5 or a list of those, `day` is `mon`…`sun`). `n: 1` and `day: mon` is the first Monday. `n: [1, 3]` is the first and the third. A month that has no such day is skipped.

### 5.3 Buckets

| condition | heading |
|---|---|
| `do_on < today`, or a cadence date before today | `## Overdue` |
| occurs today | `## Today` |
| delta == 1 | `## 1 day` |
| delta ∈ {2, 3} | `## 2-3 days` |
| delta ∈ {4, 5, 6, 7} | `## 4-7 days` |
| delta ∈ [8, 30] | `## 8-30 days` |
| delta ≥ 31 | `## +30 days` |
| no date (should already be paused) | `## Undefined` |

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

Relative to `user/tasks/`. One line per task per day, at the first `do_at` in the order written, not the earliest clock. Later clocks stay on the month grid and do not add a line. All `- [ ]`.

### 5.3.1 Order inside a bucket

The order is a suggestion. The checkbox does not depend on position.

In a bucket that spans more than one day, the occurrence day comes first. A `###` heading already used in that section is not opened again: later days append their lines under the first one.

Each dated day splits into four half-open blocks of six hours. A heading is written only when that block has a line:

| heading | clocks |
|---|---|
| `### Morning` | [06:00, 12:00) |
| `### Afternoon` | [12:00, 18:00) |
| `### Evening` | [18:00, 24:00) |
| `### Overnight` | [00:00, 06:00) |

`00:00` is Overnight. `06:00` is Morning. `12:00` is Afternoon. `18:00` is Evening. A broken clock sorts inside its block by the real minute (`07:30` is Morning, after `07:00`).

Inside one block, sort by clock, then:

1. maintenance
2. recurring independent
3. unique independent
4. recurring project
5. unique project

Tasks of the same project stay in `## Phases` order and then `## Tasks` order, across types. Those five bands apply between different projects and between tasks with no project. A project takes the band of its earliest type in that list. Inside a band, tasks without a project sort by `infinitive`. Between projects in the same band, sort by the project H1.

`###` does not change the bucket. Sync reads only a line that starts with `## `.

Tasks with no `do_at` go at the end of that day, under `### Sem horário`, in the same type order, and they stay off the month grid. Undefined has no `###` headings.

The phrase `Sem horário` is fixed, as are the four block names. Scripts do not read `preferences.md`. The user keeps hour labels in `user/vocabulary.md`. A diary word that is not on that list is still a real report. Validate does not fail it.

### 5.4 Examples

`weekdays: [wed, thu]`, today Wednesday → Today + 1 day. Today Thursday → Today + 4-7 days (next Wednesday = 6).

2-month interval, anchor today → Today + +30 days. Anchor yesterday → only +30 days.

`daily` → Today + 1 day if today is not in `done_on`.

### 5.5 Schedule

`user/schedule/YYYY/YYYY-MM.md` (October 2026 is `user/schedule/2026/2026-10.md`). One row per hour `00:00`–`23:00`. The days of the month are split into one table per week. A week runs Sunday through Saturday and is clipped to the month. October 2026 is five tables: `1 - thu` through `3 - sat`, `4 - sun` through `10 - sat`, `11 - sun` through `17 - sat`, `18 - sun` through `24 - sat`, and `25 - sun` through `31 - sat`. A month can have four, five, or six tables. Scripts write this file. The AI does not. There is no `routine-base.md` and no `routine.md`. There is no per-day file under `schedule/`.

A cell is a window. Empty is the literal `null`. A project task shows the project H1. Anything else shows `infinitive`. Several tasks in the same day and hour are comma-separated. A clock with minutes falls in the full hour (`07:30` → `07:00`). Every clock in `do_at` fills its hour. The index does not: one line, at the first clock in the list as written. A task with no `do_at` is off the grid. Paused, completed, canceled, and obsolete tasks are off the open grid. A date that used to live only on `schedule/YYYY/MM/DD.md` is kept on the task under `## When` by `aos migrate-layout` (§ 10). That command does not put the date on this grid and does not set `do_on`.

What lands on a day:

- unique: `do_on`, if it has a clock
- recurring with `do_on` and a clock, pending or ongoing: each cadence day from `do_on` through `until`. The index still shows a pending recurring only on `do_on`
- recurring with `do_on`, a clock, and no `until`: the same intersection, from `do_on` through the last day of the current month. A `do_on` in a later month opens only that month. The next month appears when `reindex` runs in a month that reaches it
- recurring with no `do_on`: does not open a month. An ongoing one fills its cadence days in months some other task already opened
- maintenance with a clock: each cadence day in the months the grid builds. Maintenance does not open a month

Months built: the month of a unique `do_on` that has a clock, and every month from a recurring `do_on` through `until` (or through the current month when `until` is absent). An existing month file stays and its open columns are rebuilt. Not every future year.

Closed days are frozen. A column whose date already has a closed daily is never rewritten. The first time a month file is created, every column is written once, including days already closed. After that, only open columns move. Completing a task frees its window on open days. Cron does not delete the file.

`user/preferences.md`: prose; **scripts do not read it**.

Schedule vs task YAML conflict → **the task wins**.

---

## 6. Checkbox — `aos watch` / `aos reindex`

Watch: inotify or poll ≤2 s on `user/tasks/tasks.md`. On a change, it runs `reindex`.

### 6.1 How to read the section

`reindex` reads `tasks.md` before it rewrites the file. Walk top to bottom. A line `## …` sets the current section. `###` does not. Each `- [x]` or `- [X]` inherits that section.

One pass, rules in this order. One line is one check. A repeated line for the same task is still one check.

1. An `[x]` whose href is `ongoing/` **maintenance**, or a live recurring that has **no** `do_on`, and the section **≠** `Today` → **forbidden**: the line goes back to `[ ]`. Do not touch `done_on`.
2. An `[x]` `ongoing/` maintenance or dateless live recurring in **Today** → § 6.2.
3. An `[x]` `ongoing/` recurring that **has** `do_on`, in any section → § 6.2. Overdue is allowed, and so is a later bucket (early). Each check advances one scheduled occurrence.
4. An `[x]` `pending/` line whose task `type` is recurring-* → start the series (§ 6.2), in any section.
5. An `[x]` `pending/` unique (any section) → § 6.3.

Then the rest of `reindex`: placement, the open schedule, today's open daily when a check was applied, and `tasks.md`. Commit `aos: reindex` and push if `origin` exists, including when the only action was reverting rule 1. A rebuild that found no `[x]` does not commit. `daily-close` rebuilds without reading `[x]`.

Inside `reindex`, after the checkbox pass, placement is reconciled: a unique or unstarted recurring with `do_on` is `pending`; without `do_on` it is `paused`. Maintenance and an already-`ongoing` recurring are not paused for lack of a date. Project and phase status are derived (§ 2.2, § 2.3). `daily-close` reconciles before it scores the day.

### 6.2 Series check

Maintenance, and a live recurring with no `do_on`, in **Today**:

1. Record today in `done_on` (drop earlier dates; keep a later date).
2. Recurring with `until == today`: `status: completed`, move `ongoing/` → `completed/`, rewrite links (§ 6.4).
3. Otherwise the file stays in `ongoing/`. Reindex drops the Today line.

Live recurring **with** `do_on` (Today, Overdue, or a later bucket):

1. Record today in `done_on`.
2. Next = the first cadence day **after** the scheduled `do_on`, ignoring `done_on`.
3. If that next day would pass `until`, or `do_on` is already the `until` day: `status: completed`, move to `completed/`.
4. Otherwise set `do_on` to that next day. The file stays `ongoing/`.
5. While the new `do_on` is still before today, reindex puts the line back in Overdue, unchecked.

First `[x]` on a `pending` recurring, any section:

1. Record today in `done_on` and advance `do_on` the same way.
2. If the series finished on `until`, move to `completed/`. Otherwise `status: ongoing`, move `pending/` → `ongoing/`.
3. Reindex. The check counts even when today is not a cadence day. The date that moves is the scheduled one.

### 6.3 Unique (any section)

Early check is OK; **do not** change `do_on`.

1. `status: completed`, `completed_on: <today>`
2. Move `pending/` → `completed/`
3. The next schedule rebuild drops it from open columns (§ 5.5). Closed columns stay.
4. Rewrite links § 6.4
5. The same `reindex` commits `aos: reindex` and pushes if origin.

### 6.4 Rewrite links

Search the `user/` tree for strings `pending/{slug}.md`, `ongoing/{slug}.md`, `paused/{slug}.md`, etc., and point them at the new folder. Includes the phase `## Tasks`. Not `schedule/`: the grid has names, not links, and open cells are rebuilt (§ 5.5).

---

## 7. `aos daily-close` (00:00)

Timezone `America/Sao_Paulo`. D = the day that **ended**. The next reindex clock = D+1.

1. Reconcile placement (§ 6.1), including project and phase status.
2. Unique still `pending` with `do_on==D` or `do_on<D` → failure on daily D. A unique already completed is not a failure on `do_on`.
3. Recurring still `pending` with `do_on==D` or `do_on<D` → failure. It stays `pending`.
4. Live recurring **with** `do_on`: failure when `do_on<=D` and D is not in `done_on`. If D is in `done_on`, that occurrence is done even when `do_on` has already moved on. A dateless live recurring, and maintenance, fail when the cadence includes D and D is not in `done_on`.
5. Paused tasks do not fail and are not planned.
6. Recurring `until == D` (the series is `ongoing`): move to `completed/`. Daily: done if D is in `done_on` or `do_on` is already after D; otherwise not done.
7. Rebuild the schedule while D is still open, so a completion frees that window. Then write the daily. D is frozen from then on.
8. Remove D from `done_on`. A later date stays.
9. Create D+1's daily if it is missing: the hour table only, every cell `null`, no metrics yet.
10. Update `user/daily/YYYY/YYYY-MM/YYYY-MM.md` from closed days only.
11. Reindex with today = D+1. This rebuild does not read `[x]`.
12. Commit `aos: daily-close D`. Push if origin.

Cron **does not** complete uniques. **Does not** start a recurring series. It does derive project and phase status, same as reindex. Until **event** and canceling maintenance: AI command only. The schedule is not deleted.

`daily-close` can also be run by hand. Document the crontab in `docs/cron.md`. Watch is a separate process: `aos up` starts it if it is dead; keeping it alive after that is the host, not AOS.

If the process was dead while the calendar moved, `aos up` does **catch-up** before starting watch:

1. Snapshot leftover `[x]` in `tasks.md` (close rewrites the index).
2. `daily-close` each day without a **closed** daily after the last one, through yesterday (no closed daily at all: yesterday only). A placeholder hour table is not closed. Those days get no credit for the `[x]`. Closed schedule columns stay.
3. Apply the snapshotted `[x]` with date = **today** (the day of return): unique `completed_on`; a live series records today; a pending recurring starts. An overdue recurring with `do_on` advances from the scheduled day, not from the missed one.
4. Reindex = today. The clock that counts is the AOS that is up.


---

## 8. Daily

`user/daily/YYYY/YYYY-MM/YYYY-MM-DD.md`

```markdown
# YYYY-MM-DD

| hour | did |
| --- | --- |
| 00:00 | null |
| 01:00 | null |

| routine | tasks |
| --- | --- |
| 75% | 60% |

## Completed tasks

- [Title](../../../tasks/completed/slug.md)

## Failed tasks

- [Title](../../../tasks/pending/slug.md)

## Notes, optional
```

The hour table is 24 rows, `00:00`–`23:00`. A cell the user did not fill is `null`. While the day is open, `reindex` may write `## Completed tasks` under that table when a check lands on the day. It keeps the `did` column and the notes. It does not write `routine` / `tasks`, so the day stays open. Close keeps the hour column and the notes, and writes the metrics and the same completed list. Omit failed if empty. Live series: link `../../../tasks/ongoing/slug.md`. Recurring closed on `until`: `completed/`.

**Done on D:** unique with `completed_on == D` (including one done early); live recurring or maintenance with D in `done_on`.

**Failure on D:** unique `do_on<=D` still pending; recurring still `pending` with `do_on<=D`; live recurring with `do_on<=D` and D not in `done_on`; dateless live recurring or maintenance whose cadence includes D and D is not in `done_on` (including `until==D` without the day). Paused tasks do not fail. An early unique is not a failure on `do_on`.

**routine** = hours where the report equals one comma-separated token of the plan cell, divided by hours where **both** the plan and the report are non-null. A `null` plan or a `null` report is not in the count and is not a deviation. A deviation is a planned hour whose report matches none of the tokens. The category is the report text. Each planned name in that cell counts toward "tasks most deviated".

**tasks** = tasks done that day / tasks planned that day. Planned: unique with `do_on==D` or still pending with `do_on<D`; recurring with `do_on==D`, or `do_on<D` still open, or checked on D; maintenance whose cadence includes D. Paused excluded. Denominator 0 → that percentage is `null` and the day is left out of the month average.

`user/daily/YYYY/YYYY-MM/YYYY-MM.md`, rewritten every close, averages **closed** days only: each day, each weekday, the month; hours with the most deviations; deviation counts by category; tasks most deviated. A day that is all `null` and a day at 100% average to 100%. A placeholder (the hour table, no metrics) is not a closed day and is not in the average. `tasks` with nothing planned is `null` and is left out of the average. `routine` on a day from before the hour report is `null`.

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
- No `do_on`: ask **at the end**, after writing. Recurring `do_on` (the first occurrence, and later the next one): same. If they will not give one, omit `do_on` — the file is `paused`, not indexed, and it does not fail. Do not ask for a clock either.
- When `do_on` is set, ask `do_at` (one or more `HH:MM`). If they still do not choose, omit it. The task sits under `Sem horário` and off the grid.
- Maintenance has no `do_on`. Ask `do_at` when creating it. If they still do not choose, omit it. It stays `ongoing`.
- Unique with `do_on`: the day is the YAML date. The month grid picks it up when it has a clock. Do not write a schedule file by hand. Complete → scripts drop it from open columns.
- Recurring on the grid: each cadence day from `do_on` through `until` (or through the current month when `until` is absent), at `do_at`. Pending and ongoing both project. Not a hand-written list. Maintenance fills those months and does not open one.
- The same action twice in one day is two clocks in `do_at` on one task, or two task files when they are actually two actions. There is no `times`. The index shows that task once, at the first clock in the list. The month grid keeps every clock.
- Several concrete forms, or a vague how → `user/research/`, not a task.
- Do not declare a Goal or Tests true.
- Useless task: they say so + a reason → `notes.md` + `obsolete/` + links.
- `{project}/notes.md` is atemporal (§ 2.8). Rewrite so current truth stands alone. Do not append a dated log.
- Until event / end maintenance / cancel: only on command. Cancel project = move `projects/{status}/{slug}/` → `projects/canceled/{slug}/`. A canceled or completed project stays that way. Other project and phase statuses follow their tasks.
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
aos daily-close          # D = yesterday in the timezone, override by arg
aos migrate               # optional today YYYY-MM-DD; --dry-run writes nothing
aos migrate-layout       # optional today YYYY-MM-DD; default America/Sao_Paulo
aos validate             # type vs folder, unique slug, XOR until,
                         # valid cadence, status vs folder, links, layout
aos up                   # calendar crontab + catch-up + watch if dead
aos up --quiet           # no stdout on success
aos up --watch-only      # watch only; no crontab or catch-up
```

`reindex` reads `[x]` before it rewrites `tasks.md` (§ 6). That pass can start a recurring series. It does not apply `until` on its own (only `daily-close`, and a check whose next day would pass `until`). It reconciles paused/pending and derived project status, rebuilds open schedule columns, and, when a check was applied, writes `## Completed tasks` on today's open daily. `daily-close` calls the rebuild with the check pass off.

`aos migrate` brings this vault onto `do_on`, `do_at`, `paused`, and the YYYY-MM paths. It is not an importer of another person's tree. Today is the argument, or the `America/Sao_Paulo` date when the argument is omitted. `--dry-run` prints the path diff and writes nothing. A second run does not change file bytes.

1. A pending unique or recurring task loses `due`, `do_on`, `do_in`, `do_after`, and `do_at`, becomes `paused`, and moves to `tasks/paused/`. Links that named `pending/{slug}.md` follow it, including links in `schedule/`.
2. Any other task renames `due` to `do_on` and keeps the value, including `null`. A `do_in` or `do_after` that is a clock (`HH:MM`) becomes `do_at`. A `do_after` that names another task is removed. Maintenance stays active.
3. Project and phase files rename `due` to `do_on` and keep the value as history. Status is derived from the tasks (§ 6). A completed or canceled project hub stays in that folder. Phases use the same derivation; the canceled outcome is `obsolete` on a phase.
4. Reindex and rebuild the month grid.
5. `aos migrate-layout` then runs.

`aos migrate-layout` rewrites this vault's schedule and daily paths. It is not an importer of another person's tree. Today is the argument, or the `America/Sao_Paulo` date when the argument is omitted. A second run does not change file bytes. `validate` reports a leftover old path. The command:

1. Moves `user/daily/YYYY/MM/DD.md` to `user/daily/YYYY/YYYY-MM/YYYY-MM-DD.md`. A file that already has the hour table moves unchanged. A legacy daily becomes that table with every hour `null`, `routine` `null`, and `tasks` counted from the completed and failed lists (both empty → `null`). `**Result:**` stays in the notes. An existing day file at the new path is not overwritten. If the new file is already the hour table and the old one is too, the old one is removed. If they disagree and the old one is legacy, both stay.
2. Renames `user/schedule/YYYY/MM.md` to `user/schedule/YYYY/YYYY-MM.md`. The grid is not rebuilt. If both files exist and differ, both stay.
3. For each `user/schedule/YYYY/MM/DD.md` whose every line is a link to an existing task, appends that ISO date under the task's `## When` when the body does not already name the day (`YYYY-MM-DD`, `D/M/YYYY`, or `DD/MM/YYYY`). It does not set `do_on` and it does not invent a clock: a paused task cannot carry `do_on`, and a task with no `do_at` stays off the grid. Then it deletes the day file and the empty month directory. A day file with any other line stays.
4. Rewrites links that still name an old path, including a relative link whose target is one of those files. A link to a schedule day file points at the month grid.
5. Creates today's daily when it is missing: the hour table only, no metrics.
6. Writes the month file for every month that has a closed daily, and for today's month. Days before the hour report keep `routine` `null`.

---

## 11. Templates

Files in `docs/templates/`. Body matches sections 4.x + the listed headings. No engine.

`project.md` · `phase.md` · `task-unique.md` · `task-recurring.md` · `task-maintenance.md` · `research.md` · `daily.md` · `schedule-month.md` · `vocabulary.md` · `preferences.md`

---

## 12. Done when

1. Tree § 3; `user/` without real life; `preferences.md` empty/minimal is OK.
2. `docs/spec.md` = this law; `AGENTS.md`; templates; `docs/cron.md`; `README.md`.
3. The commands work (`reindex`, `watch`, `daily-close`, `migrate`, `migrate-layout`, `validate`, `up`).
4. Tests in `scripts/tests/` (not in `user/`): unique buckets; a unique with no `do_on` is paused and off the index; daily, weekdays, interval, until date — empty sections omitted; Overdue holds a past unique and a live recurring whose `do_on` is past; `x` on a dateless ongoing line outside Today reverted; `x` on an overdue recurring advances one `do_on` and the line stays while the date is still past; `x` unique moves + `completed_on` + commit and does not change `do_on`; early complete frees the open window and is not a failure on `do_on`; `x` ongoing Today fills `done_on` and leaves Today when the series has no `do_on`; first `x` on pending recurring starts it and advances `do_on`; `daily-close` until without x → completed + the day in Failed tasks; closed schedule columns stay, open columns follow the clocks; catch-up closes missed days with no credit and applies `[x]` on the return day; with `user/.git`, daily-close commits in the nested user git and the parent stays clean; recurring with no `do_on` while still pending is paused and does not fail; maintenance lives in `ongoing/`; `done_on` drops the closed day; `times` and `do_in` are rejected; a project follows its tasks into `paused`; null hours stay out of the routine percentage; commit waits out a foreign `index.lock`; a commit left by a failed push goes out on the next push; a failed push does not fail daily-close.
5. `origin` on GitHub; public tree without real-life projects/tasks (`/user/` in gitignore).

---

## 13. Do not yield

- Reality > checklist.
- Phase = state + Goal (Tests if the Goal is not observable).
- A deadline is a calculation, not a folder.
- Unique: `x` moves the file. Maintenance and a dateless live series: `x` in Today records the day. A live recurring with `do_on`: `x` advances that date, including from Overdue. Pending recurring: `x` in any section starts the series.
- Cron: index + daily + frozen schedule; completes recurring only on a date `until`. It does not start a series. It does not delete the month grid.
- `aos up` installs the calendar crontab (`daily-close`), catch-up of missed days, and starts watch if it is dead. It does not start the `cron` daemon and does not reinstall every minute. Process persistence is the host.
- The AI does not replace the goal or the `x`.
