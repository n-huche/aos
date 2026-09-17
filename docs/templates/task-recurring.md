---
type: maintenance            # or recurring-independent | recurring-project
status: recurring
until: 2026-12-01            # XOR until_event; omit on maintenance
until_event: null
project: my-project          # if recurring-project
phase: my-phase
done_on: []                  # completed occurrences, YYYY-MM-DD
cadence:
  kind: daily                # daily | weekdays | interval
  days: [wed, thu]           # weekdays only; mon tue wed thu fri sat sun
  every: 2                   # interval only
  unit: months               # days | weeks | months
  anchor: 2026-09-16         # interval only
---

# Title

## What

## How

## When
