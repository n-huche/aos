# Nova fase

Não criar o projeto — se não existir, [new-project](new-project.md). Não inventar datas, pessoas nem o Como. Sem `.gitkeep`. Fase a partir de [phase-template](../templates/phase-template.md). Tarefas: [new-task](new-task.md).

## Antes

1. Confirmar o projeto (`projects/{pending|in-progress|paused|completed}/{slug}/{slug}.md`). Se não existir, parar.
2. Se faltar **slug da fase** (arquivo, inglês) ou **nome do heading** (português), ou se é planejada vs `não planejado`, perguntar. Planejada: falta **Entrega** + **Como** → perguntar; não inventar. Análise só se a complexidade justificar, **antes** desta fase ([analysis-template](../templates/analysis-template.md)).
3. Prefixo: o das fases já no hub (`FJ`, `AY1`). Se o hub ainda não tem prefixo, perguntar.
4. **nn:** próximo número no hub (`01` se ainda não há fases). Não duplicar heading. Se o pedido for **planejar** um heading `não planejado` já existente, usar esse nn e o slug do arquivo — não criar outro.
5. Default de **Status** da fase nova: `pendente` (ou `não planejado`). Pode nascer `pendente` mesmo com nn menores ainda não `concluído`. **Não** pôr `em andamento`, `pausado` ou `concluído` a menos que todas as nn menores estejam `concluído` — recusar e criar como `pendente`. Recorrente sem fim não entra em fase.
6. **Prazo:** copiar o do projeto, salvo override do usuário. Não inventar data.

## Criar

### `não planejado`

1. Só heading no hub em português: `### {PREFIXO}-{nn} — {nome}`, **Status:** `não planejado`, **Prazo**, uma frase. Sem link, sem arquivo em `phases/`, sem tarefas.

### Planejada (`pendente` ou além)

1. Nota `projects/{status}/{slug}/phases/{prefixo}-{nn}-{slug-fase}.md` (copiar o template; `{status}` = pasta atual do projeto). Pasta `phases/` nasce com o primeiro arquivo. Preencher **Entrega** + **Como**, **Projeto:** `[Nome](../{slug}.md)`, **Status**, **Prazo**. Conteúdo longo fica aqui, não no hub.
2. Heading no hub em português: link para a nota, mesmo **Status** e **Prazo**, uma frase.
3. Se o Como não der para derivar tarefas sem inventar, perguntar — não criar as tarefas ainda. Depois **≥1 tarefa** ([new-task](new-task.md); compactar a fase, não inventar).
4. Recalcular o **Status** do projeto só se esta fase nascer já `em andamento`, `pausado` ou `concluído` (e o gate das anteriores estiver ok) — [status-change](status-change.md). `pendente` / `não planejado` no meio da fila não mudam a herança.

Links `[nome](caminho relativo)` — não `[[wiki]]`.

Mudança de status ou prazo **depois** de criada: [status-change](status-change.md).
