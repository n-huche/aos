# FJ-01 — como estudar (prontidão para FJ-02)

**Atualizado:** 2026-09-06  
**Objeto:** método e profundidade mínima para os tópicos do [FJ-01](../phases/fj-01-study.md), no formato YouTube-first → mini-repo acumulativo  
**Fontes:** CS education + psicologia cognitiva traduzida; mapa [fj-01-study](../phases/fj-01-study.md); stack [fj-stack](./fj-stack.md)

## Pergunta

Qual método e qual profundidade mínima nos tópicos do FJ-01 levam **mais rápido** à prontidão para abrir a [FJ-02](../phases/fj-02-projects.md) — sem domínio profundo?

## Contexto

- Meta de carreira: 1ª vaga backend Java+Spring ([fj-stack](./fj-stack.md)).
- FJ-01 é pré-requisito da FJ-02 (Projeto 1 hireable), não um curso completo.
- Consumo real: **vídeo YouTube** (EN ok) como fonte principal; **≤1 complementar escrito** por tópico; prática no **mesmo mini-repo acumulativo**.
- Restrição: aprender rápido; gaps finos se resolvem *fazendo* o P1.

## Opções

| Critério | A — Binge + copiar tutorial | B — Domínio profundo por tópico | C — WE + fade + retrieval até gate FJ-02 |
|---|---|---|---|
| Velocidade aparente | Alta | Baixa | Média na sessão |
| Tempo até FJ-02 | Ruim (tutorial hell) | Ruim (overlearning) | **Melhor** |
| Transferência ao P1 | Fraca (reconhecimento) | Forte demais p/ o momento | Suficiente |
| Alinhamento ao formato YouTube→repo | Não | Parcial | **Sim** |

## Achados

Síntese ancorada em **aprender programação / tutoriais de software** e só então em mecanismos cognitivos gerais. Corpus: papers clássicos com DOI.

### 1. Worked examples e carga cognitiva (CS / instrução)

