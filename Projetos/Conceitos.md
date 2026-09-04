Este documento relaciona os **problemas concretos do Toujours** aos **conceitos centrais de engenharia** que serão utilizados para resolvê-los.

A intenção não é listar tudo o que poderia ser estudado. O objetivo é manter apenas os conceitos diretamente relevantes para a arquitetura deste produto.

---

### Controle de custos e abuso

- **Rate Limiting** — limita a quantidade de requisições que um usuário ou cliente pode fazer em determinado período.
- **Authentication** — identifica e confirma quem é o usuário.
- **Persistent Sessions** — mantém o usuário autenticado entre diferentes acessos.
- **Resource Limits** — define limites para uso de recursos, como armazenamento, uploads ou operações.
- **Data Retention** — define mecanismos e políticas para remoção de dados após determinado período.
- **Cost Tracking** — registra e acompanha o consumo de recursos e seus custos.
- **Admission Control** — decide se uma nova operação pode ser aceita com base em limites ou disponibilidade de recursos.

### Dados e persistência

- **Transactions** — agrupa operações que precisam ser executadas conjuntamente.
- **ACID** — conjunto de propriedades fornecidas pelo sistema transacional para garantir operações confiáveis.
- **Referential Integrity** — utiliza restrições para impedir relacionamentos inválidos entre dados.
- **Idempotency** — implementa operações que podem ser repetidas sem gerar efeitos duplicados.
- **Database Indexes** — estruturas criadas para acelerar consultas ao banco de dados.
- **Object Storage** — sistema de armazenamento para arquivos, como imagens.
- **Database** — sistema utilizado para armazenar e consultar os dados estruturados da aplicação.
- **Backups** — criação e armazenamento de cópias dos dados para recuperação.

### Spotify e integrações externas

- **API Integration** — implementação da comunicação da aplicação com APIs externas.
- **OAuth 2.0** — mecanismo de autorização para acessar recursos de um usuário em outro serviço.
- **Queues / Job Processing** — execução assíncrona de tarefas por meio de filas e workers.
- **State Management** — armazenamento e atualização do estado necessário para controlar operações e integrações.
- **Reconciliation** — processo automatizado de comparar estados e corrigir divergências.
- **Timeouts** — define um tempo máximo de espera para uma operação.
- **Retries** — repete automaticamente operações que falharam.
- **Exponential Backoff** — aumenta progressivamente o intervalo entre tentativas de retry.
- **Circuit Breaker** — interrompe temporariamente chamadas para uma dependência que está falhando.

### Experiência e performance

- **Caching** — armazena temporariamente dados para evitar processamento ou consultas repetidas.
- **CDN** — distribui arquivos por servidores próximos dos usuários.
- **Lazy Loading** — carrega recursos somente quando são necessários.
- **HTTP Caching** — utiliza os mecanismos de cache do HTTP para evitar requisições e transferências desnecessárias.

### Segurança

- **Authentication** — mecanismo para verificar a identidade do usuário.
- **Authorization** — mecanismo para controlar quais recursos e operações cada usuário pode acessar.
- **OAuth 2.0** — mecanismo de autorização delegada para serviços externos.
- **Least Privilege** — configura cada usuário ou componente com somente as permissões necessárias.
- **Secrets Management** — armazenamento e gerenciamento seguro de credenciais, tokens e chaves.
- **Encryption in Transit** — criptografia dos dados durante sua transmissão.
- **Input Validation** — validação dos dados recebidos antes de processá-los.

### Arquitetura

- **Modular Monolith** — estrutura uma aplicação única em módulos isolados e bem definidos.
- **Separation of Concerns** — separa responsabilidades diferentes entre componentes.
- **Dependency Inversion** — estrutura dependências através de abstrações em vez de implementações concretas.
- **API Contracts** — definição explícita das interfaces e formatos utilizados na comunicação entre componentes.
- **Architecture Decision Records** — registro das decisões arquiteturais importantes e suas justificativas.

### Operação

- **Observability** — implementação de mecanismos para coletar informações sobre o comportamento do sistema.
- **Structured Logging** — registro de eventos em formato estruturado e facilmente analisável.
- **Metrics** — coleta de métricas quantitativas sobre o sistema.
- **Error Tracking** — registro e acompanhamento de erros da aplicação.
- **Health Checks** — mecanismos que verificam o estado de componentes e dependências.
- **Cost Tracking** — registro e acompanhamento do consumo e custo dos recursos.

| Propriedade emergente       | Mecanismos que contribuem para produzi-la                                                                   |
| --------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Reliability**             | Transactions, Idempotency, Backups, Timeouts, Retries, Queues, Health Checks                                |
| **Availability**            | Timeouts, Retries, Circuit Breaker, Queues, Health Checks, Caching                                          |
| **Resilience**              | Timeouts, Retries, Exponential Backoff, Circuit Breaker, Queues                                             |
| **Fault Tolerance**         | Transactions, Idempotency, Retries, Queues, Backups, Circuit Breaker                                        |
| **Performance**             | Database Indexes, Caching, CDN, HTTP Caching, Lazy Loading                                                  |
| **Low Latency**             | Caching, CDN, Database Indexes, HTTP Caching, Lazy Loading                                                  |
| **Scalability**             | Caching, CDN, Queues, Database Indexes, Object Storage                                                      |
| **Security**                | Authentication, Authorization, Least Privilege, Secrets Management, Encryption in Transit, Input Validation |
| **Abuse Prevention**        | Authentication, Rate Limiting, Resource Limits, Admission Control                                           |
| **Durability**              | Database, Object Storage, Backups                                                                           |
| **Consistency**             | Transactions, Referential Integrity, Idempotency                                                            |
| **Operability**             | Observability, Structured Logging, Metrics, Error Tracking, Health Checks                                   |
| **Maintainability**         | Modular Monolith, Separation of Concerns, Dependency Inversion, API Contracts                               |
| **Cost Efficiency**         | Resource Limits, Admission Control, Caching, CDN, Cost Tracking                                             |
| **Data Recovery**           | Backups, Data Retention                                                                                     |
| **Integration Reliability** | Timeouts, Retries, Exponential Backoff, Circuit Breaker, Queues, Reconciliation, Idempotency                |

Architecture
│
├── Cost Control
│   │
│   ├── Abuse Prevention
│   │   ├── Rate Limiting
│   │   ├── Resource Limits
│   │   ├── Admission Control
│   │   └── Authentication
│   │
│   ├── Cost Efficiency
│   │   ├── Caching
│   │   ├── CDN
│   │   └── HTTP Caching
│   │
│   └── Cost Visibility
│       └── Cost Tracking
│
└── User Experience
    │
    ├── Low Latency
    │   ├── Caching
    │   ├── CDN
    │   ├── HTTP Caching
    │   ├── Lazy Loading
    │   └── Database Indexes
    │
    ├── Reliability
    │   ├── Transactions
    │   ├── Idempotency
    │   ├── Backups
    │   └── Reconciliation
    │
    ├── Availability
    │   ├── Timeouts
    │   ├── Retries
    │   ├── Circuit Breaker
    │   └── Queues / Job Processing
    │
    ├── Resilience
    │   ├── Timeouts
    │   ├── Retries
    │   ├── Exponential Backoff
    │   ├── Circuit Breaker
    │   └── Queues / Job Processing
    │
    └── Security
        ├── Authentication
        ├── Authorization
        ├── Least Privilege
        ├── Secrets Management
        ├── Encryption in Transit
        └── Input Validation