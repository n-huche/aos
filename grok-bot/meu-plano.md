# Meu plano

Atualizado: 2026-09-04  
Base: Radar de Vagas + Arquiteto de Portfólio + Mentor de Estudos (corpus ~70–80 vagas úteis; Java estágio/jr; Gupy/Programathor/GeekHunter/etc.)

## 1. Stack (foco único)

**Java + Spring** para estágio / júnior backend.

| Critério | Node/TS | Python | Java (+ Spring) |
|---|---|---|---|
| Volume BR (ordem de grandeza) | Médio | Médio (muitas vagas “Python” = dados) | **Maior** (~2,5–6× vs Python conforme fonte; backend explícito ~3×) |
| Saturação de júnior | Alta (bootcamps) | Alta no genérico | **Média** (Spring filtra) |
| Barreira 1ª vaga | Média | Mais baixa | Mais alta (OO + Spring) |
| Ponte IA / robótica | Fraca | Melhor | Mais longa |
| Decisão | — | Boa se priorizar velocidade de aprender | **Escolhida** — prioridade = entrar no mercado |

**Transversal (todas as stacks):** SQL + Git + REST + 1 linguagem.

**Depois:** migrar/adicionar Python quando for para IA.

## 2. O que o mercado pede (entrada)

Gates quase universais estágio/jr backend: soft skills, **SQL**, **Git**, **APIs REST**.  
Java jr: Spring Boot frequente; sobem JPA, testes, Docker, JWT.

Certificados: **~0** como requisito em estágio/jr Java abertos. Pular cert agora.

## 3. Portfólio (sequencial)

1. **Projeto 1 — API âncora** (Spring Boot 3, Java 21, JPA, Postgres, Flyway, JWT, JUnit, Docker Compose, OpenAPI) com **regra de negócio** (pedidos/estoque ou reembolso).  
   → Assim que hireable: **candidatar estágio** (não esperar o #2).
2. **Projeto 2 — Desafio estilo Itaú** (transações + estatística).
3. **Projeto 3 — diferencial** só se ainda precisar (CSV job / CI+Testcontainers / N+1 documentado).

Detalhe: [[projetos-github-java-estagio]]

## 4. Estudo

Ordem: Java básico → OOP → Git → SQL → HTTP/REST → Maven → Spring Boot → JPA+Postgres+Flyway → Validation/DTO → Security+JWT → JUnit → Docker Compose → OpenAPI.

Fontes: YouTube-first, EN. Texto das notas em PT.  
Detalhe: [[fontes-estudo-java-spring]]

Rotina: **com o Nicolas** (não com o Chefe de gabinete).

## 5. Time de bots

| Bot | Papel |
|---|---|
| Radar de Vagas | Vagas e requisitos |
| Arquiteto de Portfólio | Projetos GitHub |
| Mentor de Estudos | Fontes |
| docs | Vault `n-huche/docs` → pasta `grok-bot/` |

Chefe de gabinete: análises / automações sob demanda.

## 6. Riscos aceitos

- Rampa Java/Spring mais longa que Python — compensada por volume + menos júnior no filtro.
- Menos “backend Python” puro no caminho IA imediato — adiado de propósito.
- Enterprise Java (bancos/consultorias) favorece a escolha; produto/startup Node fica mais longe no curto prazo.

## 7. Critério de sucesso (próximo marco)

Repo Projeto 1 público, pinned, `docker compose up` ok, JWT + regra de negócio + testes + README → candidaturas de estágio rolando.
