# Playbook — como estruturar um projeto do zero

Guia pessoal, independente de projeto. Destilado do processo usado no Toujours. Não commitar.

A ideia central: **escrever o projeto antes de codá-lo**, em duas camadas (o que ele é; como ele é feito), de forma que nenhuma decisão de produto, estrutura ou custo sobre para a hora do código. O código vira consequência.

---

## 1. O processo

Sempre nesta ordem. Não pule etapas; cada uma é barata e corrige a anterior.

1. **Ideia em um parágrafo.** O que é, para quem, qual o resultado para o usuário, por que existe (portfólio, produto, ferramenta interna, estudo).
2. **Domínio em prosa bruta.** Escreva tudo que o produto faz, sem pensar em tecnologia. Não precisa estar organizado ainda.
3. **Rodada de perguntas.** Leia o texto procurando: estados não nomeados ("o que acontece depois que expira?"), limites sem unidade, atores ausentes (quem vê? quem paga?), palavras usadas com dois sentidos, regras que dependem de implementação ("conta tudo" — o que é "tudo"?), e dinheiro sem regra de arredondamento/mínimo/reembolso. Responda ou decida. Registre as decisões.
4. **Domínio organizado.** Reescreva por contexto (não por tela), em regras curtas, com glossário. Critério de pronto na seção 7.
5. **Restrições e prioridades.** Antes de qualquer decisão técnica, escreva o que não pode mudar (orçamento, stack imposta, prazo, legislação, time) e ordene os atributos de qualidade. Isso é o que desempata decisões depois.
6. **Arquitetura.** Visão geral, modelo de dados, ADRs, notas de implementação. Cada decisão avaliada contra o item 5.
7. **Roteiro pessoal (`orientacoes.md`).** Fases, checklists, "pronto quando". O que fazer, em que ordem, como conferir.
8. **Código**, na ordem do roteiro, uma fase por vez, cada fase deployável.

Regra que sustenta tudo: **se durante o código surgir uma decisão que muda comportamento, estrutura ou custo, para e volta para o documento certo.** Decidir no código é falha de documentação.

Como trabalhar com IA nesse processo: peça uma etapa por vez, leia antes de pedir a próxima. Erro na etapa 4 custa pouco; erro na etapa 4 descoberto na etapa 8 custa tudo que veio no meio. Use raciocínio alto nas etapas 3 a 6 e nas partes do código que envolvem dinheiro ou exclusão de dados; baixo no resto.

---

## 2. O que todo projeto tem

Independentemente do tipo:

```
README.md              porta de entrada: o que é, status, links para docs, stack, layout do repo
LICENSE
.gitignore             SO, IDE, build, dependências, segredos (.env*)
.env.example           nomes das variáveis, nunca valores (quando houver configuração)
docs/
  domain/              o que o produto faz (regras, sem tecnologia)
  architecture/        como é feito e por quê
.github/workflows/     ou equivalente: no mínimo build + testes em PR
orientacoes.md         roteiro pessoal, fora do controle de versão (ou em .gitignore)
```

E um código organizado por **módulos que espelham os contextos do domínio**, cada módulo com camadas explícitas (seção 5).

O que **não** tem por padrão: pasta `utils/` genérica, `docs/` com um único arquivo gigante, `TODO.md` (vai para issues ou para o roteiro), documentação de código gerada automaticamente commitada.

---

## 3. Como escrever cada documento

### README.md

Uma tela. Ordem: nome + uma frase; um parágrafo do que é e para quem; status atual (uma linha); links para os docs em ordem de leitura; stack em uma linha com "motivos nos ADRs"; layout do repositório com um comentário por pasta. Leitor alvo: alguém que nunca viu o projeto e tem 60 segundos.

### docs/domain/

**O que vai:** regras de negócio, conceitos, estados, limites, preços, o que o usuário pode e não pode fazer, o que acontece com o tempo.

