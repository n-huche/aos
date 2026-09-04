# Orientações — do zero ao Toujours em produção

Roteiro pessoal. Não commitar. Seguir na ordem; cada fase termina com **Pronto quando**.

Regras de negócio: `docs/domain`. Decisões técnicas: `docs/architecture`. Este arquivo só diz o que fazer e como conferir. Dúvida que muda produto, estrutura ou custo → ADR primeiro, código depois.

**Regras de ouro**

1. Nada de dinheiro real antes da Fase 1 e da Fase 5 verdes no sandbox.
2. Bug em `billing` ou no ciclo de vida da página: teste que falha, depois o fix.
3. Conventional Commits em inglês (`feat(pages): …`). Um branch por fase; merge na `main` com CI verde.
4. Versões: última estável no dia da instalação, pinadas em `libs.versions.toml` e `package.json`.
5. `PlanLimits` em `shared.domain`. Mutações HTTP só no navegador (Origin check). Takedown é SQL, não API de admin.

**Esforço** (dias focados): 0–2 ≈ 2 · identity 1–2 · pages/editor 5–7 · billing 3–4 · avisos/exclusão 1 · landing 1–2 · produção 2. Total ≈ **14–20**. O editor é o que estoura; se apertar, corte drag-and-drop e preview rico da paleta.

---

## Fase 0 — Ferramentas e contas

- [ ] Homebrew. Java 21 (`temurin@21`). Node 22 LTS + `corepack enable pnpm`. Docker Desktop. `flyctl`, `gh`, `cloudflared`.
- [ ] Contas: Fly.io (cartão), Neon, Cloudflare (DNS de `nhuche.com` **precisa** estar lá por causa do R2), Resend, Sentry (`toujours-api` e `toujours-web`), Mercado Pago (app Checkout API; credenciais de **teste** e de **produção**; contas de teste vendedor/comprador).
- [ ] GitHub: repo **público**. Dependabot semanal (`gradle`, `npm`, `github-actions`).
- [ ] `printf 'instructions.md\nplaybook.md\n' >> .git/info/exclude`

**Pronto quando:** `java -version`, `node -v`, `pnpm -v`, `docker ps`, `fly version`; painéis acima abrem; `git check-ignore -v instructions.md` confirma.

---

## Fase 1 — Gate Mercado Pago (ADR 0006)

Provar no **sandbox**, antes de codar billing, que dá para cobrar cartão salvo sem o portador (sem CVV).

- [ ] Customer → token de cartão de teste → card no customer → horas depois, `POST /v1/payments` com token só do `card_id`, `X-Idempotency-Key`. Tem que sair `approved`.
- [ ] Mesma key de novo: não duplica. Refund funciona. Webhook chega (`cloudflared`) com `x-signature`.

Aprovou → ADR 0006 vale. Recusou → **ADR 0013** (pre-approval nativo). Só então siga.

---

## Fase 2 — Esqueleto

- [ ] `docker-compose.yml`: Postgres 16 (`toujours`) + MinIO; buckets `toujours-images` (público) e `toujours-backups` (privado). `scripts/dev.sh` sobe e imprime URLs.
- [ ] API: Spring Initializr (Gradle Kotlin DSL, Java 21, Boot 3, Web, Validation, Data JDBC, PostgreSQL, Flyway, Actuator, Testcontainers) **por cima** de `apps/api`. **Sem** Spring Security.
- [ ] Libs: springdoc, ShedLock JDBC, Bucket4j, AWS SDK S3, Thumbnailator, TwelveMonkeys JPEG, encoder WebP, SDK Mercado Pago, Resend, Sentry, logstash-logback, Spotless, ArchUnit, Testcontainers PostgreSQL.
- [ ] `application.yml`: 8080, `${DATABASE_URL}`, pool 5, Flyway, Jackson datas ISO, virtual threads, `/health` só. Perfil `local`: Postgres do compose, MinIO, e-mail no log, MP sandbox.
- [ ] Dockerfile multi-stage (JRE 21, `-XX:MaxRAMPercentage=70`). `fly.toml`: `toujours-api`, `gru`, 1 GB, always on, check `/health`.
- [ ] Web: `create-next-app` em `/tmp` e copiar para `apps/web`. Tiptap (schema restrito), `heic2any`, `@mercadopago/sdk-react`, Sentry. Dev: Prettier, Vitest, Playwright, `openapi-typescript`. `output: "standalone"`. Rewrite `/api/:path*` → `API_INTERNAL_URL`. Rotas `src/app/api/internal/*` ganham do rewrite.
- [ ] `pnpm gen:api` gera `src/api/schema.ts` (commitado; regenere quando a API mudar — sem job de CI para isso).
- [ ] Web Dockerfile + `fly.toml`: `toujours-web`, 512 MB, auto-stop.
- [ ] CI: `api.yml` → `./gradlew spotlessCheck test` + deploy na `main`. `web.yml` → `format:check`, lint, `tsc`, vitest + deploy. `backup.yml` diário 05:00 UTC (`pg_dump` → R2, 30 dias) — ativar na Fase 7.

**Pronto quando:** compose + API (`/health`) + Next sobem; workflows de teste passam (deploy pode ficar `if: false` até a Fase 7).

---

