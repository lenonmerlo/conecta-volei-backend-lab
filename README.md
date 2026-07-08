# Conecta Volei Backend Lab

Backend modular para gestao de treinos e jogos de volei com foco em:

- cadastro, autenticacao e refresh token de jogadores;
- criacao e gestao administrativa de jogos;
- inscricoes com regras de lista principal, waitlist e convidados;
- sorteio, troca e persistencia de times por jogo;
- trilha de auditoria para acoes criticas;
- mensageria com publicacao e consumo de eventos RabbitMQ;
- observabilidade com metricas Prometheus e dashboard Grafana versionado;
- pipeline CI com lint, testes, validacao de Docker Compose e build Docker.

A API foi construida com FastAPI, SQLAlchemy, Alembic, Redis, RabbitMQ e PostgreSQL, com execucao local ou via Docker Compose.

## Sumario

- [Visao Geral](#visao-geral)
- [Stack Tecnologica](#stack-tecnologica)
- [Arquitetura](#arquitetura)
- [Dominio e Regras de Negocio](#dominio-e-regras-de-negocio)
- [Funcionalidades da API](#funcionalidades-da-api)
- [Modelo de Dados](#modelo-de-dados)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Configuracao e Variaveis de Ambiente](#configuracao-e-variaveis-de-ambiente)
- [Como Rodar](#como-rodar)
- [Migracoes de Banco](#migracoes-de-banco)
- [Observabilidade](#observabilidade)
- [Testes](#testes)
- [Seed de Dados de Demonstracao](#seed-de-dados-de-demonstracao)
- [Exemplos de API](#exemplos-de-api)
- [Versionamento](#versionamento)
- [Limitacoes Atuais e Proximos Passos](#limitacoes-atuais-e-proximos-passos)

## Visao Geral

O projeto segue uma arquitetura modular por dominio. Cada modulo encapsula modelo, schemas, repositorio e servico, reduzindo acoplamento e facilitando evolucao.

Principais capacidades implementadas:

- autenticacao por WhatsApp com access token e refresh token JWT;
- RBAC por papel (`player`, `admin`, `super_admin`);
- gerenciamento de jogadores com warnings e mudanca automatica de status;
- gerenciamento administrativo de jogos com validacao de dia permitido;
- inscricoes em jogos com lista principal, waitlist, convidados e promocao automatica;
- tratamento especial de convidados em janela especifica;
- sorteio automatico de times com balanceamento por nivel, capitaes, levantadores, posicao e genero;
- troca manual de jogadores entre times sorteados;
- persistencia de times confirmados por jogo;
- trilha de auditoria para acoes criticas;
- cache Redis para listagem de jogos;
- publicacao e consumo de eventos de inscricao via RabbitMQ;
- metricas HTTP para Prometheus;
- dashboard Grafana versionado para observabilidade da API;
- pipeline CI com Ruff, Pytest, Docker Compose config e Docker build.

Prefixo base da API: `/api/v1`

Documentacao interativa (FastAPI):

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Stack Tecnologica

- Linguagem: Python 3.12+
- API: FastAPI
- Servidor ASGI: Uvicorn
- ORM: SQLAlchemy 2.x
- Migracoes: Alembic
- Banco relacional: PostgreSQL
- Cache: Redis
- Mensageria: RabbitMQ (fila `registration_events`)
- Observabilidade: Prometheus Client + Prometheus + Grafana
- Testes: Pytest + HTTPX
- Qualidade: Ruff
- Containerizacao: Docker + Docker Compose
- CI: GitHub Actions

## Arquitetura

### Diagrama de camadas (modular + infraestrutura)

```mermaid
flowchart TD
  Client[Cliente HTTP] --> Router[FastAPI Routers /api/v1]

  subgraph APP[Aplicacao]
    Router --> Auth[Auth Guard JWT + RBAC]
    Router --> Service[Services por modulo]
    Service --> Domain[Domain Rules]
    Service --> Repo[Repositories]
    Repo --> Model[SQLAlchemy Models]
  end

  subgraph DATA[Dados e Integracoes]
    Model --> PG[(PostgreSQL)]
    Service --> Redis[(Redis Cache)]
    Service --> Rabbit[(RabbitMQ Events)]
    Worker[Registration Event Consumer] --> Rabbit
  end

  subgraph OBS[Observabilidade]
    Router --> Metrics[Metrics Middleware]
    Metrics --> Endpoint[/GET /metrics/]
    Endpoint --> Prom[(Prometheus)]
    Prom --> Graf[(Grafana Dashboard)]
  end

  Router -.audita acoes.-> Audit[Audit Logs Service]
  Audit --> AuditRepo[AuditLog Repository]
  AuditRepo --> PG
```

### Fluxo de requisicao (exemplo: inscricao em jogo)

```mermaid
sequenceDiagram
  autonumber
  participant U as Cliente
  participant API as FastAPI Router
  participant SVC as Registration Service
  participant PREPO as Player Repository
  participant GREPO as Game Repository
  participant RREPO as Registration Repository
  participant DB as PostgreSQL
  participant MQ as RabbitMQ
  participant AUD as Audit Service
  participant WK as Consumer Worker

  U->>API: POST /api/v1/registrations/join
  API->>SVC: join_game(payload)
  SVC->>GREPO: get(game_id)
  GREPO->>DB: SELECT game
  DB-->>GREPO: game
  GREPO-->>SVC: game
  SVC->>PREPO: get(player_id)
  PREPO->>DB: SELECT player
  DB-->>PREPO: player
  PREPO-->>SVC: player
  SVC->>RREPO: create(registration)
  RREPO->>DB: INSERT registration
  DB-->>RREPO: ok
  RREPO-->>SVC: registration
  SVC->>MQ: publish registration.joined
  API->>AUD: create audit log
  AUD->>DB: INSERT audit_logs
  MQ-->>WK: consume registration event
  SVC-->>API: RegistrationRead
  API-->>U: 201 Created
```

Autenticacao e RBAC sao aplicados nas rotas protegidas, como criacao/edicao/remocao de jogos, warnings, processamento de convidados, persistencia de times e consulta de audit logs.

### Responsabilidades por pacote

- `app/api`: camada HTTP (roteamento, validacao de entrada/saida, codigos de resposta).
- `app/modules/*/service.py`: regras de aplicacao e orquestracao de casos de uso.
- `app/modules/*/repository.py`: acesso a dados e queries.
- `app/modules/*/model.py`: entidades ORM.
- `app/modules/*/schemas.py`: contratos Pydantic.
- `app/domain`: regras de dominio puras (constantes, regras de jogo, regras de jogador, sorteio de times).
- `app/core`: infraestrutura transversal (configuracao, banco, cache, seguranca JWT, mensageria, metricas, handlers de erro).
- `scripts`: rotinas operacionais, seed e workers locais.

## Dominio e Regras de Negocio

### Jogadores

- Status calculado por warnings:
  - 0-1 warning: `active`
  - 2 warnings: `penalized`
  - 3+ warnings: `blocked`
- Jogador `blocked` nao pode se inscrever em jogos.
- Jogador `blocked` nao pode autenticar ou renovar token.
- Papeis disponiveis:
  - `player`
  - `admin`
  - `super_admin`

### Jogos

- Um jogo so pode ser criado para:
  - quarta-feira (`wednesday`)
  - domingo (`sunday`)
- O ID do jogo e deterministico: `{day}-{yyyy-mm-dd}`
  - exemplo: `sunday-2026-07-05`
- Criacao, edicao e remocao de jogos exigem permissao administrativa.
- A listagem de jogos usa cache Redis e invalida o cache em mudancas.

### Inscricoes

- Capacidade da lista principal: 21 jogadores.
- Regras de slot:
  - jogador `penalized` entra direto em `waitlist`;
  - se houver vaga, entra em `main`;
  - sem vaga, entra em `waitlist`.
- Ao sair um jogador da lista principal, o primeiro da waitlist e promovido automaticamente.
- Convidados (`guest`) com `invited_by` durante janela de quinta/sexta entram em `guests` e podem ser processados depois via endpoint administrativo.
- Inscricoes publicam eventos na fila RabbitMQ `registration_events`.
- O worker `scripts/consume_registration_events.py` consome e confirma eventos processados.

### Times

- O sorteio considera jogadores da lista principal.
- Menos de 8 jogadores retorna lista vazia.
- A partir de 8 jogadores sao gerados 2 times.
- A partir de 14 jogadores sao gerados 3 times.
- O algoritmo considera:
  - nivel tecnico;
  - capitaes;
  - levantadores;
  - posicao;
  - distribuicao de jogadoras.
- A API permite trocar jogadores entre times ja sorteados.
- Times confirmados podem ser salvos por jogo.
- Ao salvar novos times para um jogo, os times anteriores daquele jogo sao substituidos.

## Funcionalidades da API

Autenticacao exigida usa `Authorization: Bearer <token>`.

| Metodo | Rota                                               | Descricao                                  | Auth  |
| ------ | -------------------------------------------------- | ------------------------------------------ | ----- |
| GET    | `/api/v1/health`                                   | Health check simples                       | Nao   |
| GET    | `/api/v1/ready`                                    | Readiness check (DB + cache)               | Nao   |
| POST   | `/api/v1/auth/login`                               | Login por WhatsApp e emissao de tokens     | Nao   |
| POST   | `/api/v1/auth/refresh`                             | Renova access/refresh token                | Nao   |
| GET    | `/api/v1/auth/me`                                  | Retorna jogador autenticado                | Sim   |
| GET    | `/api/v1/players`                                  | Lista jogadores                            | Nao   |
| GET    | `/api/v1/players/{player_id}`                      | Busca jogador por ID                       | Nao   |
| POST   | `/api/v1/players`                                  | Cria jogador                               | Nao   |
| PATCH  | `/api/v1/players/{player_id}`                      | Atualiza jogador                           | Nao   |
| DELETE | `/api/v1/players/{player_id}`                      | Remove jogador                             | Admin |
| POST   | `/api/v1/players/{player_id}/warnings`             | Adiciona warning                           | Admin |
| DELETE | `/api/v1/players/{player_id}/warnings`             | Remove warning                             | Admin |
| POST   | `/api/v1/players/{player_id}/warnings/reset`       | Zera warnings                              | Admin |
| GET    | `/api/v1/games`                                    | Lista jogos (com cache)                    | Nao   |
| GET    | `/api/v1/games/{game_id}`                          | Busca jogo por ID                          | Nao   |
| POST   | `/api/v1/games`                                    | Cria jogo                                  | Admin |
| PATCH  | `/api/v1/games/{game_id}`                          | Atualiza jogo                              | Admin |
| DELETE | `/api/v1/games/{game_id}`                          | Remove jogo                                | Admin |
| GET    | `/api/v1/games/{game_id}/teams`                    | Lista times salvos do jogo                 | Nao   |
| PUT    | `/api/v1/games/{game_id}/teams`                    | Substitui times salvos do jogo             | Admin |
| GET    | `/api/v1/registrations?game_id=...`                | Lista inscricoes por jogo                  | Nao   |
| POST   | `/api/v1/registrations/join`                       | Inscreve jogador no jogo                   | Nao   |
| POST   | `/api/v1/registrations/leave`                      | Remove inscricao do jogo                   | Nao   |
| POST   | `/api/v1/registrations/process-guests?game_id=...` | Processa fila de convidados                | Admin |
| GET    | `/api/v1/audit-logs`                               | Lista logs de auditoria                    | Admin |
| GET    | `/api/v1/teams`                                    | Lista times (placeholder compativel)       | Nao   |
| POST   | `/api/v1/teams/draw`                               | Sorteia times a partir de jogadores        | Admin |
| POST   | `/api/v1/teams/swap`                               | Troca jogadores entre times sorteados      | Admin |
| GET    | `/metrics`                                         | Metricas Prometheus                        | Nao   |

## Modelo de Dados

```mermaid
erDiagram
    PLAYERS ||--o{ GAME_REGISTRATIONS : registers
    GAMES ||--o{ GAME_REGISTRATIONS : has
    GAMES ||--o{ GAME_TEAMS : has
    PLAYERS ||--o{ AUDIT_LOGS : actor
    PLAYERS ||--o{ AUDIT_LOGS : target
    GAMES ||--o{ AUDIT_LOGS : context

    PLAYERS {
      string id PK
      string name
      string whatsapp UK
      string gender
      string type
      string role
      string status
      int warnings
      string avatar_url
      float skill_level
      bool is_captain
      bool is_setter
      string position
    }

    GAMES {
      string id PK
      string day
      date date
      string location
      time time
      string status
      string notes
    }

    GAME_REGISTRATIONS {
      string id PK
      string game_id FK
      string player_id FK
      string invited_by FK
      string slot
      datetime registered_at
    }

    GAME_TEAMS {
      string id PK
      string game_id FK
      string team_name
      json players
      float total_level
      datetime created_at
    }

    AUDIT_LOGS {
      string id PK
      string actor_player_id FK
      string target_player_id FK
      string game_id FK
      string action
      json details
      datetime created_at
    }
```

## Estrutura de Pastas

```text
app/
  api/
    router.py
    v1/
      audit_logs.py
      auth.py
      games.py
      players.py
      registrations.py
      system.py
      teams.py
  core/
    cache.py
    config.py
    database.py
    errors.py
    messaging.py
    metrics.py
    security.py
  domain/
    constants.py
    game_rules.py
    player_rules.py
    team_draw.py
  modules/
    audit_logs/
    auth/
    game_teams/
    games/
    players/
    registrations/
    teams/

docs/
  api-examples.md

observability/
  prometheus.yml
  grafana/
    dashboards/
    provisioning/

scripts/
  consume_registration_events.py
  seed_demo.py
  start_api.sh

tests/
alembic/
```

## Configuracao e Variaveis de Ambiente

Use `.env` (ha um template em `.env.example`).

Variaveis principais:

- `APP_NAME`: nome da aplicacao.
- `ENVIRONMENT`: ambiente (`local`, `test`, etc.).
- `DEBUG`: habilita modo debug.
- `DATABASE_URL`: URL SQLAlchemy para PostgreSQL.
- `TEST_DATABASE_URL`: banco isolado para suite de testes.
- `REDIS_URL`: URL do Redis.
- `RABBITMQ_URL`: URL AMQP do RabbitMQ.
- `JWT_SECRET_KEY`: segredo para assinatura do token JWT.
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: expiracao do access token em minutos.
- `JWT_REFRESH_TOKEN_EXPIRE_MINUTES`: expiracao do refresh token em minutos.

## Como Rodar

### 1) Rodando local (sem Docker para API)

Pre-requisitos:

- Python 3.12+
- PostgreSQL
- Redis
- RabbitMQ

Passos (Linux/macOS):

```bash
cp .env.example .env
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Passos (Windows PowerShell):

```powershell
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API disponivel em: `http://localhost:8000`

### 2) Rodando com Docker Compose (stack completa)

```bash
docker compose up --build
```

Fluxo mais usado no projeto (subindo a API em background):

```bash
docker compose up -d --build api
```

Esse comando sobe a API e os servicos dependentes definidos no Compose.

Servicos expostos:

- API: `http://localhost:8000`
- PostgreSQL: `localhost:5433`
- Redis: `localhost:6379`
- RabbitMQ AMQP: `localhost:5672`
- RabbitMQ Management: `http://localhost:15672`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

Observacao: o container da API executa `alembic upgrade head` automaticamente no startup.

### 3) Consumindo eventos RabbitMQ

Com RabbitMQ rodando, o worker local pode ser iniciado com:

```powershell
$env:RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
.\.venv\Scripts\python.exe scripts\consume_registration_events.py
```

O worker consome eventos da fila `registration_events`, registra o processamento e confirma mensagens validas com `ack`.

## Migracoes de Banco

Historico atual de migrations Alembic:

- `4ab5bc9c79da`: cria tabela `players`.
- `49d804a86c37`: cria tabela `games`.
- `d545fcee814f`: cria tabela `game_registrations`.
- `a1f2b3c4d5e6`: adiciona coluna `role` em `players`.
- `b2c3d4e5f6a7`: cria tabela `audit_logs`.
- `c3d4e5f6a7b8`: cria tabela `game_teams`.

Comandos uteis:

```bash
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "descricao da mudanca"
```

## Observabilidade

- Endpoint de metricas: `GET /metrics`
- Metricas instrumentadas:
  - `http_request_total`
  - `http_request_duration_seconds`
- `observability/prometheus.yml` contem scrape da API.
- Grafana sobe com datasource Prometheus provisionado.
- Dashboard versionado: `Conecta Volei API`.
- Caminho do dashboard no container: `/etc/grafana/dashboards`.

## Testes

Rodar suite completa:

```bash
pytest -q
```

No Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

Cobertura funcional existente inclui:

- health e readiness;
- autenticacao, refresh token e endpoint `/auth/me`;
- CRUD de players/games com rotas administrativas protegidas;
- regras de warning/status;
- fluxo de inscricoes (main/waitlist/guests);
- publicacao e consumo de eventos RabbitMQ;
- auditoria de eventos;
- sorteio, troca e persistencia de times por jogo;
- cache Redis para listagem de jogos;
- configuracoes de Dockerfile, Compose, Prometheus, Grafana e CI.

O pipeline CI executa:

- Ruff;
- Pytest;
- Alembic upgrade em banco de teste;
- validacao de `docker compose config`;
- build da imagem Docker.

## Seed de Dados de Demonstracao

Para popular dados de exemplo:

```bash
python -m scripts.seed_demo
```

No Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts\seed_demo.py
```

O seed cria:

- jogo de domingo de demonstracao;
- 21 membros na lista principal;
- 1 jogador em waitlist;
- 1 convidado em `guests`;
- 1 jogador penalizado;
- 1 jogador bloqueado.

## Exemplos de API

Exemplos praticos de uso da API estao em [`docs/api-examples.md`](./docs/api-examples.md).

O arquivo inclui fluxos para:

- health/readiness;
- login, refresh token e `/auth/me`;
- players, games e registrations;
- warnings;
- sorteio, troca e persistencia de times;
- audit logs;
- metricas e observabilidade.

## Versionamento

A versao atual do projeto e `0.1.0`.

O projeto segue Conventional Commits para manter o historico claro e facilitar evolucao futura:

- `feat`: novas funcionalidades.
- `fix`: correcoes.
- `docs`: documentacao.
- `test`: testes.
- `ci`: integracao continua.
- `chore`: manutencao.
- `refactor`: refatoracoes sem mudanca de comportamento.

Mudancas relevantes sao documentadas em [`CHANGELOG.md`](./CHANGELOG.md).

## Limitacoes Atuais e Proximos Passos

Este projeto e um backend lab em evolucao. O foco atual e demonstrar arquitetura modular, regras de negocio testadas, integracoes de infraestrutura e uma API proxima de um cenario real de produto.

- O modulo de times ja cobre sorteio, troca e persistencia, mas pode evoluir para historico/versionamento de sorteios por jogo.
- A autenticacao JWT ja possui access token e refresh token, mas pode evoluir para logout com revogacao de tokens.
- O worker RabbitMQ consome eventos de inscricao, mas ainda pode evoluir para processamento assincrono com efeitos de negocio adicionais.
- O pipeline CI valida lint, testes e build Docker, mas pode evoluir para publicacao de imagem e deploy automatizado.
- Dashboards Grafana estao versionados, mas podem evoluir com paineis de negocio, alertas e SLOs.

---