**O que não vai:** telas, botões, "no topo da página aparece...", tecnologia, tabelas de banco, nomes de endpoint. Teste: se você trocasse toda a stack, o texto continuaria verdadeiro? Se não, está no lugar errado.

**Como dividir:** um arquivo por **contexto** (bounded context), não por tela. Sinais de contexto: um conjunto de conceitos que muda junto e tem um vocabulário próprio (ex.: cobrança; ciclo de vida do recurso principal; conteúdo do recurso; identidade/conta). Dois arquivos ficam grandes demais quando passam de ~100 linhas ou quando um leitor precisa pular seções para achar uma regra. Nomes de arquivo em kebab-case, em inglês se o código for em inglês.

**Sempre presente:**
- `glossary.md` — tabela termo → significado. É a linguagem ubíqua; os nomes daqui viram nomes de classe, tabela e pasta.
- Um arquivo com o **ciclo de vida do recurso principal**: diagrama de estados (Mermaid `stateDiagram-v2`) + tabela "estado × o que é permitido" + regras por estado.
- Se houver dinheiro: um arquivo de **planos e cobrança** com tabela de planos, regras de renovação/falha/cancelamento/mudança/reembolso, e a fórmula de qualquer cálculo.
- Se houver usuário: um arquivo de **conta** (identidade, propriedade, exclusão, locale).

**Estilo:** uma regra por linha, frases curtas, imperativo ou indicativo ("O dono pode..."; "A página fica..."). Tabelas para qualquer coisa com mais de duas dimensões. Números sempre com unidade. Nada de "etc." — se existe, lista; se não, corta. Quando uma regra é uma escolha deliberada que parece erro (ex.: plano flexível mais barato que o fixo), diga que é intencional e por quê.

### docs/architecture/

Camadas de profundidade: quem quer só a visão geral lê dois arquivos; quem quer tudo lê todos. Ordem de leitura fixada num `README.md` de índice.

**constraints.md** — restrições duras (time, orçamento em número, stack imposta, prazo, lei, domínio disponível) e **atributos de qualidade em ordem de prioridade** (ex.: corretude de dinheiro > simplicidade > legibilidade > custo > segurança > operabilidade > performance). Diga explicitamente o que *não* é objetivo (ex.: escala horizontal). Feche com princípios derivados ("servidor é a fonte da verdade para limites"; "tudo que é tempo é timestamp no banco + job idempotente"; "terceiros atrás de uma porta"). Este arquivo é o que você consulta para desempatar qualquer decisão.

**overview.md** — um diagrama de containers (Mermaid `flowchart`), tabela container → responsabilidade, tabela de módulos → o que possui → de quem depende, e os 5–8 fluxos principais em um parágrafo cada, apontando para o ADR relevante. Ambientes (local, produção; staging só se justificar).

**data-model.md** — convenções gerais (ids, timestamps, dinheiro, fuso), diagrama ER (Mermaid `erDiagram`), tabelas agrupadas por módulo com coluna → tipo → observação, máquinas de estado que não estão no domínio (assinatura, cobrança, job), e o schema de qualquer documento/JSON que o sistema armazena. Aqui vale ser exaustivo: cada coluna que você não escreve agora é uma decisão na hora do código.

