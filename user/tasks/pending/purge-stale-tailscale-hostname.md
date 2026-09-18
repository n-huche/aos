---
type: unique-independent
status: pending
due: 2026-09-19
completed_on: null
---

# Apagar nó Tailscale velho via API antes de subir um novo

## What

No reset da box, se `/var/lib/tailscale/tailscaled.state` sumir, o próximo `tailscale up` cria um **nó novo**. O nó antigo **não some sozinho**: fica na tailnet, offline, no admin do Tailscale.

Se o hostname for o mesmo (ex. um nome estável tipo `cursor-box`), o MagicDNS pode apontar pro morto. O IP também muda. SSH pelo nome quebra mesmo com auth key funcionando.

Hoje o `box-access` **recusa** criar identidade nova: só adota o state que já existe. `TS_AUTHKEY` ainda não está no bootstrap (isso é outro pedaço: a chave de *entrar* na tailnet). Esta task é o pedaço seguinte: **antes** de um `up` que nasceria um nó novo, chamar a API do Tailscale e apagar o aparelho velho com o mesmo hostname.

Não meter auth key nem API key no git. As duas vivem fora do repo (env / gestor de senha).

## How

1. No admin Tailscale, criar uma **API key** (não é a auth key de nó). Escopo o mais estreito possível pra listar/apagar devices. Guardar fora do git.
2. Combinar um **hostname estável** pra box e usar sempre esse no `tailscale up --hostname …`.
3. No `box-access` (bootstrap / `up` de recuperação), quando for o caso de criar identidade nova (`TS_AUTHKEY` presente e state ausente):
   - listar devices na tailnet;
   - achar o hostname da box;
   - apagar esse device (o offline);
   - só então `tailscale up --authkey … --hostname …`.
4. Se a API key não estiver no ambiente, falhar claro: não subir nó duplicado no silêncio.
5. Idempotente: se não houver device com aquele hostname, segue o `up`.
6. Não tocar no AOS nem no `box-upkeep`. Identidade de rede é só o portão.

A auth key (`TS_AUTHKEY`) pode ainda não existir no código; esta task assume que o fluxo de nó novo vai existir e **encaixa a limpeza antes do up**. Se o `TS_AUTHKEY` ainda não estiver no bootstrap, fazer os dois no mesmo fluxo de recuperação, sem misturar os secrets.

## When

Due 2026-09-19.

## Where

Código: repo `box-access` (bootstrap). Secret: fora do git. Conferência: admin da tailnet e `ssh -p 2222` pelo hostname depois de um wipe simulado ou real.

## Goal

Depois de um reset que apaga o state, um bootstrap com os secrets certos deixa **um** nó na tailnet com o hostname da box, e o SSH pelo nome funciona sem ir no admin apagar o cadáver na mão.
