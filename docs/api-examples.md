# API Examples

Exemplos práticos para testar os principais fluxos da API localmente.

Base URL:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## Health e Readiness

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/ready
```

## Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"whatsapp":"27991112222"}'
```

Resposta esperada:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "player": {
    "id": "...",
    "name": "Nao Apagar Docker",
    "whatsapp": "27991112222",
    "role": "admin",
    "status": "active"
  }
}
```

## Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

## Usuário Atual

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## Criar Jogador

```bash
curl -X POST http://localhost:8000/api/v1/players \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Player Example",
    "nickname": "Example",
    "whatsapp": "27990000001",
    "gender": "M",
    "type": "member"
  }'
```

## Ativar Jogador

```bash
curl -X PATCH http://localhost:8000/api/v1/players/<player_id> \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}'
```

## Criar Jogo

Requer admin.

```bash
curl -X POST http://localhost:8000/api/v1/games \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-07-12",
    "location": "Arena Conecta",
    "time": "08:00:00"
  }'
```

## Entrar no Jogo

```bash
curl -X POST http://localhost:8000/api/v1/registrations/join \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "sunday-2026-07-12",
    "player_id": "<player_id>",
    "invited_by": null
  }'
```

## Sair do Jogo

```bash
curl -X POST http://localhost:8000/api/v1/registrations/leave \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "sunday-2026-07-12",
    "player_id": "<player_id>"
  }'
```

## Adicionar Warning

Requer admin.

```bash
curl -X POST http://localhost:8000/api/v1/players/<player_id>/warnings \
  -H "Authorization: Bearer <access_token>"
```

## Processar Convidados

Requer admin.

```bash
curl -X POST "http://localhost:8000/api/v1/registrations/process-guests?game_id=sunday-2026-07-12" \
  -H "Authorization: Bearer <access_token>"
```

## Sortear Times

Requer admin.

```bash
curl -X POST http://localhost:8000/api/v1/teams/draw \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "players": [
      {
        "id": "p-1",
        "name": "Player 1",
        "skill_level": 5,
        "gender": "M",
        "is_captain": true,
        "is_setter": false,
        "position": "attacker"
      },
      {
        "id": "p-2",
        "name": "Player 2",
        "skill_level": 3,
        "gender": "F",
        "is_captain": false,
        "is_setter": true,
        "position": "setter"
      },
      {
        "id": "p-3",
        "name": "Player 3",
        "skill_level": 4,
        "gender": "M",
        "is_captain": false,
        "is_setter": false,
        "position": "middle"
      },
      {
        "id": "p-4",
        "name": "Player 4",
        "skill_level": 4,
        "gender": "F",
        "is_captain": false,
        "is_setter": false,
        "position": "all-around"
      },
      {
        "id": "p-5",
        "name": "Player 5",
        "skill_level": 2,
        "gender": "M",
        "is_captain": false,
        "is_setter": false,
        "position": "middle"
      },
      {
        "id": "p-6",
        "name": "Player 6",
        "skill_level": 3,
        "gender": "M",
        "is_captain": false,
        "is_setter": false,
        "position": "attacker"
      },
      {
        "id": "p-7",
        "name": "Player 7",
        "skill_level": 5,
        "gender": "F",
        "is_captain": false,
        "is_setter": false,
        "position": "all-around"
      },
      {
        "id": "p-8",
        "name": "Player 8",
        "skill_level": 4,
        "gender": "M",
        "is_captain": false,
        "is_setter": true,
        "position": "setter"
      }
    ]
  }'
```

## Trocar Jogadores Entre Times

Requer admin.

```bash
curl -X POST http://localhost:8000/api/v1/teams/swap \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "teams": [
      {
        "name": "Time A",
        "players": [
          {
            "id": "p-1",
            "name": "Player 1",
            "skill_level": 5,
            "gender": "M",
            "is_captain": true,
            "is_setter": false,
            "position": "attacker"
          }
        ]
      },
      {
        "name": "Time B",
        "players": [
          {
            "id": "p-2",
            "name": "Player 2",
            "skill_level": 3,
            "gender": "F",
            "is_captain": false,
            "is_setter": true,
            "position": "setter"
          }
        ]
      }
    ],
    "from_team_index": 0,
    "from_player_id": "p-1",
    "to_team_index": 1,
    "to_player_id": "p-2"
  }'
```

## Salvar Times do Jogo

Requer admin.

```bash
curl -X PUT http://localhost:8000/api/v1/games/sunday-2026-07-12/teams \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "teams": [
      {
        "name": "Time A",
        "players": [
          {
            "id": "p-1",
            "name": "Player 1",
            "skill_level": 5,
            "gender": "M",
            "is_captain": true,
            "is_setter": false,
            "position": "attacker"
          }
        ],
        "total_level": 5
      }
    ]
  }'
```

## Listar Times Salvos

```bash
curl http://localhost:8000/api/v1/games/sunday-2026-07-12/teams
```

## Audit Logs

Requer admin.

```bash
curl http://localhost:8000/api/v1/audit-logs \
  -H "Authorization: Bearer <access_token>"
```

## Métricas

```bash
curl http://localhost:8000/metrics
```

## Observabilidade

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- Dashboard: `Conecta Volei API`
