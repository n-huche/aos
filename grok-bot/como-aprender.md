# Como aprender (rápido + retenção)

Guia operacional para o caminho Java + Spring até o primeiro estágio/júnior no Brasil. Complementa o mapa de fontes (o *o quê*); aqui está o *como*. Sem calendário semanal — você controla o ritmo. Prioridade absoluta: **prática deliberada no repositório acumulativo (API Tarefas/Contatos)** vence qualquer método que atrase o ship.

---

## Princípios (evidence-based)

Traduzidos para “assisti YouTube → codei no repo”.

- **Active recall / retrieval practice (Roediger & Karpicke; testing effect)** — Depois do vídeo, feche a aba e tente explicar ou reescrever o conceito *sem olhar*. Testar a memória fortalece mais do que reler. Na prática: “sem olhar o código do tutorial, escrevo o `Controller` do zero?”
- **Spaced repetition (Ebbinghaus; Anki-style para código)** — Revisar no dia 1, ~3 e ~7 (ajuste fino depois). Não é só flashcard de sintaxe: revise *refazendo um pedaço pequeno* do endpoint ou relendo sua nota Q→A.
- **Deliberate practice (Ericsson)** — Sessão com meta estreita, fora da zona de conforto, com feedback rápido (compila? testa? curl responde?). “Assistindo mais um vídeo” sem stretch goal não é prática deliberada.
- **Worked examples → faded guidance (Sweller; worked-example effect)** — Iniciante: *estude* o exemplo do vídeo passo a passo. Depois: pause e complete o próximo passo sozinho. Depois: implemente a fatia no P1 *sem* o vídeo. Guia some conforme a expertise sobe (expertise reversal: exemplo demais atrapalha quem já sabe).
- **Interleaving vs blocking** — *Block* ao aprender um conceito novo (só `List` hoje). *Interleave* depois: misture prompts similares que você confunde (ex.: `ArrayList` vs `LinkedList`, `@RequestBody` vs `@RequestParam`, entity vs DTO). Interleaving dói mais e retém melhor (Rohrer et al.; Bjork).
- **Generation effect** — Tente gerar a resposta/código *antes* de ver a solução. Errar com esforço > colar certo.
- **Dual coding (leve)** — Um diagrama minúsculo (fluxo request → filter → controller → service → JPA) + texto PT na nota. Sem obsessão com mind maps bonitos.
- **Desirable difficulties (Bjork)** — Se a sessão parece “fácil demais”, falta retrieval, spacing ou stretch. Dificuldade *desejável* acelera retenção; dificuldade *indesejável* (tutorial de Kafka no meio do P1) só atrasa o hireable.
- **Pedagogia prática de código**
  - **Read → Trace → Modify → Write**: leia o exemplo; trace com debugger/`println`; mude um detalhe; só então escreva do zero no repo.
  - **Rubber duck**: explique o bug/endpoint em voz alta (ou num comentário temporário).
  - **Feynman para endpoints**: explique `POST /tarefas` como se fosse para um colega júnior — se travar, você ainda não sabe.
  - **“Consigo construir sem o vídeo?”** — critério de ouro. Se não, volte ao fade (complete 1 passo faltando), não ao binge.

**Conflito de método:** se um ritual de estudo (Anki 1h, reassistir a playlist) compete com tempo de código no P1, **corte o ritual**. Ship do repo = prática deliberada com feedback de mercado.

---

## Anti-padrões

- **Binge sem código** — 3h de vídeo, 0 commits. Zero retenção hireable.
- **Highlight-only / anotar sem retrieval** — Sublinhado ≠ saber. Sem recall fechado, é ilusão de competência.
- **Reassistir passivo** — Segundo play no piloto automático. Prefira: pause + predizer + implementar.
- **Tutorial hell** — Copiar o projeto do instrutor e nunca portar para *seu* repo acumulativo.
- **Colecionar playlists** — “Salvei 40 cursos” ≠ progresso. 1 fonte principal + no máximo 1 complementar por tópico (já no mapa).
- **Estudar 4h sem retrieval** — Maratona sem teste. Quebre em blocos 25–50 min com recall no fim.
- **Projeto paralelo infinito** — Novo repo a cada tutorial. Mate: tudo converge no P1.
- **Perfeição antes de expor** — Polir teoria de Security Resource Server antes de JWT path A no P1. Escopo errado.
- **Fora do escopo como “só mais um vídeo”** — Kafka, K8s, microservices, React, Python/AI. Não.

