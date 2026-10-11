# YYYY-MM

## First Week (01/10 - 03/10)

| hour | 1 - thu | 2 - fri | 3 - sat |
| --- | --- | --- | --- |
| 00:00 | null | null | null |
| 07:00 | null | project name | null |

## Second Week (04/10 - 10/10)

| hour | 4 - sun | 5 - mon | 6 - tue | 7 - wed | 8 - thu | 9 - fri | 10 - sat |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 00:00 | null | null | null | null | null | null | null |

One table per week, Sunday through Saturday, clipped to the month. The heading is the week ordinal and that month's days, `DD/MM`. A new file uses `##`. One row per hour, `00:00` through `23:00`. An empty window is the literal `null`. Labels are lowercase. Scripts write this file. Closed days, and today's hours through the current hour, are not rewritten.
