---
type: recurring-independent  # or recurring-project
status: pending              # pending | ongoing | completed | obsolete | canceled
due: 2026-10-01              # deadline to start; YYYY-MM-DD or null
until: 2026-12-01            # XOR until_event
until_event: null
infinitive: Do the thing
# do_in: "09:00"             # XOR do_after; omit when due is null
# do_after: other-task
project: my-project          # recurring-project only
phase: mp-01-my-phase        # filename stem
done_on: []
cadence:
  kind: daily                # daily | weekdays | interval | month-weekday
  days: [wed, thu]
  every: 2
  unit: months
  anchor: 2026-09-16
  day: mon                   # month-weekday only
  n: 1                       # month-weekday only; 1–5, or a list such as [1, 3]
---

# The thing

## What

## How

## When