---

## Protocolo de sessão (25–50 min)

### Antes (2–3 min)
1. **Meta em 1 frase** — Ex.: “Entender `@Valid` + `MethodArgumentNotValidException` e aplicar no `POST /contatos`.”
2. Abrir o **repo acumulativo** (não um scratch descartável).
3. Escolher o pedaço do vídeo alinhado à meta (pular GUI/out-of-scope).

### Durante (vídeo ativo)
1. **Pause + predict** — Antes de cada bloco importante: “O que o próximo método faz? Qual anotação entra?”
2. **Trace** — Se houver código: acompanhe o fluxo mentalmente (request → camada → resposta).
3. **Não pause 40 min para digitar tudo** — Anote só ganchos; o código real vem *depois*, closed-book no seu repo.
4. Se for tópico novo e denso: use o vídeo como **worked example** (estude a solução), não como ditado.

### Depois (obrigatório — ver seção seguinte)
Closed-book recall → fatia no P1 → nota/flashcards → agendar review.

**Regra:** se o timer acabou e você só assistiu, a sessão **não contou**. Estenda 15 min só para retrieval + 1 commit mínimo, ou marque como incompleta.

---

## Depois do vídeo (obrigatório)

Checklist (faça na ordem):

- [ ] **Explicar sem olhar** (Feynman / rubber duck, 2–5 min): o que mudou no sistema? Por que? Onde no P1 isso vive?
- [ ] **Implementar uma fatia minúscula no repo acumulativo** — 1 endpoint, 1 anotação, 1 migration, 1 teste. Commit com mensagem clara.
- [ ] **3–5 flashcards OU 1 nota PT com Q→A** (templates abaixo). Prefira perguntas que forçam *decisão* (“quando uso DTO vs entity?”), não só definição.
- [ ] **Agendar review espaçado (aproximado):** amanhã (1d) / +3d / +7d. Na review: *refaça* ou *responda Q→A*, não reassine o vídeo inteiro.
- [ ] **Teste ácido:** “Consigo construir isso sem o vídeo?” Se não → faded guidance amanhã (complete passos faltantes), não playlist nova.

---

## Como saber que "já sabe"

Não é “terminei o vídeo”. Critérios de saída por tipo de habilidade:

| Tipo | Você “já sabe” quando… |
|------|-------------------------|
| **Conceito de linguagem** | Explica em PT com exemplo próprio; escreve um snippet closed-book; identifica o erro comum em 30s. |
| **Ferramenta CLI/fluxo** | Executa o fluxo completo *sem tutorial* (init → commit → push; ou `mvn test`; ou `docker compose up` + health). Explica *por que* cada comando. |
| **Rede/dados** | Desenha o request/response ou o modelo SQL de cabeça; escreve a query/endpoint certo para um caso novo do P1. |
| **Framework hands-on** | Adiciona a feature no P1 sozinho; sabe onde configurar, o que quebra se errar, e como validar (curl/teste). |
| **Testes** | Escreve um teste que falha pelo motivo certo, depois passa; mocka a dependência certa; nomeia o teste pelo comportamento. |
| **Geral (hireable)** | Em entrevista improvisada: explica o endpoint do P1 ponta a ponta (HTTP → security → validation → service → JPA → JSON) sem ler o código. |

Sinal vermelho de “ainda não”: só reconhece a tela do vídeo; copia e torce para compilar; não consegue modificar o exemplo para o domínio Tarefas/Contatos.

---

## Protocolos por TIPO de tópico

Mapeamento dos 13 tópicos → tipos. Use a receita do tipo, não um método genérico.

