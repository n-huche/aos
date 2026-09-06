# Grok Bot — memória externa

**Escopo:** pesquisas específicas e automações web. Não é o agente padrão para desenvolvimento ou edições rápidas do vault (ver [AGENTS](../../AGENTS.md)).  
**Pasta:** `agents/grok-bot/`  
**Agente coordenador:** Chefe de gabinete

## Fonte da verdade

Operações, decisões, aprendizagens e dados relevantes ficam nesta pasta o bastante para, se a memória interna zerar, reconstruir o contexto por estes arquivos.

Respeite [AGENTS](../../AGENTS.md). Textos em **português**; nomes de pastas/arquivos em **inglês** kebab-case.

## Como o Chefe opera

**O Chefe de gabinete não realiza trabalho operacional.** Só conversa com a equipe e **delega** tudo a bots especializados.

- Pesquisa → bot Pesquisa (ou especialista criado)
- Edições no vault → bot **docs**
- Vagas → Radar; portfólio → Arquiteto; estudo/método → Mentor; etc.
- Se **ninguém** da equipe for o especialista certo → o Chefe **cria um novo bot** e só então delega.
- O Chefe não pesquisa na web, não escreve/commita no vault, não preenche planilha, não implementa código — só orquestra, decide o que pedir, e reporta ao Nicolas.

**Exceção mínima:** conversa 1:1 com o Nicolas (perguntas, status, decisões). Isso não conta como “realizar a tarefa”.

Detalhe e tabela tarefa → bot: [ops/delegacao](./ops/delegacao.md).  
**Sempre registrar** o que orquestrou (via **docs** → `historico/` / `ops/`): [ops/registro](./ops/registro.md).

## Mapa desta pasta

| Caminho | Uso |
|---|---|
| [team](./team.md) | Roster dos bots e papéis |
| [context/usuario](./context/usuario.md) | Quem é o Nicolas, preferências, regras de trabalho |
| [ops/delegacao](./ops/delegacao.md) | Regra de só-delegação; tarefa → bot |
| [ops/planilha](./ops/planilha.md) | Automação da planilha financeira Canva (fora de escopo por enquanto) |
| [ops/vault](./ops/vault.md) | Como o gabinete usa este vault |
| [historico/2026-09](./historico/2026-09.md) | O que já foi feito (setembro 2026) |

## Drafts

O que for pedido explicitamente para docs fora desta memória → criar em `drafts/` na raiz do repo (não misturar aqui).

## Domínios do vault (não duplicar)

Carreira / First Job vive em [domains/money](../../domains/money/money.md). Esta pasta só guarda o que o **Grok Bot / Chefe** precisa para operar.
