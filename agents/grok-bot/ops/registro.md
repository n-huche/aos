# Registro — memória do gabinete

**Atualizado:** 2026-09-06  
**Status:** em vigor

## Regra

O Chefe deve **sempre** registrar no próprio diretório (`agents/grok-bot/`) o que acabou de fazer/orquestrar (decisões, delegações, entregas). Isso reforça a memória interna e sobrevive a reset de contexto.

## Como registrar

Após cada entrega relevante ao Nicolas:

1. O Chefe manda o bot **docs** acrescentar nota em `historico/` (mês corrente).
2. Se for **regra nova** ou protocolo → atualizar / criar arquivo em `ops/` (e apontar em [grok-bot](../grok-bot.md) se entrar no mapa).
3. **Não pular o log** — mesmo quando a entrega já foi falada no chat.

## O que entra no log

- Decisões do Nicolas
- Delegações (quem fez o quê)
- Entregas / commits relevantes
- Criação ou aposentadoria de bots
- Correções de processo

## O que não substitui

- Domínios de vida (`domains/`) — não reescrever análise de carreira aqui; só apontar.
- Chat — resultado imediato fica no chat; o vault é a memória durável do gabinete.

Ver [ops/delegacao](./delegacao.md) · [historico/2026-09](../historico/2026-09.md).
