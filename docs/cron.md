# Cron and watch

Timezone: `America/Sao_Paulo`.

AOS does not babysit the host. It exposes commands; the machine (or a supervisor such as `box-keep`) starts them and keeps the `cron` daemon alive.

The calendar crontab **lives in this repo** (`docs/crontab`). `aos up` installs it for the current user with a real `AOS_ROOT`.

```cron
CRON_TZ=America/Sao_Paulo
MAILTO=""
PATH=/usr/bin:/bin
AOS_ROOT=/workspace/aos

0 0 * * * /workspace/aos/scripts/aos daily-close >> /workspace/aos/logs/daily-close.log 2>&1
```

- Midnight local: `aos daily-close`.
- No minute job. No `@reboot`. Those were host persistence.

`aos up` (on return from downtime, or by hand):

1. Installs the calendar crontab.
2. Snapshots leftover `[x]` in `tasks.md`.
3. Closes each day without a daily, up to yesterday (no daily at all: yesterday only). Those days do not get credit for the `[x]`.
4. Applies leftover `[x]` as **today**.
5. Reindexes today and starts `watch` if it is dead.

No daily in the vault: close yesterday only, not the whole history.

Commands:

```text
/workspace/aos/scripts/aos up
/workspace/aos/scripts/aos up --watch-only
```

`--watch-only` is for a host supervisor that already ran catch-up and only needs the watch process alive.
