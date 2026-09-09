# Atualização diária

O usuário só marca checkboxes em [tasks](../../tasks/tasks.md). `[x]` / `[X]` = fez; `[ ]` = não. Pasta só com nota.

1. Entrada

   Pedido de atualização diária, ou relógio ≥ 21:00.
   `{D}` = data do relógio (o dia que acaba). `{D1}` = `{D}` + 1 dia.

2. Ler o índice

   Para cada item: `{fez}` = checkbox marcada. Abrir a nota (não a pasta): `{status}`, `{prazo}`. Tem **Fase:** → `{tipo}` = `de-projeto`; senão `independente`.

3. `{fez}` → status

   `{fez}` e `{status}` = `pendente` → `{status}` = `concluído`.
   `{fez}` e `{status}` = `recorrente` e `{prazo}` é data e `{D}` ≥ `{prazo}` → `{status}` = `concluído`.
   `{fez}` e `{status}` = `recorrente` e (`{prazo}` = `none` ou `{D}` < `{prazo}`) → não mover; no diário entra em concluídas.
   `{status}` = `concluído`: [new-task](new-task.md) passos 4–8 (`completed/`; some do índice). `{tipo}` = `de-projeto`: também [new-phase](new-phase.md) **Status da fase ← tarefas** e **Herança**.

4. Não `{fez}`

   `{status}` = `pendente`: `{balde}` vs `{D1}` ([new-task](new-task.md) passo 6, hoje = `{D1}`). Pasta mudou → mover; apagar pasta vazia.
   `{status}` = `recorrente` e `{prazo}` é data e `{D}` ≥ `{prazo}` → `{status}` = `concluído` (passo 3). Senão fica.

5. Índice

   Reescrever [tasks](../../tasks/tasks.md): só `- [ ]`. Ordem e headings: [new-task](new-task.md) passo 8. Caminhos depois das mudas. Sem `--`. Heading só com item.

6. Diário

   `daily/{D}.md` a partir de [day-template](../templates/day-template.md). Pasta `daily/` só com nota.
   Se `daily/{D}.md` já existe e o índice não tem `[x]` / `[X]`: parar (idempotente).
   **Tarefas Concluídas** = `{fez}`.
   **Tarefas Fracassadas** = não `{fez}` e (`{prazo}` = `{D}` ou `{status}` = `recorrente`). Omitir a seção se vazia.
   **Resultado:** Fracassadas ≠ vazia → `fracasso`. Senão, se `{fez}` também em item com `{prazo}` data ≠ `{D}` e `{status}` ≠ `recorrente` → `sucesso`. Senão `satisfatório`.
   **Notas** só se o usuário já tinha ou pediu.
