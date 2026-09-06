# FJ-01 — como estudar (prontidão para FJ-02)

**Atualizado:** 2026-09-06  
**Objeto:** método e profundidade mínima para os tópicos do [FJ-01](../phases/fj-01-study.md), no formato YouTube-first → mini-repo acumulativo  
**Fontes:** brief do bot Pesquisa (CS education + psicologia cognitiva traduzida); mapa [fj-01-study](../phases/fj-01-study.md); stack [fj-stack](./fj-stack.md)

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

Síntese ancorada em **aprender programação / tutoriais de software** e só então em mecanismos cognitivos gerais. Corpus: Pesquisa + papers clássicos com DOI.

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

### 4. Lacunas (honestas)

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

| Tipo | “Chega” quando… |
|---|---|
| Java / OOP | Escreve classes/enums do domínio do P1 closed-book; sabe equals/hashCode o suficiente para entidades |
| Git / Maven / Compose | Fluxo sozinho no *seu* repo (`commit`, `mvn test`, `compose up`) |
| HTTP / SQL | Contratos REST + schema/migrations mínimos do P1 sem tutorial aberto |
| Spring (Boot, JPA, Validation, JWT-A, OpenAPI) | Sobe app; 1 resource vivo; DTO≠entity; path A JWT nas rotas; Flyway ligado — **sem** reassistir curso inteiro |
| Testes | 1–N testes de service/regra que falham pelo motivo certo |

**Quando abrir FJ-02:** checklist acima no essencial (não perfeição); Security só path A; fora de escopo (Kafka/K8s/React/Resource Server) continua fora.

### Anti-padrões a cortar

Binge sem commit · copiar projeto do YouTube · digitar *com* o vídeo o tempo todo · 2º complementar · WE demais após schema formado · Anki/ritual que atrasa o próximo commit.

## Riscos

- **Fluência enganosa do vídeo** — mitiga: retrieval + commit obrigatório.  
- **Overlearning FJ-01** — mitiga: gate explícito → FJ-02.  
- **Evidência indireta (poucos RCTs Spring/YouTube)** — mitiga: mecanismos robustos (WE/CLT/retrieval); ajustar se o P1 mostrar gaps recorrentes.  
- **Desirable difficulty sem base** — mitiga: fade; se não consegue completar o passo, volte um nível de WE (não force “genérico”).

## Critério de sucesso

Em ≤ o tempo que você alocar para FJ-01, você: (1) tem mini-repo acumulativo com fatias dos tópicos do mapa; (2) passa nos gates da tabela sem reabrir os cursos; (3) **abre FJ-02** e começa o esqueleto do Projeto 1 na mesma semana em que o gate fecha — sem “mais um vídeo” de atraso.