- Para novatos, estudar uma solução completa (worked example) reduz busca means-end e carga extrínseca vs. inventar do zero — base de Cognitive Load Theory ([Sweller, 1988](https://doi.org/10.1016/0364-0213(88)90023-7); overview em [Sweller et al., 1998](https://doi.org/10.1023/A:1022193728205)).
- No FJ-01 o **vídeo é o worked example** — só funciona se tratado como procedimento (pause/predict), não binge passivo.
- **Subgoal labels** (nomear a *função* do passo, não a “história” do todo-list do vídeo) melhoram aquisição e organização do procedimento (trabalhos de Margulieux e linha STEM/CS education sobre subgoals; ver também sínteses de worked examples em programação, ex. Muldner et al. TOCE).
- **Fading / completion problems:** exemplo completo → lacunas → gerar sozinho acelera a transição para código próprio ([Renkl, Atkinson & Große, 2004](https://doi.org/10.1023/B:TRUC.0000021815.74806.f6); evidência recente em programação com faded WE, ex. [Tech Know Learn, 2025](https://doi.org/10.1007/s10758-025-09901-2)).
- **Expertise reversal:** depois que o schema existe, exemplo completo atrapalha ([Kalyuga et al., 2001](https://doi.org/10.1037/0022-0663.93.3.579)). No FJ-01: WE no 1º `@RestController`; no 2º CRUD similar, **não** reassistir — ir ao repo.

### 2. Formato vídeo / tutorial de software

- Em treinamento baseado em vídeo, **sinalização** e **prática intercalada com o vídeo** melhoram desempenho (revisões Educ. Sci. / software-training: prática durante o tutorial > assistir bloco longo e codar depois).
- Long-form YouTube deve ser **segmentado** por meta de 1 frase (timestamps), senão satura memória de trabalho.
- WE + self-explanation guiada (explicar o que o trecho faz) favorece *transfer* melhor que só ouvir o instrutor.
- “Tutorial hell”: tutoriais treinam reconhecimento com cues do narrador; o P1 exige recall sem cues. Saída alinhada à evidência: rebuild closed-book + artefato no **seu** repo.

### 3. Mecanismos cognitivos — só traduzidos ao FJ-01

- **Retrieval / testing effect:** testar memória melhora retenção atrasada mais que restudar ([Roediger & Karpicke, 2006](https://doi.org/10.1111/j.1467-9280.2006.01693.x); review [2006](https://doi.org/10.1111/j.1745-6916.2006.00012.x)). Aqui = explicar endpoint / reescrever filtro JWT **sem** o vídeo.
- **Distributed / spaced practice:** espaçar revisões melhora retenção; o intervalo ótimo cresce com o horizonte ([Cepeda et al., 2006](https://doi.org/10.1037/0033-2909.132.3.354)). Aqui = refazer fatia ou Q→A em ~1d/3d/7d, **não** reassistir o curso.
- **Interleaving** (depois da aquisição): misturar tipos de problema melhora escolha de estratégia ([Rohrer et al., 2015](https://doi.org/10.1037/edu0000001); [Taylor & Rohrer, 2010](https://doi.org/10.1002/acp.1598)). Aqui = DTO vs entity, `@RequestBody` vs Param, `ddl-auto` vs Flyway.
- **Generation effect:** gerar a resposta (código) > só ler ([Slamecka & Graf, 1978](https://doi.org/10.1037/0278-7393.4.6.592)).
- **Desirable difficulties:** spacing, testing, interleaving doem na sessão mas melhoram retenção/transfer; dificuldade sem base vira *undesirable* ([Bjork & Bjork, 2011/2014](https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/04/EBjork_RBjork_2011.pdf)).
- **Utilidade relativa (síntese ampla):** practice testing e distributed practice = alta utilidade; highlighting/rereading = baixa ([Dunlosky et al., 2013](https://doi.org/10.1177/1529100612453266)).
- **Deliberate practice:** meta estreita, fora da zona de conforto, feedback rápido ([Ericsson et al., 1993](https://doi.org/10.1037/0033-295X.100.3.363)). Feedback no FJ-01 = compila / curl / teste / commit — não “terminei o vídeo”.

### 4. Addendum CS-ed (reforço)

- Com vídeo e exercícios em links separados, alunos assistem e pulam o código; prática **acoplada** ao vídeo aumenta engajamento conjunto ([Buffardi & Wang, ITiCSE 2022](https://doi.org/10.1145/3502718.3524778)) → repo ao lado / commit no mesmo bloco.
- Atividade **generativa** durante o vídeo (pausar, self-explain, imitar) > só assistir ([Mayer, Fiorella & Stull, ETR&D 2020](https://learningglass.eu/en/wp-content/uploads/sites/2/Mayer2020_5-ways-to-increase-the-effectiveness-of-instructional-video.pdf)).
- Fading orientado a **conceito/subgoal** (não só apagar a última linha) melhora near/far transfer (Shin et al., linha 2023/24) → fade por subgoal do endpoint (JWT/JPA).
- Retrieval espaçado/intercalado prediz desempenho em CS ([YeckehZaare et al., ICER 2019](https://doi.org/10.1145/3291279.3339411)) → review ~48h closed-book no mini-repo.
- Prática curta + feedback imediato prediz exam (Edwards / CodeWorkout, CompEd 2019) → curl/teste verde como critério da fatia.
- Transfer entre contextos precisa *bridging* explícito (Tshukudu et al.) → periodicamente 1 feature com os **mesmos subgoals**, domínio do P1.
- Síntese WE em programação: [Muldner et al., TOCE](https://doi.org/10.1145/3560266).

**Sessão longa opcional (~75–90 min):** subgoals → vídeo segmentado → implementar/fade → variante → retrieval → testes + nota “o que falharia no P1” → +48h spaced 15–20 min.

### 5. Lacunas (honestas)


- Poucos RCTs em crash courses YouTube long-form de Spring Boot; ponte por mecanismo (CLT, WE, fading, prática intercalada).
- “Tutorial hell” é bem explicado cognitivamente; o rótulo popular é menos paper-formal.

## Decisão

Adotar o protocolo **C**: tratar YouTube como worked example com **fade rápido** para o mini-repo, retrieval closed-book, e **parar no gate de prontidão FJ-02** — não maestria.

Profundidade-alvo por tópico = *shallow-but-enough*: consegue começar o Projeto 1 sem travar no fundamental; detalhes se aprendem no P1.

## Implicações

Operacionalização: [learning-method](../learning-method.md). Mapa de fontes: [fj-01-study](../phases/fj-01-study.md).

### Sessão done (25–50 min)

1. Meta em 1 frase  
2. Só o trecho de vídeo alinhado (pular fora de escopo)  
3. Vídeo como WE: pause + predict  
4. Retrieval closed-book (explicar em PT)  
5. **Commit** no mini-repo acumulativo  
6. “Consigo sem o vídeo?” — se não, fade amanhã (não playlist nova)

### Fade explícito

Assiste pedaço → completa o próximo passo sozinho → implementa **sem** vídeo → próximo feature similar = do zero (vídeo só se travar ~20–30 min).

### Critérios de saída (gate FJ-02) — por tipo

| Tópico | Já sabe o suficiente quando… | Skim / pular |
|---|---|---|
| Java básico | Variáveis, if/loops, métodos, classes, ArrayList, try/catch; classe de domínio simples closed-book | Swing/GUI, threads, genéricos profundos |
| OOP | Encapsulamento + interface; uso no domínio do P1; equals/hashCode básico se precisar | GoF, reflection |
| Git/GitHub | init/add/commit/branch/push no mini-repo | rebase avançado, hooks |
| Maven | Lê `pom.xml`, `mvn test`/`package`, adiciona 1 dep | multi-module |
| SQL | CRUD + JOIN + PK/FK no Postgres do repo | triggers, procedures |
| HTTP/REST/JSON | Verbos, status, JSON; curl em 1 endpoint | HTTP/2–3, Node do vídeo |
| Spring Boot | App sobe; Controller + Service + DI + yml | módulos laterais |
| JPA+Flyway | 1 entity + repo + 1 migration; `ddl-auto` não é estratégia final | N+1 “curso”, cloud do vídeo |
| Validation/DTO/Advice | `@Valid` + DTO≠entity + erro JSON mínimo | groups/custom complexos |
| Security JWT-A | Emite JWT + filtro + 401 em rota protegida | OAuth2, path B |
| JUnit/Mockito | 1 teste de service com mock; `mvn test` verde | Testcontainers agora |
| Docker Compose | Compose sobe Postgres (+ app se der) | K8s/Swarm |
| OpenAPI | springdoc abre nos endpoints existentes | codegen, Springfox |


### Anti-padrões a cortar

Binge sem commit · copiar projeto do YouTube · digitar *com* o vídeo o tempo todo · 2º complementar · WE demais após schema formado · Anki/ritual que atrasa o próximo commit.

## Riscos

- **Fluência enganosa do vídeo** — mitiga: retrieval + commit obrigatório.  
- **Overlearning FJ-01** — mitiga: gate explícito → FJ-02.  
- **Evidência indireta (poucos RCTs Spring/YouTube)** — mitiga: mecanismos robustos (WE/CLT/retrieval); ajustar se o P1 mostrar gaps recorrentes.  
- **Desirable difficulty sem base** — mitiga: fade; se não consegue completar o passo, volte um nível de WE (não force “genérico”).

## Critério de sucesso

**Gate único para abrir FJ-02** (mesmo com buracos):

1. Mini-repo sobe com `./mvnw` + Postgres via Compose (ou caminho documentado).
2. Sem vídeo, você esboça e implementa: 1 resource REST + service + entity/DTO separado + 1 migration Flyway + login JWT path A protegendo 1 rota + 1 teste de service.
3. Explica em ~2 min: `HTTP → filter JWT → @Valid → service → JPA → JSON`.
4. **Não** exige: equals perfeito, JPA avançado, Resource Server, cobertura alta, OpenAPI completo, “terminar” os vídeos do mapa.

Quando o gate for verdade, o mapa vira referência on-demand durante o P1 — não trilha a completar. KPI = P1 destravado, não retenção de syllabus.

## Bibliografia (DOIs / URLs)

### CS education / WE / programação
- Margulieux, Morrison & Decker (2020): https://doi.org/10.1186/s40594-020-00222-7
- Margulieux, Guzdial & Catrambone (2012): https://doi.org/10.1145/2361276.2361291
- Margulieux, Morrison & Decker (2019): https://doi.org/10.1145/3304221.3319756
- Muldner, Jennings & Chiarelli (TOCE): https://doi.org/10.1145/3560266
- Gray et al. (2007): https://doi.org/10.1145/1288580.1288594
- Renkl, Atkinson & Große (2004): https://doi.org/10.1023/B:TRUC.0000021815.74806.f6
- Kalyuga et al. (2003) expertise reversal: https://doi.org/10.1207/S15326985EP3801_4
- Kalyuga (2007): https://doi.org/10.1007/s10648-007-9054-3
- van Merriënboer & de Croock (1992): https://doi.org/10.2190/MJDX-9PP4-KFMT-09PM
- Shin, Jung, Zumbach & Yi (2023): https://doi.org/10.1177/07356331231174454
- Shin, Jung & Lee (2024): https://doi.org/10.1007/s11409-023-09362-x
- Faded WE (Tech Know Learn 2025): https://doi.org/10.1007/s10758-025-09901-2
- Buffardi & Wang (2022): https://doi.org/10.1145/3502718.3524778
- Video software training Educ Sci (2023): https://doi.org/10.3390/educsci13060602
- YeckehZaare et al. (2019): https://doi.org/10.1145/3291279.3339411
- Edwards et al. / CodeWorkout (2019): https://doi.org/10.1145/3300115.3309525
- Tshukudu et al.: https://doi.org/10.1145/3488042.3488050

### Vídeo / cognitivos (traduzir com cuidado)
- Mayer, Fiorella & Stull (2020) PDF: https://learningglass.eu/en/wp-content/uploads/sites/2/Mayer2020_5-ways-to-increase-the-effectiveness-of-instructional-video.pdf
- Roediger & Karpicke (2006) testing: https://doi.org/10.1111/j.1467-9280.2006.01693.x
- Cepeda et al. (2006) spacing: https://doi.org/10.1037/0033-2909.132.3.354
- Dunlosky et al. (2013): https://doi.org/10.1177/1529100612453266
- Ericsson et al. (1993): https://doi.org/10.1037/0033-295X.100.3.363
- Slamecka & Graf (1978): https://doi.org/10.1037/0278-7393.4.6.592
- Rohrer et al. (2015) interleaving: https://doi.org/10.1037/edu0000001