### 1) Conceitos de linguagem — *Java basics, OOP*
**Como assistir:** Blocos curtos; pause + predizer o output; worked example nos primeiros loops/classes; fade rápido para exercícios seus.

**O que construir:** Classes/enums do domínio do P1 (ex.: `StatusTarefa`, `Contato`) — não “Hello World” eterno. Interleave depois: polimorfismo vs composição em decisões reais do modelo.

**Retrieval prompts:**
- “Diferença entre `==` e `.equals` com exemplo que quebra?”
- “Por que encapsular este campo no P1?”
- “Desenhe a hierarquia / composição do seu domínio em 1 min.”

**Falhas comuns:** Overlearn de sintaxe sem domínio; bloquear semanas em Java puro sem Git/HTTP; anotar a JDK inteira.

---

### 2) Ferramentas CLI/fluxo — *Git+GitHub, Maven, Docker Compose*
**Como assistir:** Mãos no terminal *durante* o vídeo (ativo), mas o “exame” é repetir o fluxo sozinho depois.

**O que construir:**
- Git: histórico limpo no P1 (branches curtas, PRs para você mesmo se quiser).
- Maven: entender `pom.xml` do P1; adicionar 1 dependência com propósito.
- Docker Compose: Postgres (+ app se já couber) subindo o ambiente do P1.

**Retrieval prompts:**
- “Sem Google: como desfaz o último commit *ainda não pushado*?”
- “O que `mvn test` vs `mvn package` faz no *meu* projeto?”
- “Quais serviços o `compose` sobe e como verifico saúde?”

**Falhas comuns:** Assistir Git como teoria; ter medo de errar o histórico (erre num branch); Docker como tour de flags em vez de “meu Postgres sobe”.

---

### 3) Conceitos de rede/dados — *HTTP+REST+JSON, SQL*
**Como assistir:** Trace de request real; desenhe status codes e corpo; no SQL, rode queries no Postgres do P1 (não só slide).

**O que construir:** Contratos REST do P1 (recursos, verbos, códigos); schema/migrations alinhados às entidades que você *vai* precisar (sem overmodelar).

**Retrieval prompts:**
- “Quando 201 vs 204 vs 400 vs 404 no meu `POST/DELETE`?”
- “Idempotência: o que significa para `PUT` vs `POST` aqui?”
- “Escreva o `SELECT`/`JOIN` que a listagem do P1 precisa — sem olhar.”

**Falhas comuns:** Decorar métodos HTTP sem curl; SQL em abstrato sem tabela real; pular JSON até “chegar no Spring”.

---

### 4) Framework hands-on — *Spring Boot, JPA+Postgres+Flyway, Validation+ControllerAdvice+DTO≠entity, Spring Security+JWT path A, OpenAPI/springdoc*
**Como assistir:** Worked example → fade → **implementar no P1 sem o vídeo**. Pule demos fora do escopo. Security: **só path A** (API emite JWT; filter + JJWT). Resource Server = pós-P1 opcional.

**O que construir (sempre no acumulativo):**
- Boot: skeleton + 1 resource vivo.
- JPA+Flyway: entities + migrations; **relacionamentos aprendidos construindo no P1**, não como curso separado.
- Validation/Advice/DTO: request DTO ≠ entity; erros em JSON consistente.
- Security JWT-A: login/emissão + filtro validando token nas rotas protegidas.
- OpenAPI: documentar os endpoints que já existem (verdade do código > spec fantasia).

**Retrieval prompts:**
- “Fluxo de um request autenticado no P1, camada a camada.”
- “Por que esta classe não pode ser a entity exposta?”
- “O que o filtro JWT rejeita e com qual status?”
- “Onde o Flyway grava a versão e o que fazer se a migration falhar?”

**Falhas comuns:** Tutorial hell de Spring sem portar; estudar Resource Server cedo; JPA “completo” antes de 1 CRUD sólido; misturar entity na API; OpenAPI antes de ter endpoints estáveis.

---

