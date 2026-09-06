# Estudo — Java + Spring (1ª vaga)

**Objetivo:** aprender o mais rápido possível **com excelência** — YouTube primeiro; fontes em inglês ok (e preferíveis quando forem melhores).  
**Rotina:** você define. Este doc só diz *onde* (método: [learning-method](../learning-method.md) · análise: [fj-01-learning](../analysis/fj-01-learning.md)).  
**Fora do escopo neste ciclo:** Kafka, K8s, microsserviços, React, Python/IA, certificados, roadmaps gigantes.

Fonte: Mentor de Estudos v2 (set/2026). Fontes em inglês; texto deste arquivo em português.

---

## Princípios

- **1 principal + no máximo 1 complementar** por tópico.
- Mão no teclado — prática > binge.
- Pule GUI e itens fora de escopo em qualquer vídeo (lista no topo).
- Prefira inglês quando a fonte for melhor (você é fluente).
- Um mini-repo acumulativo; cada tópico acrescenta uma fatia. Escopo amplo: [análise](../analysis/fj-stack.md).

---

## 1. Java básico

- [ ]

Variáveis, tipos, if/loops, métodos, classes, List/ArrayList, exceções.

| | |
|---|---|
| **Principal** | [Bro Code — Java Full Course for free](https://www.youtube.com/watch?v=xTtL8E4LzTQ) — use os timestamps da descrição |
| **Cobrir** | JDK/IDE, variáveis/tipos, if/switch, loops, métodos, classes, arrays, **ArrayList**, **exceções** |
| **Pular** | Swing/GUI, graphics, áudio, multithreading, genéricos avançados, serialização, projetos longos de jogos |
| **Complementar** | [Programming with Mosh — Java Full Course for Beginners](https://www.youtube.com/watch?v=eIrMbAQSU34) — fundamentos mais curtos e limpos; não reassista o Bro Code inteiro |

---

## 2. OOP

- [ ]

Encapsulamento, herança, interface, equals/hashCode.

| | |
|---|---|
| **Principal** | [Coding with John — Tutorials playlist](https://www.youtube.com/playlist?list=PLkeaG1zpPTHhXOfy-mFbdqd1Zz4GnjcpC) — em especial [equals vs ==](https://www.youtube.com/watch?v=AoUVdLWLFQw); implemente equals/hashCode numa classe de domínio |
| **Cobrir** | Encapsulamento, herança, polimorfismo, abstract vs interface, toString, equals/hashCode |
| **Pular** | Multithreading, genéricos profundos, reflection, padrões GoF completos |
| **Complementar** | [Baeldung — equals() and hashCode() contracts](https://www.baeldung.com/java-equals-hashcode-contracts) |

---

## 3. Git + GitHub

- [ ]

| | |
|---|---|
| **Principal** | [freeCodeCamp — Git & GitHub Crash Course for Beginners](https://www.youtube.com/watch?v=mAFoROnOfHs) |
| **Cobrir** | init/status/add/commit/log, branch, merge, remote, push/pull, PR, `.gitignore` |
| **Pular** | Rebase avançado, hooks complexos, submodules, CI/CD profundo |
| **Complementar** | [Pro Git](https://git-scm.com/book/en/v2) — só Ch. 1–3 + Ch. 6 (GitHub) |

---

## 4. SQL

- [ ]

CRUD, JOIN, PK/FK, índices básicos.

| | |
|---|---|
| **Principal** | [freeCodeCamp / Mike Dane — SQL Tutorial](https://www.youtube.com/watch?v=HXV3zeQKqGY) |
| **Cobrir** | Tabelas, PK/FK, INSERT/SELECT/UPDATE/DELETE, WHERE, INNER/LEFT JOIN, constraints, índices básicos |
| **Pular** | Triggers, ER longos, stored procedures, analytics pesado |
| **Complementar** | [ThoughtSpot SQL Tutorial](https://www.thoughtspot.com/sql-tutorial) — drills de SELECT/JOIN se precisar |

---

## 5. HTTP + REST + JSON

- [ ]

| | |
|---|---|
| **Principal** | [Traversy Media — HTTP Crash Course](https://www.youtube.com/watch?v=iYM2zFP3Zn0) — Express é só demo; **ignore Node**, foque no protocolo |
| **Cobrir** | GET/POST/PUT/PATCH/DELETE, 2xx/4xx/5xx, Content-Type, body JSON, recursos REST |
| **Pular** | Código Express/Node, HTTPS profundo, internals HTTP/2/3 |
| **Complementar** | [MDN — A typical HTTP session](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Session) |

---

## 6. Maven

- [ ]

| | |
|---|---|
| **Principal** | [Programming Techie — Maven Complete Tutorial with IntelliJ](https://www.youtube.com/watch?v=JhSBS2OpGdU) (~38 min) |
| **Cobrir** | `pom.xml` (GAV), dependencies, lifecycle compile/test/package, `src/main` e `src/test` |
| **Pular** | Multi-module, plugins obscuros, release/deploy remoto |
| **Complementar** | [Maven in 5 Minutes](https://maven.apache.org/guides/getting-started/maven-in-five-minutes.html) |

---

## 7. Spring Boot

- [ ]

Controllers, services, DI, application.yml.

| | |
|---|---|
| **Principal** | [Dan Vega / freeCodeCamp — Spring Boot 3](https://www.youtube.com/watch?v=31KTdfRH6nY) |
| **Cobrir** | Initializr, `@RestController`, camada service, DI/`@Service`, `application.yml`, JSON |
| **Pular** | RestClient profundo / módulos laterais — fique em API + DI + config |
| **Complementar** | [Amigoscode — Spring Boot 3 (2 Hours)](https://www.youtube.com/watch?v=-mwpoE0x0JQ) — pule a parte de DB (tópico 8) |

---

## 8. Spring Data JPA + PostgreSQL + Flyway

- [ ]

|                  |                                                                                                                                          |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Principal**    | [Amigoscode — Spring Boot Full Course 2025](https://www.youtube.com/watch?v=Cw0J6jYJtzw) — Boot + Postgres via Docker + JPA              |
| **Cobrir**       | `@Entity`, `JpaRepository`, CRUD; aprenda `ddl-auto` e depois **desligue**                                                               |
| **Pular**        | K8s/AWS/microsserviços no fim; nunca trate `ddl-auto=update` como migração de verdade                                                    |
| **Complementar** | [Devtiro — Flyway with Spring Boot](https://www.youtube.com/watch?v=IuKXPx3WLbg) — depois: **Flyway ON + `ddl-auto=validate` ou `none`** |

---

## 9. Validation + ControllerAdvice + DTO ≠ entity

- [ ]

| | |
|---|---|
| **Principal** | [CodeSnippet — RestControllerAdvice / Exception Handling](https://www.youtube.com/watch?v=IdHHwZg3v58) |
| **Cobrir** | `@NotBlank`/`@Email`/`@Size`, `@Valid`, DTO ≠ entity, `@RestControllerAdvice` global |
| **Pular** | Detalhes específicos de MySQL, validadores custom complexos, groups |
| **Complementar** | [reflectoring.io — Validation with Spring Boot](https://reflectoring.io/bean-validation-with-spring-boot/) |

---

## 10. Spring Security + JWT

- [ ]

**Decisão:** caminho **A** — a API **emite** JWT (`JwtAuthenticationFilter` + **JJWT**). Caminho **B** fica **opcional depois** (não estudar agora).

| | |
|---|---|
| **Principal** | [Amigoscode — Spring Boot 3 + Security 6 JWT](https://www.youtube.com/watch?v=KxqlJblhzfI) |
| **Cobrir** | `SecurityFilterChain`, UserDetails, BCrypt, **emitir JWT**, filtro que valida o token, autorização de rotas |
| **Pular** | OAuth2 social, Authorization Server completo, multi-tenancy, caminho B (resource server / IdP externo) |
| **Complementar** | [Dan Vega — Spring Security JWT](https://www.youtube.com/watch?v=KYNR5js2cXE) — aprofunda o **mesmo** caminho A (filtro + JJWT); não misturar com B |

---

## 11. JUnit + Mockito

- [ ]

| | |
|---|---|
| **Principal** | [Amigoscode — Software Testing Tutorial](https://www.youtube.com/watch?v=Geq60OVyBPg) |
| **Cobrir** | `@Test`, assertions, `@Mock`/`@InjectMocks`, when/verify, testar service sem DB |
| **Pular** | Diffblue, dogma TDD, Testcontainers (depois), cobertura 100% |
| **Complementar** | [Coding with John — Java Unit Testing with JUnit](https://www.youtube.com/watch?v=vZm0lHciFsQ) |

---

## 12. Docker Compose (app + Postgres)

- [ ]

| | |
|---|---|
| **Principal** | [TechWorld with Nana — Docker Crash Course](https://www.youtube.com/watch?v=pg19Z8LL06w) — mais curto; Compose docs no complementar |
| **Cobrir** | Dockerfile da API, Compose `app` + `postgres`, ports, env, volumes |
| **Pular** | AWS registry, K8s, Swarm |
| **Complementar** | [Docker Docs — Compose](https://docs.docker.com/compose/) |

---

## 13. OpenAPI / Swagger

- [ ]

| | |
|---|---|
| **Principal** | [springdoc.org](https://springdoc.org/) — melhor que tutoriais aleatórios: `springdoc-openapi-starter-webmvc-ui`, `/swagger-ui.html`, `/v3/api-docs` |
| **Cobrir** | Dependência Boot 3, UI, `@Operation`/`@Tag`, liberar paths no Security |
| **Pular** | Springfox, codegen, multi-group, plugin Maven complexo |
| **Complementar** | [Baeldung — OpenAPI 3.0 with Spring](https://www.baeldung.com/spring-rest-openapi-documentation) |

---

## Mini-projeto acumulativo

- [ ]

Uma API REST (tarefas/contatos): DTOs validados, entities JPA ≠ DTOs, PostgreSQL + Flyway, JWT, testes, Compose, springdoc — depois sobe pro **Projeto 1** (API âncora com regra de negócio) do doc de projetos.
