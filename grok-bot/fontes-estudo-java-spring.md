# Where to study — Java + Spring (1st job)

**Goal:** learn as fast as possible **with excellence** — YouTube-first, English OK.  
**Routine:** yours. This doc only says *where*.  
**Out of scope:** Kafka, K8s, microservices, React, Python/AI, certificates, giant roadmaps.

Source: Mentor de Estudos v2 (Sep 2026). Previous PT-BR-heavy map discarded.

---

## Principles

- **1 primary + at most 1 complementary** per topic.
- Hands on keyboard — practice > binge.
- Skip GUI, Kafka, K8s, microservices, React, Python/AI in any video.
- Prefer English when it’s the better source (you’re fluent).
- One accumulating mini-repo; each topic adds a slice.

---

## 1. Java basics

Variables, types, if/loops, methods, classes, List/ArrayList, exceptions.

| | |
|---|---|
| **Primary** | [Bro Code — Java Full Course for free](https://www.youtube.com/watch?v=xTtL8E4LzTQ) — use description timestamps |
| **Cover** | JDK/IDE, variables/types, if/switch, loops, methods, classes, arrays, **ArrayList**, **exceptions** |
| **Skip** | Swing/GUI, graphics, audio, multithreading, advanced generics, serialization, long game projects |
| **Complementary** | [Programming with Mosh — Java Full Course for Beginners](https://www.youtube.com/watch?v=eIrMbAQSU34) — shorter clean fundamentals; don’t re-binge Bro Code |

---

## 2. OOP

Encapsulation, inheritance, interface, equals/hashCode.

| | |
|---|---|
| **Primary** | [Coding with John — Tutorials playlist](https://www.youtube.com/playlist?list=PLkeaG1zpPTHhXOfy-mFbdqd1Zz4GnjcpC) — especially [equals vs ==](https://www.youtube.com/watch?v=AoUVdLWLFQw); implement equals/hashCode on a domain class |
| **Cover** | Encapsulation, inheritance, polymorphism, abstract vs interface, toString, equals/hashCode |
| **Skip** | Multithreading, deep generics, reflection, full GoF patterns |
| **Complementary** | [Baeldung — equals() and hashCode() contracts](https://www.baeldung.com/java-equals-hashcode-contracts) |

---

## 3. Git + GitHub

| | |
|---|---|
| **Primary** | [freeCodeCamp — Git & GitHub Crash Course for Beginners](https://www.youtube.com/watch?v=mAFoROnOfHs) |
| **Cover** | init/status/add/commit/log, branch, merge, remote, push/pull, PR, `.gitignore` |
| **Skip** | Advanced rebase, complex hooks, submodules, deep CI/CD |
| **Complementary** | [Pro Git](https://git-scm.com/book/en/v2) — Ch. 1–3 + Ch. 6 (GitHub) only |

---

## 4. SQL

CRUD, JOIN, PK/FK, basic indexes.

| | |
|---|---|
| **Primary** | [freeCodeCamp / Mike Dane — SQL Tutorial](https://www.youtube.com/watch?v=HXV3zeQKqGY) |
| **Cover** | Tables, PK/FK, INSERT/SELECT/UPDATE/DELETE, WHERE, INNER/LEFT JOIN, constraints, basic indexes |
| **Skip** | Triggers, long ER digressions, stored procedures, heavy analytics |
| **Complementary** | [Mode SQL Tutorial](https://mode.com/sql-tutorial) — SELECT/JOIN drills if needed |

---

## 5. HTTP + REST + JSON

| | |
|---|---|
| **Primary** | [Traversy Media — HTTP Crash Course](https://www.youtube.com/watch?v=iYM2zFP3Zn0) — Express is demo only; **ignore Node**, focus on the protocol |
| **Cover** | GET/POST/PUT/PATCH/DELETE, 2xx/4xx/5xx, Content-Type, JSON body, REST resources |
| **Skip** | Express/Node code, deep HTTPS, HTTP/2/3 internals |
| **Complementary** | [MDN — A typical HTTP session](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Session) |

---

## 6. Maven

| | |
|---|---|
| **Primary** | [Programming Techie — Maven Complete Tutorial with IntelliJ](https://www.youtube.com/watch?v=JhSBS2OpGdU) (~38 min) |
| **Cover** | `pom.xml` (GAV), dependencies, lifecycle compile/test/package, `src/main` & `src/test` |
| **Skip** | Multi-module, obscure plugins, remote release/deploy |
| **Complementary** | [Maven in 5 Minutes](https://maven.apache.org/guides/getting-started/maven-in-five-minutes.html) |

---

## 7. Spring Boot

Controllers, services, DI, application.yml.

| | |
|---|---|
| **Primary** | [Dan Vega / freeCodeCamp — Spring Boot 3](https://www.youtube.com/watch?v=31KTdfRH6nY) |
| **Cover** | Initializr, `@RestController`, service layer, DI/`@Service`, `application.yml`, JSON |
| **Skip** | Deep RestClient / later modules — stay on API + DI + config |
| **Complementary** | [Amigoscode — Spring Boot 3 (2 Hours)](https://www.youtube.com/watch?v=-mwpoE0x0JQ) — skip the DB part (topic 8) |

---

## 8. Spring Data JPA + PostgreSQL + Flyway

| | |
|---|---|
| **Primary** | [Amigoscode — Spring Boot Full Course 2025](https://www.youtube.com/watch?v=Cw0J6jYJtzw) — Boot + Postgres via Docker + JPA |
| **Cover** | `@Entity`, `JpaRepository`, CRUD; learn `ddl-auto` then **turn it off** |
| **Skip** | K8s/AWS/microservices at the end; never treat `ddl-auto=update` as real migrations |
| **Complementary** | [Devtiro — Flyway with Spring Boot](https://www.youtube.com/watch?v=IuKXPx3WLbg) — then: **Flyway ON + `ddl-auto=validate` or `none`** |

---

## 9. Validation + ControllerAdvice + DTO ≠ entity

| | |
|---|---|
| **Primary** | [Exception Handling & Request Validation | RestControllerAdvice](https://www.youtube.com/watch?v=UD1MzZJjSUQ) |
| **Cover** | `@NotBlank`/`@Email`/`@Size`, `@Valid`, DTO ≠ entity, global `@RestControllerAdvice` |
| **Skip** | MySQL-specific bits, complex custom validators, groups |
| **Complementary** | [reflectoring.io — Validation with Spring Boot](https://reflectoring.io/bean-validation-with-spring-boot/) |

---

## 10. Spring Security + JWT

| | |
|---|---|
| **Primary** | [Amigoscode — Spring Boot 3 + Security 6 JWT](https://www.youtube.com/watch?v=KxqlJblhzfI) |
| **Cover** | `SecurityFilterChain`, UserDetails, BCrypt, JWT, route authorization |
| **Skip** | OAuth2 social, full Authorization Server, multi-tenancy |
| **Complementary** | [Dan Vega — Spring Security JWT](https://www.youtube.com/watch?v=KYNR5js2cXE) — pick **one** path and go deep |

---

## 11. JUnit + Mockito

| | |
|---|---|
| **Primary** | [Amigoscode — Software Testing Tutorial](https://www.youtube.com/watch?v=Geq60OVyBPg) |
| **Cover** | `@Test`, assertions, `@Mock`/`@InjectMocks`, when/verify, service tests without DB |
| **Skip** | Diffblue, TDD dogma, Testcontainers (later), 100% coverage |
| **Complementary** | [Coding with John — Java Unit Testing with JUnit](https://www.youtube.com/watch?v=vZm0lHciFsQ) |

---

## 12. Docker Compose (app + Postgres)

| | |
|---|---|
| **Primary** | [TechWorld with Nana — Docker Tutorial](https://www.youtube.com/watch?v=3c-iBn73dDE) — jump to Compose; don’t need all 3h linear |
| **Cover** | Dockerfile for the API, Compose `app` + `postgres`, ports, env, volumes |
| **Skip** | AWS registry, K8s, Swarm |
| **Complementary** | [Docker Docs — Compose](https://docs.docker.com/compose/) |

---

## 13. OpenAPI / Swagger

| | |
|---|---|
| **Primary** | [springdoc.org](https://springdoc.org/) — better than random videos: `springdoc-openapi-starter-webmvc-ui`, `/swagger-ui.html`, `/v3/api-docs` |
| **Cover** | Boot 3 dependency, UI, `@Operation`/`@Tag`, open paths in Security |
| **Skip** | Springfox, codegen, multi-group, complex Maven plugin |
| **Complementary** | [Baeldung — OpenAPI 3.0 with Spring](https://www.baeldung.com/spring-rest-openapi-documentation) |

---

## Accumulating mini-project

One REST API (tasks/contacts): validated DTOs, JPA entities ≠ DTOs, PostgreSQL + Flyway, JWT, tests, Compose, springdoc — then graduate to **Project 1** (business-rule anchor) from the portfolio doc.
