---
type: recurring-independent  # or recurring-project
status: pending              # pending | recurring | completed | obsolete | canceled
start: 2026-10-01            # YYYY-MM-DD or null
until: 2026-12-01            # XOR until_event
until_event: null
project: my-project          # recurring-project only
phase: mp-01-my-phase        # filename stem
done_on: []
cadence:
  kind: daily                # daily | weekdays | interval
  days: [wed, thu]
  every: 2
  unit: months
  anchor: 2026-09-16
---

# Title

## What

## How

## When
