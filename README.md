# Agency Operating System (AOS)

Markdown operating system. Decision first; execution is mechanical. Tasks, projects, a derived index, daily close, and a watcher on checkboxes. The law is [`docs/spec.md`](docs/spec.md). The AI contract is [`AGENTS.md`](AGENTS.md).

This repository is the public law and the scripts. It does not ship real life.

## Layout

```text
AGENTS.md
README.md
docs/spec.md
docs/cron.md
docs/crontab
docs/templates/
scripts/aos
scripts/aos_lib/
user/                 # not in this git — see below
```

`aos` finds the root via `AOS_ROOT` or the directory that contains `scripts/`. Timezone: `America/Sao_Paulo`.

`user/` is a nested git (not a submodule, not `AOS_ROOT`). This tree gitignores `/user/`. Clone your private user repository into `user/`, or mkdir the empty folders from the spec. Scripts still need `user/` on disk next to `scripts/`.

If `user/.git` exists, `aos` commits and pushes life there. Otherwise (tests) it stages `user/` on the parent.

## Commands

Python 3, stdlib only.

```text
scripts/aos reindex
scripts/aos watch
scripts/aos watch --loop
scripts/aos sync
scripts/aos daily-close          # optional YYYY-MM-DD
scripts/aos validate
scripts/aos up
scripts/aos up --quiet
scripts/aos up --watch-only
```

`aos up` installs the calendar crontab from `docs/crontab` (`daily-close` at midnight local), catch-up of missed days, and starts watch if it is dead. It does not start the `cron` daemon. Process persistence is the host.

## Tests

```text
cd scripts && python3 -m unittest tests.test_aos tests.test_cadence
```

## What this git does not store

Secrets, Tailscale state, SSH keys, and the nested `user/` tree. Parent `.gitignore` includes `/user/`, `logs/`, `.obsidian/`, `__pycache__/`, `.DS_Store`.
