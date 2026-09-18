---
type: unique-independent
status: pending
due: 2026-09-19
completed_on: null
---

# Separar vault privado da lei pública do AOS

## What

Hoje um git só: `n-huche/aos` é **privado** e mistura lei/scripts (`docs/`, `scripts/`) com vida (`user/`). A intenção é o contrário: **AOS público** (contrato, templates, código) e **vault privado** (projects, tasks, daily, schedule, research).

`user/*` no gitignore do repo público **não basta**. O `aos` precisa de `user/` no disco, na raiz que tem `scripts/`. E o `gitutil` (`commit_user`, `push_if_origin`) commit/push o git **pai**. Se `user/` estiver ignorado no pai, a vida não vai pro público **nem** pro privado — limbo.

Forma certa: **dois gits, um disco**.

```text
aos/              ← repo público
  user/           ← clone do repo privado (nested git)
    .git/
```

Não: submodule no público apontando pro privado (clone do AOS 404). Não: vault como `AOS_ROOT` (a raiz continua sendo a pasta com `scripts/`).

## How

1. Criar repo privado só do vault (espelho do `user/` atual). `origin` desse git é o privado.
2. No repo público: gitignore de `user/` (exceto o que for esqueleto vazio, se fizer sentido — pastas/`constraints.md` de exemplo, sem vida). README/spec: como clonar o vault pra dentro de `user/`.
3. Tirar conteúdo real de `user/` do histórico público **ou** aceitar um repo público novo sem esse histórico. Não deixar daily/task de verdade no clone aberto.
4. Mudar `gitutil`: `commit_user` e o push correspondente operam no git **dentro de `user/`**, não no pai. Pai só commita lei/scripts. `aos up` / `daily-close` / `watch`/`sync` que commitam hoje o pai têm que seguir o vault.
5. Disco desta box: `aos/` público + `user/` nested privado. `box-upkeep` não muda de papel; só o path do vault continua sendo `…/aos/user`.
6. Testes: commit de daily-close não suja o git público; `git -C user status` vê o commit. Clone do AOS público sem credencial do vault ainda roda scripts em fixture.
7. Não meter secret de Tailscale nem de GitHub no vault público. O privado também não é lugar de auth key — só Markdown da agência.

## When

Due 2026-09-19.

## Where

Repos: `aos` (público) e o vault privado novo. Código: `scripts/aos_lib/gitutil.py` e o que chama `commit_user` / `push_if_origin`. Disco: `/…/aos/user/.git`.

## Goal

Quem clona o AOS aberto vê lei e scripts, zero vida. A box continua com o vault em `user/`, e `aos daily-close` / reindex gravam e dão push **só** no privado.
