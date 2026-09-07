# AY1-03 — desenvolvimento do site

**Objetivo:** desenvolver o site estático (só frontend) com imagens e textos no repositório, usando o Cursor.  
**Status:** não iniciado  
**Projeto:** [Ana Year One](../ana-year-one.md)

## Entrega

- Site estático (só frontend) no repositório, com imagens e textos, layout e seções definidos na construção.
- Playlist: conteúdo de [AY1-02](ay1-02-playlist.md).

## Como

Cursor. Spec fina em `docs/` + schema, separada do editorial. Árvore `content/` no **repo do site** (não no vault). Detalhe: Organização e Conteúdo da página abaixo.

## Tarefas

- [Desenvolver o site estático](../../../../../tasks/pending/build-anniversary-static-site.md)

## Organização no repositório

Fonte: formato content/repo para AY1-03.

- **Spec fina** (1–3 MDs + schema) **separada** do conteúdo editorial.
- Árvore `content/` no **repo do site** (não no vault Obsidian): pasta = hierarquia ≤3 níveis; item = `index.md` + imagens colocalizadas.
- **JSON/YAML** só para config (paleta, nav, Spotify IDs) — não para prosa longa.
- Esqueleto sugerido:
  - `docs/ay1-03-spec.md`
  - `schema/content.schema.json`
  - `content/{inicio,diario,memorias,playlist}/`
  - `scripts/process-images`
  - `src/`
  - `public/media`
- **Frontmatter:**
  - Diário: `date` + `image`
  - Memórias: `title` + `date` + `images`
  - Playlist: `spotify`
  - Início: blocos em Markdown
- **Fotos** no git do site (ou Git LFS) — **não** no vault.

## Conteúdo da página

A página é um frontend com conteúdo definido na construção. Layout, seções, textos, imagens, cores e músicas são fixos: não há editor nem conteúdo genérico.

### Estrutura

A página usa um único layout. Tamanhos de fonte e posição de cada elemento são definidos por esse layout.

Há quatro seções, nesta ordem:

1. **Início**
2. **Diário**
3. **Memórias**
4. **Playlist**

**Diário**, **Memórias** e **Playlist** organizam itens. Um item pode estar na seção, numa pasta ou numa subpasta. A profundidade máxima é: seção → pasta → subpasta → item.

Pastas e itens seguem a ordem definida no conteúdo, com uma exceção: no Diário, as entradas de um mesmo recipiente aparecem por data, da mais antiga para a mais recente.

#### Início

- Nome do casal (Nicolas e Ana), um coração e um campo de texto.
- Imagem de fundo, exibida semitransparente.
- Contador opcional de dias de relacionamento (desde 05/09/2025), a partir da data de início.

#### Diário — entradas

Cada entrada tem:

- Data
- Texto
- 1 Imagem

#### Memórias — momentos

Cada momento tem:

- Título.
- Texto
- Data.
- 10 Imagens.

#### Playlist — músicas

Cada música tem:

- Link de **faixa** do Spotify (não álbum, playlist ou artista).
- Título e capa obtidos do Spotify.
- Texto dizendo porque aquela musica lembra ela.
- Player embutido do Spotify.

### Imagens

Toda imagem é recodificada, redimensionada para no máximo 2048 px no lado maior e sem metadados embutidos (por exemplo localização).

### Cores

A paleta tem três cores:

- **Primária** — títulos e elementos clicáveis.
- **Secundária** — subtítulos e elementos não clicáveis.
- **Terciária** — fundo.

Variações da terciária são geradas automaticamente para o texto atingir contraste WCAG AA (4,5:1 no texto normal, 3:1 no texto grande).
