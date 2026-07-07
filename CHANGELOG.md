# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato segue uma adaptação de [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e o versionamento segue [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-07-07

### Adicionado

- API modular com FastAPI, SQLAlchemy e Alembic.
- Configuração local com PostgreSQL, Redis, RabbitMQ, Prometheus e Grafana via Docker Compose.
- Health check e readiness check com validação de banco e cache.
- CRUD de jogadores com status, tipo, papel, nível técnico, capitão, levantador e posição.
- Autenticação via JWT com access token e refresh token.
- RBAC com papéis `player`, `admin` e `super_admin`.
- Gestão de jogos com cache Redis para listagem.
- Proteção administrativa para rotas críticas de jogos, warnings, convidados, times e auditoria.
- Inscrições em jogos com lista principal, waitlist, convidados e promoção automática.
- Regras de warnings com penalização e bloqueio automático.
- Publicação e consumo de eventos de inscrição via RabbitMQ.
- Trilhas de auditoria para ações críticas.
- Sorteio automático de times com balanceamento por nível, capitães, levantadores, posição e gênero.
- Troca manual de jogadores entre times sorteados.
- Persistência de times confirmados por jogo.
- Métricas Prometheus para requisições HTTP e duração.
- Dashboard Grafana versionado para observabilidade da API.
- Seed de dados de demonstração.
- Pipeline CI com Ruff, Pytest, validação de Docker Compose e build Docker.
- README completo com arquitetura, regras de negócio, execução local, Docker e observabilidade.

### Observações

- Este é um backend lab orientado a portfólio, com foco em demonstrar arquitetura modular, regras de negócio, testes e integração com infraestrutura.