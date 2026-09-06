# First Job Stack — análise

**Atualizado:** 2026-09-04  
**Objeto:** stack e caminho até o primeiro emprego em tecnologia (estágio/júnior backend, Brasil)  
**Fontes:** Radar de Vagas + Arquiteto de Portfólio + Mentor de Estudos (corpus ~70–80 vagas úteis; Java estágio/jr; Gupy/Programathor/GeekHunter/etc.)

## Pergunta

Qual stack e sequência maximizam a chance de entrar no mercado o mais rápido possível, sem fechar IA no médio prazo?

## Contexto

Prioridade absoluta: **entrar no mercado**. Volume de vagas BR e filtro de júnior pesam mais que velocidade de aprender ou ponte imediata para IA. Transversal em qualquer stack: SQL + Git + REST + 1 linguagem.

## Opções

| Critério | Node/TS | Python | Java (+ Spring) |
|---|---|---|---|
| Volume BR (ordem de grandeza) | Médio | Médio (muitas vagas “Python” = dados) | **Maior** (~2,5–6× vs Python conforme fonte; backend explícito ~3×) |
| Saturação de júnior | Alta (bootcamps) | Alta no genérico | **Média** (Spring filtra) |
| Barreira 1ª vaga | Média | Mais baixa | Mais alta (OO + Spring) |
| Ponte IA / robótica | Fraca | Melhor | Mais longa |

Python seria a escolha se a prioridade fosse velocidade de aprender ou IA agora.

## Achados

Gates quase universais em estágio/jr backend: soft skills, **SQL**, **Git**, **APIs REST**.  
Java jr: Spring Boot frequente; sobem JPA, testes, Docker, JWT.  
Certificados: **~0** como requisito em estágio/jr Java abertos.

## Decisão

**Java + Spring.** Prioridade = entrar no mercado (volume + filtro Spring).  
Python fica para quando o alvo for IA — não agora.

## Implicações

- Fontes: [estudo](../phases/fj-01-study.md) · método: [learning-method](../learning-method.md)
- Portfólio: [projetos](../phases/fj-02-projects.md) — candidatar estágio assim que o Projeto 1 estiver hireable, sem esperar o #2
- Estudo com o Nicolas (não com o Chefe de gabinete)

## Riscos

- Rampa Java/Spring mais longa que Python — compensada por volume + menos júnior no filtro
- Menos “backend Python” puro no caminho IA imediato — adiado de propósito
- Enterprise Java (bancos/consultorias) favorece a escolha; produto/startup Node fica mais longe no curto prazo

## Critério de sucesso

Repo Projeto 1 público, pinned, `docker compose up` ok, JWT + regra de negócio + testes + README → candidaturas de estágio rolando.
