---
type: maintenance
status: ongoing              # ongoing | canceled
infinitive: Do the thing
# do_in: "06:00"             # XOR do_after
# do_after: other-task
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
