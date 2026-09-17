# Cron e watch

Fuso: `America/Sao_Paulo`.

Não há systemd nesta box. O crontab **vive no repo** (`docs/crontab`); `aos up` instala no usuário `box` e sobe o watch se estiver morto.

```cron
CRON_TZ=America/Sao_Paulo
MAILTO=""
PATH=/usr/bin:/bin
AOS_ROOT=/workspace/aos

* * * * * /workspace/aos/scripts/aos up --quiet >> /workspace/aos/logs/up.log 2>&1
0 0 * * * /workspace/aos/scripts/aos daily-close >> /workspace/aos/logs/daily-close.log 2>&1
@reboot /workspace/aos/scripts/aos up --quiet >> /workspace/aos/logs/up.log 2>&1
```

- A cada minuto: `aos up` (crontab idempotente + catch-up de dias não fechados + watch se o pid morreu).
- À meia-noite local: `aos daily-close`.
- `@reboot`: best-effort. Nesta box costuma não disparar; se disparar, é o mesmo `aos up`.
- Watch em `--loop` (reinicia se o inotify cair).

`aos up` no retorno (minuto, `@reboot` ou na mão):

1. Fotografa os `[x]` ainda no `tasks.md`.
2. Fecha cada dia sem daily, até ontem (sem daily nenhum: só ontem). Schedule ≤ D some. Esses dias não recebem crédito dos `[x]`.
3. Aplica os `[x]` fotografados como **hoje** (`completed_on` / `done_on` = o dia da volta).
4. Reindexa hoje e sobe o watch.

Sem daily nenhum no vault: fecha só ontem, não a história inteira.

Comando:

```text
/workspace/aos/scripts/aos up
```

Cold start da box: `/home/box/start.sh` vem do repo [n-huche/box-infra](https://github.com/n-huche/box-infra) (Tailscale + sshd). Sobe os watchdogs em `/home/box/infra/` e chama `aos up` quando reboot ou Update não reiniciaram os processos. Depois de Update: o disco `/workspace/aos` tende a ficar; `cron` e o spool podem sumir. O `aos up` do `start.sh` (ou o minuto do cron, se o daemon voltar) reconstrói crontab, fecha dias perdidos e sobe o watch.