### 5) Testes — *JUnit+Mockito*
**Como assistir:** Foque no ciclo red → green → refactor; veja *o que* mockar (porta) vs o que não mockar (regra pura).

**O que construir:** Testes no P1 para service/controller críticos (validação, regra de negócio, security happy/unauthorized). Um teste bom > cobertura teatral.

**Retrieval prompts:**
- “Este teste quebra se eu remover qual linha de produção?”
- “Por que mockei X e não Y?”
- “Nomeie o teste pelo comportamento observável.”

**Falhas comuns:** Só `@SpringBootTest` pesado para tudo; mockar o System Under Test; testes que espelham a implementação e quebram no refactor sem achar bug.

---

## Ligação com o P1 âncora

Toda sessão deve **alimentar a API acumulativa (Tarefas/Contatos)**.

| Sessão estuda… | Deve deixar no P1… |
|----------------|--------------------|
| Java / OOP | Tipos de domínio, regras puras |
| Git / Maven | Repo saudável, build reproduzível |
| HTTP / SQL | Contratos + schema reais |
| Spring Boot | App sobe; health; 1º resource |
| JPA + Flyway | Persistência real; migrations versionadas; relações *no domínio do P1* |
| Validation / Advice / DTO | API segura contra input lixo; erros padronizados |
| Security JWT-A | Rotas protegidas; token emitido e validado (path A only) |
| JUnit / Mockito | Rede de segurança para refatorar sem medo |
| Docker Compose | Onboarding em um comando |
| OpenAPI | Spec alinhada ao que o curl já prova |

**Princípios de ligação:**
- Não abra repo-tutorial paralelo “só para acompanhar”. Porte a ideia no P1 no mesmo dia.
- Relacionamentos JPA: aprenda *quando o domínio pedir* (ex.: Contato–Tarefa), não numa trilha isolada.
- Security: path A agora; Resource Server depois do P1, se ainda fizer sentido.
- Se o método de estudo atrasa o próximo commit hireable, **corte o método**.

Fora de escopo permanente neste ciclo: Kafka, K8s, microservices, React, Python/AI.

---

## Mini templates

### Template de nota PT (Q/A)

```markdown
# [Tópico] — [fatia concreta]  (ex.: Validation — POST /contatos)

## Meta da sessão
Uma frase.

## Q → A
**P:** …?
**R:** … (suas palavras; 3–8 linhas)

**P:** …?
**R:** …

## Onde no P1
Arquivos / endpoints tocados.

## Armadilha
O erro que quase cometi / o que o vídeo omitiu.

## Review
1d: ____  3d: ____  7d: ____
```

### Template de flashcard

**Frente:** pergunta de *decisão* ou *reconstrução* (não “o que é Spring?”).  
**Verso:** resposta curta + 1 exemplo do P1.

Exemplos de frente:
- “DTO vs entity no `POST /tarefas` — o que retorna e por quê?”
- “Ordem: Filter JWT → Controller → Service → Repository?”
- “Migration Flyway falhou no meio — o que verifico primeiro?”

Limite: 3–5 cards por sessão. Se passar disso, você está catalogando em vez de praticar.

### Definition of done da sessão

Uma sessão está **done** somente se:

1. Meta de 1 frase foi escrita *antes*;
2. Houve retrieval closed-book (explicação ou quiz mental);
3. Existe **mudança no repo acumulativo** (mesmo mínima) *ou* evidência explícita de por que hoje foi só CLI/conceitual com artefato (nota Q→A + comando reproduzível);
4. 3–5 cards **ou** 1 nota Q→A;
5. Reviews 1d / 3d / 7d anotados;
6. Você responde com honestidade: **“Consigo construir sem o vídeo?”** — sim / parcial (e o que falta no fade de amanhã).

Se 2–3 falharam, a sessão foi exposição, não aprendizado. Corrija na próxima antes de avançar de tópico.

---

*Mentor de Estudos — foque no próximo commit que um recrutador entenderia. O mapa de fontes diz o quê assistir; este doc diz como transformar vídeo em habilidade.*
