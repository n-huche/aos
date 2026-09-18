# Cron and watch

Timezone: `America/Sao_Paulo`.

AOS does not babysit the host. It exposes commands; whatever runs the machine starts them and keeps the `cron` daemon alive.

The calendar crontab **lives in this repo** (`docs/crontab`). `aos up` installs it for the current user, filling in the real repo root (`AOS_ROOT` or the directory that contains `scripts/`).

```cron
CRON_TZ=America/Sao_Paulo
MAILTO=""
PATH=/usr/bin:/bin
AOS_ROOT={root}

0 0 * * * {root}/scripts/aos daily-close >> {root}/logs/daily-close.log 2>&1
```

- Midnight local: `aos daily-close`.
- No minute job. No `@reboot`. Those were host persistence.

`aos up` (on return from downtime, or by hand):

1. Installs the calendar crontab.
2. Snapshots leftover `[x]` in `tasks.md`.
3. Closes each day without a daily, up to yesterday (no daily at all: yesterday only). Those days do not get credit for the `[x]`.
4. Applies leftover `[x]` as **today**.
5. Reindexes today and starts `watch` if it is dead.

No daily under `user/`: close yesterday only, not the whole history.

Commands (from the repo root):

```text
scripts/aos up
scripts/aos up --watch-only
```

`--watch-only` is for whoever already ran catch-up and only needs the watch process alive.
