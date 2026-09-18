---
type: unique-independent
status: pending
due: 2026-09-26
completed_on: null
---

# Trocar iCloud+ por Google Workspace Starter

## What

Sair do iCloud+ e passar a assinar **Google Workspace Business Starter** (1 utilizador). Motivo: e-mail no domínio próprio com API/IA e o resto do ecossistema Google (Admin, Drive, Calendar).

**Fotos:** ficam no iPhone + **iCloud gratuito** (galeria nativa). Não é Google Fotos. Fotos que importam também vão como **arquivo** para uma pasta no Drive — não a biblioteca inteira, não sync Fotos↔Drive (o Google não oferece isso).

Dois ou três domínios, catch-all em todos, uma caixa: domínio primário + os outros como **alias de utilizador** + Default routing para endereço não reconhecido.

Isto é o plano que o usuário trouxe. Não misturar com as tasks de 19/09 (Tailscale API e vault AOS).

## How

1. Abrir Workspace Starter, 1 licença, plano flexível ou anual. Conferir preço no checkout (tabela oficial ~R$ 41–49/mês Starter; 30 GB em pool Gmail+Drive+Fotos).
2. Verificar os 2 (depois 3) domínios no Admin. Alias de utilizador, não secundário, enquanto for só uma pessoa.
3. MX/SPF/DKIM/DMARC segundo o Google. Catch-all: Default routing → destinatário não reconhecido → a caixa única. Testar com um endereço inventado em cada domínio.
4. Migrar o que ainda estiver no iCloud Mail (IMAP/export) se houver histórico a guardar.
5. **Antes** de cancelar iCloud+: tirar os domínios custom do iCloud (Apple não pode continuar dona do MX). Confirmar que o mail novo recebe.
6. Cancelar iCloud+. iCloud grátis = 5 GB. Se iCloud Fotos estiver ligado e a biblioteca for maior, o iPhone vai queixar-se — ou otimizar/dispositivo, ou caber nos 5 GB (backup do telemóvel também come isso).
7. Drive: pasta tipo `Photos/` (ou o nome que quiser) só para as relevantes, ficheiro original. App Arquivos / Drive no iPhone. **Não** ligar backup da câmera no Google Fotos, senão come o Starter e deixa de ser “arquivo”.
8. Conta Google: 2FA, senha de app só se algum cliente IMAP antigo precisar; o caminho da IA é OAuth/Gmail API, não senha no git.
9. Gmail no iPhone no lugar do Mail iCloud para esses domínios.

## When

Due 2026-09-26.

## Where

Admin Google, DNS dos domínios, Apple ID (iCloud Mail / domínio / assinatura), iPhone (Mail, Fotos, Arquivos/Drive).

## Goal

E-mail dos domínios (com catch-all) vive no Workspace, agente consegue integrar por API. iCloud+ cancelado. Fotos do dia a dia no iPhone/iCloud grátis. As que importam também existem como ficheiro no Drive, sem duplicar a biblioteca no Google Fotos.
