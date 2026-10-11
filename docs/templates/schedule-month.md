# YYYY-MM

| hour | 1 - thu | 2 - fri | 3 - sat |
| --- | --- | --- | --- |
| 00:00 | null | null | null |
| 07:00 | null | Project name | null |

| hour | 4 - sun | 5 - mon | 6 - tue | 7 - wed | 8 - thu | 9 - fri | 10 - sat |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 00:00 | null | null | null | null | null | null | null |

One table per week, Sunday through Saturday, clipped to the month. One row per hour, `00:00` through `23:00`. An empty window is the literal `null`. Scripts write this file. Closed days are not rewritten.
