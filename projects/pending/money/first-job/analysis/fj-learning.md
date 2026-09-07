# First Job Aprendizagem (prontidão para FJ-02)

**Atualizado:** 2026-09-06  
**Objeto:** método e profundidade mínima nos tópicos do [FJ-01](../phases/fj-01-study.md) até abrir a [FJ-02](../phases/fj-02-projects.md)  
**Fontes:** mapa [fj-01-study](../phases/fj-01-study.md); stack [fj-stack](./fj-stack.md)

## Pergunta

Qual método leva **mais rápido** à prontidão para o Projeto 1 — sem domínio profundo?

## Contexto

- Meta: 1ª vaga backend Java+Spring ([fj-stack](./fj-stack.md)).
- FJ-01 é pré-requisito da FJ-02, não um curso completo.
- Fonte principal: vídeo YouTube (inglês ok); no máximo 1 texto complementar por tópico; prática no **mesmo** mini-repo.
- Gaps finos se resolvem fazendo o P1.

## Opções

| Critério | A — Binge + copiar tutorial | B — Dominar cada tópico | C — Vídeo como exemplo + fade + explicar sem olhar |
|---|---|---|---|
| Tempo até FJ-02 | Ruim (tutorial hell) | Ruim (overlearning) | **Melhor** |
| Serve no P1 | Fraco | Forte demais agora | Suficiente |
| Combina com YouTube → repo | Não | Parcial | **Sim** |

## Achados

- Assistir o vídeo inteiro e só depois codar treina reconhecimento, não recall.
- Pausar, prever o próximo passo, explicar sem o vídeo e commitar no próprio repo transfere melhor para o P1.
- Depois que o padrão existe (ex.: o 2º CRUD), reassistir o exemplo completo atrasa.

## Decisão

**C.** YouTube = exemplo trabalhado. Fade rápido para o mini-repo. Parar no gate — não maestria. Sessão só conta com explicar sem olhar + commit.

## Implicações

- Mapa: [fj-01-study](../phases/fj-01-study.md).
- Loop 25–50 min: meta em 1 frase → só o trecho do vídeo → pause + predict → fechar vídeo e explicar → fatia no mesmo repo → “consigo sem o vídeo?”.
- Fade: completo → lacuna → sozinho → próximo feature similar do zero (vídeo só se travar ~20–30 min).
- Sem 2º complementar, sem copiar o projeto do YouTube, sem binge sem commit.

## Riscos

- Fluência falsa do vídeo — mitiga: retrieval + commit obrigatório.
- Overlearning no FJ-01 — mitiga: gate e abrir FJ-02.

## Critério de sucesso

Abrir FJ-02 quando (buracos ok):

1. Mini-repo sobe com `./mvnw` + Postgres via Compose.
2. Sem vídeo: 1 resource REST + service + entity/DTO + 1 migration Flyway + JWT protegendo 1 rota + 1 teste de service.
3. Explica em ~2 min: `HTTP → filter JWT → @Valid → service → JPA → JSON`.
4. Não exige terminar os vídeos do mapa.
