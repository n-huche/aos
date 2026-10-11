---
type: recurring-independent  # or recurring-project
status: pending              # pending | ongoing | paused | completed | obsolete | canceled
do_on: 2026-10-01            # next occurrence; omit when paused
do_at: ["09:00"]             # one or more HH:MM; omit when there is no hour
until: 2026-12-01            # XOR until_event
until_event: null
infinitive: Do the thing
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