**decisions/** (ADRs) — um arquivo por decisão significativa, numerado, imutável (supersede em vez de editar depois de implementado; antes de implementar, editar é ok). Formato: `Status` · `Contexto` (2–3 linhas) · `Opções` (bullets, com o motivo da rejeição em cada) · `Decisão` (uma frase ou tabela) · `Consequências` (bullets, incluindo as negativas). Meia página. Índice em `decisions/README.md`.

Quando vale um ADR: a decisão muda custo, forma do sistema, dependência externa, ou seria difícil de reverter. Quando agrupar: decisões pequenas e correlatas viram um ADR só ("práticas de engenharia": convenções, testes, CI, observabilidade, segurança básica). Se um ADR depende de algo que só dá para saber testando (ex.: API de um provedor), escreva um **gate de validação** explícito nele com o plano B.

ADRs quase sempre presentes: registrar ADRs (0001); forma do sistema (monolito, modular, serviços); stack e versões maiores; hospedagem e domínios com custo estimado; autenticação; persistência do dado principal; práticas de engenharia. Presentes quando o projeto tem: pagamento → provedor e modelo de cobrança + algoritmo de medição se houver uso variável; arquivos → armazenamento e processamento; tempo → jobs agendados; conteúdo público → renderização e cache.

**implementation-notes.md** — tudo que é pequeno demais para ADR mas grande demais para decidir no código: constantes (limites, tempos, listas curadas, palavras reservadas), contratos HTTP (tabela método → caminho → notas → códigos de erro), formato de erro, fluxos passo a passo dos casos delicados (dinheiro, exclusão), lista de e-mails/notificações com gatilho, variáveis de ambiente, escopo explícito (o que fica fora da v1, para ninguém se perguntar), e a **ordem de implementação** em fases deployáveis.

### orientacoes.md (pessoal)

Fases numeradas; cada fase com checklist de caixinhas e um bloco **Pronto quando** verificável. Fase 0 é sempre ferramentas e contas; a última é lançamento; depois, operação contínua. Referencie os docs em vez de repetir regras; aqui vai só *o que fazer, em que ordem, como conferir*. Inclua comandos exatos, nomes de classes e arquivos a criar, e os testes que provam a fase. Regras de ouro no topo (ex.: nada de dinheiro real antes do sandbox verde; todo bug em área crítica ganha teste antes do fix; padrão de commit).

---

## 4. O que muda com o tipo de projeto

| Tipo | Layout | Domínio | Arquitetura | ADRs quase obrigatórios |
|---|---|---|---|---|
| **Biblioteca / SDK** | `src/`, `tests/`, `examples/` | Curto: conceitos e garantias (o que a lib promete) | Foco em API pública, compatibilidade, versionamento | Superfície da API, política de versionamento (semver, deprecação), suporte a plataformas/versões, formato de distribuição |
| **CLI / ferramenta** | `src/`, `tests/`, `docs/usage.md` | Comandos como casos de uso, formatos de entrada/saída | Leve: um overview e poucos ADRs | Formato de config, saída legível × máquina, distribuição (binário, brew, npm), atualização |
| **API / backend só** | `src/` (módulos por contexto) | Completo | Completo, sem seção de renderização | Todos os "quase sempre" + contratos HTTP detalhados nas notas |
| **Full-stack, uma linguagem** (Next full-stack, Rails, Django, Spring + templates) | `src/` com módulos; UI dentro ou em `src/ui` | Completo | Completo | Idem, mais "onde a lógica vive" (servidor, não cliente) |
| **Front + back separados** (linguagens diferentes) | `apps/web`, `apps/api`; `packages/` só se houver código compartilhado | Completo | Completo, com o contrato entre os dois explícito (OpenAPI gerado) | Idem, mais como o front fala com o back (rewrite, CORS, cookies) e hospedagem de cada um |
| **Mobile** | `apps/mobile`, `apps/api` | Completo | Adiciona offline/sync, notificações, lojas | Estado offline e conflito, push, distribuição e review das lojas, versionamento de API por versão do app |
| **Dados / pipeline / ML** | `src/`, `pipelines/`, `notebooks/` (fora do caminho de produção), `data/` ignorado | Definições: fontes, entidades, métricas, qualidade | Foco em fluxo de dados, agendamento, idempotência, linhagem | Armazenamento e formato, orquestração, reprocessamento, versionamento de dados e modelos, custo de compute |
| **Ferramenta interna / protótipo** | `src/` | Um arquivo | `constraints.md` + um ADR de stack | Só stack e "o que este protótipo não é" |

Regras gerais:
- `src/` quando há **um** programa; `apps/` quando há dois ou mais deployáveis; `packages/` só quando algo é de fato compartilhado entre eles.
- Documento que não teria conteúdo não é criado. Um protótipo com `data-model.md` vazio é ruído.
- Quanto mais dinheiro, dados de terceiros ou exclusão irreversível, mais peso em `data-model.md`, máquinas de estado e testes de domínio.
- Portfólio: a legibilidade é entrega. README, glossário e índice de ADRs são os três lugares que um recrutador vai ler; capriche neles.

---

## 5. Estrutura de código

Independente de linguagem:

- **Um módulo por contexto do domínio**, com o mesmo nome do arquivo em `docs/domain`. Mais um `shared` para o que é realmente transversal (dinheiro, ids, tempo, erros) — e só isso.
- **Quatro camadas dentro de cada módulo:**
  - `api` (ou `http`, `cli`): entrada e saída; DTOs; sem regra.
  - `application`: casos de uso, transações, orquestração; chama domínio e infraestrutura.
  - `domain`: entidades, objetos de valor, regras, máquinas de estado; **sem framework, sem I/O**. É o que se testa unitariamente e exaustivamente.
  - `infrastructure`: banco, HTTP externo, storage, e-mail; implementa as portas que `application`/`domain` definem.
- **Módulos conversam por `application`** (chamadas diretas) ou eventos internos; nunca pela tabela do outro. Uma regra de arquitetura em teste (ArchUnit, dependency-cruiser, import-linter) mantém isso verdadeiro.
- **Terceiros atrás de uma porta** (interface) com uma implementação falsa para testes e desenvolvimento local.
- **Tempo injetado** (clock), nunca `now()` solto no domínio.
- **Testes espelham a estrutura**: unitários de domínio (muitos, rápidos), integração com infraestrutura real em container (poucos, por fluxo), e2e mínimo do caminho feliz principal.
- **Migrações** forward-only, numeradas, nunca editadas depois de aplicadas.
- **Configuração** por variável de ambiente, com `.env.example` e um perfil local com defaults apontando para o stack do `docker compose`.

Front-end, quando separado: sem regra de negócio; um cliente de API tipado gerado do contrato; mensagens de erro mapeadas de códigos estáveis; estado global só se a interação exigir.

---

## 6. Checklists

**Domínio pronto quando**
- [ ] Todo conceito do glossário aparece no texto, e todo termo do texto está no glossário.
- [ ] O recurso principal tem diagrama de estados e cada transição tem gatilho e regra.
- [ ] Nenhuma frase menciona tela, tecnologia ou implementação.
- [ ] Todo limite tem unidade e toda contagem tem definição do que conta.
- [ ] Todo valor em dinheiro tem regra de arredondamento, mínimo, falha e reembolso.
- [ ] Todo ator (dono, visitante, admin, sistema) está nomeado e tem o que pode fazer.
- [ ] Toda escolha que parece erro está marcada como intencional, com o motivo.
- [ ] Você consegue responder "e se...?" para expiração, cancelamento, downgrade, exclusão, conflito de edição e falha de pagamento, só lendo o texto.

**Arquitetura pronta quando**
- [ ] `constraints.md` tem número de orçamento e ordem de prioridades.
- [ ] Toda caixa do diagrama tem um custo estimado e um motivo em ADR.
- [ ] Toda tabela tem todas as colunas, tipos e índices não óbvios.
- [ ] Toda máquina de estado fora do domínio está desenhada.
- [ ] Todo terceiro tem porta, implementação falsa, e — se houver dúvida sobre a API — gate de validação com plano B.
- [ ] Todo endpoint tem método, caminho, corpo, códigos de erro com nome estável.
- [ ] Toda operação baseada em tempo tem um job nomeado, agendado e idempotente.
- [ ] Toda notificação tem gatilho e template nomeado.
- [ ] Toda variável de ambiente está listada.
- [ ] O escopo negativo (o que não está na v1) está escrito.
- [ ] Existe ordem de implementação em fases deployáveis.

**Pronto para codar quando**
- [ ] `orientacoes.md` tem Fase 0 (ferramentas/contas) completa e cada fase tem "Pronto quando".
- [ ] O repositório tem README, LICENSE, `.gitignore`, árvore de pastas e CI de build+teste.
- [ ] Você consegue abrir qualquer arquivo de código futuro e dizer em qual pasta ele vai, só pelo nome.

---

## 7. Prompt inicial para reproduzir o fluxo com IA

Cole numa conversa nova, ajustando os colchetes. Anexe o texto bruto do domínio.

```
Vou construir [nome]: [um parágrafo: o que é, para quem, por que existe].
Objetivo: [portfólio / produto real / ambos]. Restrições: [dev solo, orçamento US$ X/mês,
stack imposta: ..., prazo: ..., país/legislação: ..., domínio disponível: ...].

Quero seguir este processo, uma etapa por vez, e você espera minha revisão entre elas:
1. Ler meu texto bruto de domínio (anexo) e me devolver só perguntas: estados não
   nomeados, limites sem unidade, atores ausentes, termos ambíguos, regras que dependem de
   implementação, dinheiro sem regra de arredondamento/mínimo/falha/reembolso. Para cada
   pergunta, proponha uma resposta padrão para eu só confirmar ou vetar.
2. Com as respostas, reescrever o domínio em docs/domain/: um arquivo por contexto (não por
   tela), glossary.md, diagrama de estados Mermaid do recurso principal, regras curtas em
   tabelas e bullets, sem qualquer menção a UI ou tecnologia. Em inglês, enxuto, para leitura
   de recrutador.
3. docs/architecture/: README (índice), constraints.md (restrições + atributos de qualidade
   priorizados + princípios), overview.md (diagrama de containers, módulos, fluxos),
   data-model.md (tabelas completas, máquinas de estado, schemas JSON), decisions/ (ADRs de
   meia página: contexto, opções, decisão, consequências; agrupar as pequenas), e
   implementation-notes.md (constantes, contratos HTTP, erros, fluxos delicados, e-mails,
   env vars, escopo negativo, ordem de implementação em fases deployáveis).
4. Criar a árvore de diretórios do código com módulos espelhando os contextos e quatro
   camadas por módulo (api/application/domain/infrastructure), e documentá-la no README.
5. Escrever orientacoes.md (português, pessoal, não commitado): fases com checklists e
   "pronto quando", da instalação de ferramentas ao lançamento e operação contínua.

Regras: não commite nada; não tome decisão que mude produto, estrutura ou custo sem me
mostrar; quando decidir algo por mim, liste no fim da etapa para eu vetar; se uma decisão
depender de API de terceiro que só dá para confirmar testando, escreva um gate de
validação com plano B no ADR. Meta: ao fim, nenhuma decisão de produto, estrutura ou custo
sobra para a hora de escrever código.
```

---

## 8. Erros que este processo evita (e que eu já cometi ou quase)

- Nomear docs de domínio por tela ("editor", "gerenciador") e deixar UI vazar para a regra.
- "Tudo conta" sem definir o que é tudo — a contagem passa a depender do formato de armazenamento.
- Preço de plano pós-pago menor que o pré-pago sem dizer que é intencional.
- Esquecer o visitante/leitor anônimo como ator.
- Exclusão imediata sem janela de recuperação em um lugar e com janela em outro.
- Free tier de hospedagem que proíbe uso comercial (Vercel Hobby) em produto pago.
- Assumir que um provedor de pagamento permite cobrar cartão salvo sem o portador antes de testar.
- Jobs em memória em plataforma que dorme quando ociosa.
- Sub-caminho de um domínio pessoal (`site.com/projeto`) em vez de subdomínio gratuito.
- Documentar tudo em um arquivo só, ou em quinze ADRs de uma linha.
- Começar pelo billing. Comece por entrar, criar, editar, publicar; dinheiro vem depois que o resto existe.
