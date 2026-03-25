# Proposal: Redução de Topologia de Containers (v1)

## Por Quê

A topologia inicial de 8 containers (`db`, `redis`, `minio`, `typesense`, `otel-collector`, `api`, `matching`, `web`) introduz complexidade operacional e overhead de hardware excessivos para o lançamento da **v1**. 

Identificamos redundâncias funcionais significativas:
- **Typesense**: Pode ser substituído pelo PostgreSQL FTS + PostGIS já presentes.
- **MinIO**: Pode ser substituído por filesystem local servido pela API para desenvolvimento/v1.
- **Matching**: Pode ser internalizado como módulo Python na `api`, eliminando comunicação HTTP inter-container e um segundo runtime Python.
- **Otel-Collector**: Sem backend de visualização, apenas polui o tráfego local.

## O Que Muda

- **[MODIFICADO]** `api` — Absorve as funções de matching engine (módulo interno) e orquestração de workers (in-process).
- **[MODIFICADO]** `db` — Assume responsabilidade total pela busca full-text e geo-search (via extensões nativas).
- **[DELETADO]** `typesense` — Removido da stack; busca processada no banco principal.
- **[DELETADO]** `matching` — Removido como microserviço isolado; código mergeado na `api`.
- **[DELETADO]** `minio` — Removido; storage migra para bind mount local em `/app/uploads`.
- **[DELETADO]** `otel-collector` — Removido; monitoramento via logs estruturados do uvicorn.

## Capacidades

### Novas Capacidades
- _(nenhuma)_

### Capacidades Modificadas
- `docker-topology` — Redução drástica de 8 para 4 containers; simplificação das redes Docker (remove rede `backend`).
- `search-discovery` — Lógica de busca migrada de Typesense para PostgreSQL (FTS + PostGIS).
- `matching-engine` — Interface de chamada migrada de REST para função Python interna.
- `service-request` — Storage de imagens migrado de S3/MinIO para local filesystem (StaticFiles).

## Impacto

- **Stack**: Unificação real em Python (FastAPI) no backend, eliminando a rede `backend` e o overhead de 4 containers de infra.
- **Infra**: Docker Compose consolidado em `db`, `redis`, `api` e `web`.
- **Performance**: Latência de matching reduzida (elimina o roundtrip HTTP entre containers).
- **Manutenibilidade**: Redução de pontos de falha (sincronização de índices, conexões S3 falhas em dev).

## Non-Goals

- Eliminar o Redis (mantido para pub/sub e cache).
- Eliminar o suporte nativo a S3 em produção (o código deve usar abstração de storage).
- Reduzir a fidelidade da busca (FTS + PostGIS cobrem 100% dos casos de v1).