## Fase 3 — Identity

- [ ] `V1__identity.sql`: citext, `accounts`, `verification_codes`, `sessions`, `shedlock`.
- [ ] `shared.domain`: `Money`, UUIDv7, `Clock` injetável, `PlanLimits`.
- [ ] Filtros: problem+json, Origin (mutações; ignora `/webhooks/**`), request id, rate limit (códigos, IP).
- [ ] Códigos 6 dígitos hashed, 10 min, 5 tentativas. Sessão cookie `HttpOnly`/`Secure`/`SameSite=Lax`, 180 dias. `POST /auth/codes` sempre 202.
- [ ] E-mail de código via `notifications` (log no `local`).
- [ ] Testes: unitários do código/sessão; `AuthFlowTest`; ArchUnit (domain sem I/O, módulos só via `application`, sem ciclo, `billing` não importa `pages`).
- [ ] `/login` (e-mail → código → `/edit`). Cliente `fetch` com cookie; servidor só `GET`. `/` logado redireciona para `/edit`.

**Pronto quando:** entra, recarrega logado, sai. CI verde.

---

## Fase 4 — Pages + media

- [ ] `V2`/`V3`: página (índice parcial no slug e em `account_id` onde não deletada, `expired_reason`), working copy, published, `images`.
- [ ] Domínio: `Slug`, `Page` (transições + `expire(reason)`; `restore()` recusa takedown), validador do documento, contagem. **Sem** `PlanLimits` aqui. `LimitsQuery` provisório = Trial.
- [ ] Autosave `PUT` documento inteiro + `expectedUpdatedAt`. Publish copia. Jobs `ExpireTrials`, `DeleteExpiredPages`. Exclusão de conta = hard delete.
- [ ] Upload multipart → WebP ≤ 2048 px + thumb, R2/MinIO. Spotify oEmbed só faixa.
- [ ] Revalidate: `POST` no web com `REVALIDATE_SECRET`.
- [ ] `/edit`: sem página e trial livre → slug; trial já usado → Assinar em `/conta`; Trial/Active → editor (chrome Publicar / Ver / Conta); Expired → Assinar/Restaurar (pagar não restaura sozinho). `/s/[slug]` (cache, `noindex`, OG, barra Editar se for o dono). Playwright: criar → editar → publicar → visitar.
- [ ] Testes de transições, inclusive takedown: SQL `expired_reason = 'takedown'` → restore do dono 409. Sem assinatura e `trial_used` → `POST /page` 422 `trial-used`.

**Pronto quando:** fluxo local com MinIO; trial expirada some do ar (ajuste `trial_ends_at` no banco).

---

## Fase 5 — Billing

- [ ] `V4`: payment methods, subscriptions, charges, webhook_events.
- [ ] Máquinas de `Subscription` e `Charge` (3 tentativas). Gateway atrás de porta; fake no `local`. Webhook verifica assinatura, reconsulta o pagamento, idempotente, sempre 200.
- [ ] Assinar / renovar / cancelar / desfazer / reembolsar 7 dias. Trial → active (só se ainda for trial; expired espera restore). Ended → página expired. Cobrança `abandoned` tem que estar quitada antes de assinar de novo.
- [ ] `/conta`: Brick só tokeniza; token vai para a API. Slug, sair, apagar conta.
- [ ] Sandbox manual: aprovado, recusado (402), cancelar, reembolso, webhook duplicado.

**Pronto quando:** testes verdes e checklist sandbox no PR.

---

## Fase 6 — Avisos, limpeza, exclusão

- [ ] Os 8 jobs do ADR 0009, cada um com teste (relógio avançado).
- [ ] Excluir conta: cancela → apaga storage → página → cliente MP → identity → e-mail.

---

## Fase 7 — Landing e produção

Landing, termos e privacidade (PT-BR; abuso `abuso@toujours.nhuche.com`; CDC art. 49; takedown). Sentry nos dois apps. `robots.txt`. Neon `sa-east-1`, R2 (`img.toujours.nhuche.com` + backups), Resend, webhook MP de produção. Secrets no Fly. DNS **cinza** para `toujours` e `api.toujours`. Deploy pela `main`. Smoke: entrar de verdade, publicar, ver no celular, preview no WhatsApp. Rodar o backup uma vez e **abrir o dump** num Neon descartável.

**Pronto quando:** site no ar, sem cartão de verdade ainda.

---

## Fase 8 — Lançamento

- [ ] Um pagamento real (R$ 5) + reembolso pelo produto. Depois reassinar e deixar um ciclo.
- [ ] E-mail no inbox (Gmail/Outlook), `noindex` no `curl -I`, alerta Sentry, UptimeRobot em `/` e `/health`.
- [ ] Tag `v1.0.0`. README: "In production at toujours.nhuche.com".

---

## Operação

- Dia 1: uma renovação de teste no sandbox (ou relógio avançado) gerou `charges` certo.
- Semana: Dependabot; backup dos últimos 7 dias no R2.
- Mês: Fly ≈ US$ 6–9; Neon/R2/Resend nos free tiers; Sentry.
- Takedown: SQL nas notas de implementação + revalidate.
- Mudança de preço: domínio → ADR se precisar → `Plan.java` e `src/lib/plans.ts`.
