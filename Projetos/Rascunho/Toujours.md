## Conceito

Plataforma para criação de sites românticos personalizados.

O usuário pode criar um site, editar seu conteúdo e compartilhar uma URL pública.

A plataforma possui projetos temporários gratuitos e projetos persistentes obtidos mediante pagamento.

---

## Estrutura de URLs

A aplicação utiliza o namespace `/toujours` dentro do domínio geral `nhuche.com`.

```text
nhuche.com/toujours
    → Landing page

nhuche.com/toujours/create
    → Início da criação

nhuche.com/toujours/create/:slug
    → Editor do projeto

nhuche.com/toujours/s/:slug
    → Site público

nhuche.com/toujours/s/:slug/diario
    → Seção Diário

nhuche.com/toujours/s/:slug/momentos
    → Seção Momentos

nhuche.com/toujours/s/:slug/musicas
    → Seção Músicas
```

O `slug` identifica o site publicamente.

O estado do projeto (`TEMPORARY` ou `PERSISTENT`) não faz parte da URL.

A URL permanece a mesma caso um projeto temporário seja convertido em persistente.

---

## Conteúdo do site

Cada site possui três seções:

- **Diário**
    
- **Momentos**
    
- **Músicas**
    

A estrutura e o conteúdo de cada seção são personalizáveis pelo usuário.

O usuário deve conseguir facilmente:

- adicionar, editar e remover textos;
    
- adicionar, substituir e remover imagens;
    
- adicionar, substituir e remover músicas;
    
- adicionar e remover entradas;
    
- definir a quantidade de fotos de cada momento.
    

O sistema deve permitir que o usuário coloque suas próprias imagens, textos e músicas sem precisar modificar código-fonte.

### Diário

Cada entrada possui uma imagem associada.

### Momentos

Cada momento pode possuir uma ou mais imagens, com suporte para aproximadamente até 10 imagens por momento.

O layout deve se adaptar responsivamente à quantidade de imagens.

### Músicas

Cada música pode possuir informações e uma descrição explicando sua relação com o site/pessoa.

---

## Projetos

Existem dois estados principais:

```text
TEMPORARY
PERSISTENT
```

### Temporário

- Gratuito.
    
- Possui duração limitada.
    
- Expira após determinado período.
    
- Após a expiração, os dados e arquivos associados podem ser removidos.
    
- A expiração não restaura a elegibilidade para um novo projeto gratuito.
    

### Persistente

- Obtido mediante pagamento.
    
- Não expira.
    
- Permanece disponível para edição e visualização.
    

A conversão de `TEMPORARY` para `PERSISTENT` mantém o mesmo projeto e a mesma URL pública.

---

## Autenticação

Não haverá autenticação por senha.

A autenticação será feita através de e-mail e código de verificação (OTP).

Fluxo:

```text
E-mail
  ↓
Código de verificação
  ↓
Identidade verificada
  ↓
Sessão persistente
```

No primeiro acesso:

- se o e-mail não existir, uma identidade é criada após a verificação;
    
- se o e-mail já existir, o usuário é autenticado.
    

O usuário não precisa realizar um cadastro tradicional.

A sessão persistente mantém o usuário autenticado, mas não substitui a identidade verificada.

---

## Acesso de usuários existentes

A landing page deve oferecer:

- **Criar meu site**
    
- **Já tenho um site / Editar meu site**
    

O segundo fluxo permite que o usuário informe seu e-mail, valide o código OTP e acesse seus projetos.

Se houver apenas um projeto, o usuário pode ser direcionado diretamente ao editor.

Se houver vários projetos, o usuário poderá escolher qual editar.

---

## Limite de projetos gratuitos

Cada identidade pode possuir no máximo um projeto gratuito.

Se o usuário tentar criar outro projeto gratuito enquanto já possui um projeto gratuito ativo:

1. não deve ser criado um novo projeto;
    
2. o usuário deve ser direcionado ao editor do projeto existente;
    
3. o editor deve exibir uma mensagem informando que outro projeto requer pagamento;
    
4. o usuário pode iniciar o fluxo de pagamento para criar outro projeto.
    

Essa regra deve ser validada no backend.

---

## Prevenção de abuso

A plataforma não deve depender apenas da sessão do navegador para impedir abuso.

Medidas principais:

- identidade baseada em e-mail verificado;
    
- limite de um projeto gratuito por identidade;
    
- sessões persistentes;
    
- rate limiting;
    
- mecanismos adicionais contra automação/abuso quando necessário.
    

A expiração de um projeto não deve permitir que a mesma identidade obtenha indefinidamente novos trials gratuitos.

---

## Princípios arquiteturais

- A URL identifica o recurso; o estado do recurso não faz parte da URL.
    
- Identidade e sessão são conceitos distintos.
    
- Autenticação e autorização são responsabilidades do backend.
    
- Regras de negócio devem ser aplicadas no backend, não apenas no frontend.
    
- Um projeto temporário pode mudar de estado sem mudar de identidade ou URL.
    
- O editor e o site público são interfaces diferentes do mesmo projeto.
    
- O conteúdo deve ser facilmente editável sem alterações no código.
    
- A organização interna do código e a arquitetura específica ficam a critério da implementação.