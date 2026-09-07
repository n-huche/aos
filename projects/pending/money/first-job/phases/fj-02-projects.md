# FJ-02 — projetos (Backend Java + Spring, 1ª vaga)

**Objetivo:** maximizar chance de estágio/júnior backend o mais rápido possível.  
**Status:** não iniciado  
**Projeto:** [First Job](../first-job.md)  
**Stack alvo:** Java 21 · Spring Boot 3 · SQL · REST · Git  
**Regra:** um projeto por vez. Candidatar assim que o Projeto 1 estiver hireable — não esperar o 2.

Decisões de stack/mercado: [análise](../analysis/fj-stack.md). Fontes: [estudo](fj-01-study.md).

## Entrega

- Projeto 1 hireable (API âncora com regra de negócio) e candidatura a estágio — não esperar o Projeto 2.
- Projeto 2 (desafio estilo Itaú) e, se ainda precisar de sinal, Projeto 3 (diferencial).

## Como

Um projeto por vez; candidatar quando o Projeto 1 estiver hireable. Stack, escopo mínimo, o que não fazer e ordem do README: seções abaixo. Decisões de stack: [fj-stack](../analysis/fj-stack.md). Fontes: [estudo](fj-01-study.md).

## Tarefas

- [Escolher domínio da API âncora](../../../../../tasks/pending/projects/first-job/fj-02-projects/choose-anchor-api-domain.md)
- [Criar o repositório e o README esqueleto](../../../../../tasks/pending/projects/first-job/fj-02-projects/create-anchor-api-repo.md)

## Ordem de execução

1. **Projeto 1 — API âncora** (obrigatório)
2. → **Começar a candidatar estágio**
3. **Projeto 2 — Desafio estilo Itaú**
4. **Projeto 3 — Diferencial** (só se ainda precisar de sinal)

Fora do plano neste ciclo: roadmaps gigantes, certificados agora, Kafka/K8s/microsserviços no v1.

---

## Projeto 1 — API âncora com regra de negócio

### Por quê
Cobre o que as vagas pedem: Java, Spring Boot, REST, SQL, Git; e o que júnior quase exige: JPA, testes, Docker, JWT. Uma API com regra de negócio vale mais que vários CRUDs.

### Domínio

Escolher **um**:

| Opção | Regra de negócio que prova | Preferência |
|---|---|---|
| **A) Pedidos + estoque** | Não confirma pedido sem saldo; baixa estoque ao confirmar | Recomendada |
| **B) Reembolsos com aprovação** | Fluxo de status + role aprovador | Recomendada |
| **C) Oficina / agenda** | Não agenda horário já ocupado | Ok |

Evitar: CRUD de livros, todo list, produtos sem regra.

### Stack exata
- Java 21 · Spring Boot 3 (Web, Validation, Data JPA, Security)
- PostgreSQL · Flyway · Spring Security + JWT (roles)
- JUnit 5 + Mockito · Docker Compose (app + Postgres)
- springdoc-openapi · Maven

### Escopo mínimo hireable
- ≥ 2 fluxos de negócio (não só CRUD)
- ≥ 1 relacionamento JPA real + migrations Flyway
- DTO ≠ entity · Bean Validation · `@ControllerAdvice` · status HTTP corretos
- JWT: login/cadastro, endpoints protegidos, roles, 401 vs 403 (segredo fora do código)
- Testes unitários mínimos nos services + `./mvnw test` documentado
- `docker compose up` sobe limpo · `.env.example`
- OpenAPI (Swagger UI) + README completo

### Não fazer no Projeto 1
Kafka, Kubernetes, microsserviços, Eureka, CQRS, GraphQL, Clean Architecture teatral, front completo, só H2 sem Postgres no Compose, um único commit `final`, secrets no repo.

### Pronto para candidatar quando
- [ ] `docker compose up` sobe
- [ ] Fluxos de negócio + JWT funcionam
- [ ] Testes passam
- [ ] README legível em ~30–60s
- [ ] Repo público e pinned
- [ ] Explica em 2 min: problema → stack → 1 decisão → 1 bug → próximo passo

**Aí candidata estágio.** Não espera o Projeto 2.

### Estimativa de referência
~8 semanas a 10–15 h/semana (orientação; o critério é “hireable”, não o calendário).

---

## Projeto 2 — Desafio estilo Itaú (transações + estatística)

### Por quê
Treina take-home de banco/fintech: API enxuta, validação, status HTTP, commits por feature. Combustível de entrevista — não pré-requisito para aplicar.

### Stack
Java 21 · Spring Boot 3 · Web · Validation · JUnit · em memória ou H2 (sem Postgres obrigatório).

### Escopo mínimo
- `POST` / `DELETE` de transação · `GET` estatística (janela de tempo)
- Validação + status HTTP · testes · README + `curl` · commits por feature

### Não fazer
Microsserviço; Kafka “pra parecer sênior”.

### Pronto quando
Sobe local, testes verdes, README com `curl`, histórico claro.

---

## Projeto 3 — Diferencial (opcional)

Só depois de candidatar com #1 (e idealmente #2). Escolher **um**:

| Opção | O quê | Por quê |
|---|---|---|
| **A** | Job CSV → validar → persistir → relatório de falhas | Parece trabalho júnior corporativo |
| **B** | Evoluir o #1: GitHub Actions + Testcontainers + 1 query SQL documentada | CI + SQL além do CRUD |
| **C** | N+1 de propósito + JOIN FETCH / `@EntityGraph` com README antes/depois | Consciência de performance JPA |

### Não fazer
Fila + Redis + cloud tudo junto; terceiro monólito CRUD paralelo.

---

## Checklist GitHub / README (olhada de 30s)

### Perfil
- Bio: `Backend Java/Spring · buscando estágio`
- README de perfil · Top Languages = Java · 1–2 repos pinned

### README do repo (nessa ordem)
1. Título + 2–3 linhas do problema
2. Demo: Swagger / `curl` / Postman
3. Funcionalidades (3–6 bullets)
4. Stack real com versões
5. Como rodar: clone → `.env.example` → `docker compose up` → `./mvnw spring-boot:run`
6. Endpoints (método, path, auth?, status)
7. Arquitetura em 1 parágrafo (Controller → Service → Repository)
8. Como testar
9. 2–5 decisões técnicas honestas
10. Limitações + próximos passos

### Mata em 30s
README só com lista de libs · um commit `final` · sem como rodar · só H2 sem Postgres no Compose (Projeto 1).

---

## O que não fazer (global)

- 10 repos abandonados · wall de badges · listar Kafka/K8s sem código
- Parecer pleno sem base · Python/IA antes de 1–2 repos Java vivos
- Fragmentar foco em 3 projetos ao mesmo tempo · certificados antes do Projeto 1 hireable

---

## Próximo passo concreto

1. Escolher domínio do Projeto 1 (**A** ou **B** — ainda pendente).
2. Criar o repositório e o README esqueleto.
3. Entregar o escopo mínimo hireable.
4. Pinar e candidatar.
